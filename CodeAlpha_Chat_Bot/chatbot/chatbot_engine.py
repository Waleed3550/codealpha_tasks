import logging
from sklearn.feature_extraction.text import TfidfVectorizer

logger = logging.getLogger(__name__)

from sklearn.metrics.pairwise import cosine_similarity
from .preprocessing import preprocess_text
from .models import FAQ

class ChatbotEngine:
    _instance = None
    
    def __new__(cls):
        # Singleton pattern to ensure the vectorizer is loaded only once
        if cls._instance is None:
            cls._instance = super(ChatbotEngine, cls).__new__(cls)
            cls._instance.vectorizer = TfidfVectorizer()
            cls._instance.faq_list = []
            cls._instance.tfidf_matrix = None
            cls._instance.is_trained = False
        return cls._instance

    def train(self):
        """
        Loads FAQs from the database, preprocesses them, and fits the TF-IDF vectorizer.
        Optimized to train only if not already trained, or can be forced to retrain.
        """
        if self.is_trained:
            return

        self.faq_list = list(FAQ.objects.all())
        if not self.faq_list:
            # Auto-populate 30 sample FAQs if the database is empty (Step 9)
            try:
                from django.core.management import call_command
                logger.info("Database is empty. Auto-seeding 30 sample FAQs...")
                call_command('load_faqs')
                self.faq_list = list(FAQ.objects.all())
            except Exception as e:
                logger.error(f"Failed to auto-seed database: {e}")
                
            if not self.faq_list:
                self.tfidf_matrix = None
                return
        
        raw_questions = [faq.question for faq in self.faq_list]
        questions_preprocessed = [preprocess_text(q) for q in raw_questions]
        
        # Fit and transform the questions
        try:
            self.tfidf_matrix = self.vectorizer.fit_transform(questions_preprocessed)
        except ValueError:
            # Raised if all questions are empty after preprocessing (e.g., only stop words)
            self.tfidf_matrix = None
            
        self.is_trained = True
        
    def force_retrain(self):
        self.is_trained = False
        self.train()

    def get_response(self, user_input):
        """
        Given a user input, finds the most similar FAQ and returns (answer, confidence_score).
        """
        if self.tfidf_matrix is None or not self.faq_list:
            return "No FAQs are available in the database.", 0.0

        processed_input = preprocess_text(user_input)
        
        # If user input becomes empty after preprocessing (e.g. only stopwords)
        if not processed_input.strip():
            return "Sorry, I couldn't find a relevant answer.", 0.0
            
        input_vector = self.vectorizer.transform([processed_input])
        
        try:
            # Calculate cosine similarity
            similarities = cosine_similarity(input_vector, self.tfidf_matrix)
            
            # Get the indices of the highest similarity, sorted descending
            best_indices = similarities[0].argsort()[::-1]
            best_score = float(similarities[0, best_indices[0]])
            
            logger.info(f"TF-IDF Similarity Score: {best_score:.4f}, Confidence: {best_score * 100:.2f}%")

            # Threshold for matching
            if best_score >= 0.40:
                selected_faq = self.faq_list[best_indices[0]]
                logger.info(f"Matched FAQ: '{selected_faq.question}'")
                return selected_faq.answer, best_score
            else:
                logger.info("Matched FAQ: None (Score below threshold)")
                response_text = "I couldn't find an exact answer.\n\nDid you mean one of these?\n"
                
                # Top 3 matches
                top_3 = []
                for idx in best_indices[:3]:
                    score = similarities[0, idx]
                    if score > 0.0:  # Only suggest if there is SOME similarity
                        top_3.append((self.faq_list[idx].question, score))
                
                if top_3:
                    for idx, (question, score) in enumerate(top_3):
                        response_text += f"{idx+1}. {question} (Confidence: {score * 100:.1f}%)\n"
                else:
                    response_text += "No related FAQs found."
                    
                return response_text, best_score
        except Exception as e:
            logger.error(f"TF-IDF or Cosine Similarity Error: {str(e)}")
            return "Sorry, I encountered an internal NLP error while processing your request.", 0.0

# Global instance
engine = ChatbotEngine()
