# FAQ Chatbot

An AI-powered Django chatbot that uses Natural Language Processing (via `nltk`) and TF-IDF with Cosine Similarity (via `scikit-learn`) to intelligently match user queries with an offline database of Frequently Asked Questions.

## Features
- **Offline NLP Engine**: Operates completely offline without relying on OpenAI, Gemini, or Claude.
- **Intelligent Matching**: Tokenizes, lemmatizes, removes stop-words, and calculates cosine similarity thresholds to fetch the most accurate answers.
- **Modern User Interface**: A responsive, professional blue-and-white themed chat interface with dynamic typing animations, chat bubbles, and auto-scrolling.
- **CSRF Protected**: Secure API endpoints interacting seamlessly with the Fetch API.
- **Auto-seeded Database**: A custom Django management command to load 30 default questions instantly.

## Folder Structure
```text
faq_chatbot/
│
├── chatbot/                   # Main Django App
│   ├── management/commands/   # Custom management scripts (load_faqs.py, setup_nltk.py)
│   ├── models.py              # FAQ database model
│   ├── views.py               # API endpoints
│   ├── preprocessing.py       # NLTK text processing pipeline
│   ├── chatbot_engine.py      # TF-IDF Vectorizer and Cosine Similarity logic
│   └── urls.py                # App routing
│
├── faq_chatbot/               # Django Project configuration
│   ├── settings.py            # Global settings
│   └── urls.py                # Global routing
│
├── static/                    # Frontend assets
│   ├── css/style.css          # Modern UI styles
│   └── js/script.js           # Fetch API and DOM manipulation
│
├── templates/chatbot/         # HTML structure
│   └── index.html             # Responsive chat UI
│
├── requirements.txt           # Python dependencies
└── manage.py                  # Django CLI
```

## Installation & Setup

### 1. Virtual Environment Setup
Open your terminal and create an isolated Python environment:
```bash
python -m venv venv
```
Activate it:
- **Windows**: `.\venv\Scripts\activate`
- **Mac/Linux**: `source venv/bin/activate`

### 2. Install Dependencies
Install all required packages (Django, NLTK, Scikit-learn):
```bash
pip install -r requirements.txt
```

### 3. Setup NLTK Resources
Download the required offline NLTK resources for tokenization and lemmatization:
```bash
python manage.py setup_nltk
```

### 4. Database Migration
Apply the migrations to create the database schema:
```bash
python manage.py makemigrations chatbot
python manage.py migrate
```

### 5. Load FAQs
Automatically populate the SQLite database with 30 pre-configured FAQs:
```bash
python manage.py load_faqs
```

### 6. Run the Server
Start the Django development server:
```bash
python manage.py runserver
```

Navigate to **http://127.0.0.1:8000/** in your web browser to interact with the chatbot!

## Example Questions & Expected Outputs
You can ask variations of these questions:
- *Q: What is Django?*
  **Output**: "Django is a high-level Python web framework that encourages rapid development..."
- *Q: How do I filter a queryset?*
  **Output**: "You can use the filter() method on a manager, e.g., Model.objects.filter(field=value)."
- *Q: How do I cook pasta?*
  **Output**: "Sorry, I couldn't find a relevant answer." *(Because similarity score is < 0.40)*
