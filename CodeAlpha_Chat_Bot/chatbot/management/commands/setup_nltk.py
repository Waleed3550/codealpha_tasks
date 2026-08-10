from django.core.management.base import BaseCommand
import nltk

class Command(BaseCommand):
    help = 'Downloads required NLTK resources for the chatbot'

    def handle(self, *args, **kwargs):
        resources = ['punkt', 'punkt_tab', 'stopwords', 'wordnet', 'omw-1.4']
        
        self.stdout.write("Starting download of NLTK resources...")
        
        for resource in resources:
            self.stdout.write(f"Downloading {resource}...")
            nltk.download(resource, quiet=True)
            
        self.stdout.write(self.style.SUCCESS("Successfully downloaded all required NLTK resources!"))
