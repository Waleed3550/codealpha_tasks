from django.core.management.base import BaseCommand
from chatbot.models import FAQ
from chatbot.chatbot_engine import engine

class Command(BaseCommand):
    help = 'Load 30 sample FAQs into the database'

    def handle(self, *args, **kwargs):
        faqs = [
            ("What is AI?", "AI, or Artificial Intelligence, is the simulation of human intelligence processes by machines, especially computer systems. These processes include learning, reasoning, and self-correction."),
            ("What is Machine Learning?", "Machine Learning is a subset of AI that provides systems the ability to automatically learn and improve from experience without being explicitly programmed."),
            ("What is Deep Learning?", "Deep Learning is a subset of machine learning based on artificial neural networks with representation learning. It involves multiple layers to progressively extract higher-level features from raw input."),
            ("What is Natural Language Processing?", "Natural Language Processing (NLP) is a branch of AI that helps computers understand, interpret and manipulate human language."),
            ("What is Python?", "Python is a high-level, interpreted programming language known for its simplicity and readability, widely used in Data Science, AI, and web development."),
            ("What is Computer Science?", "Computer Science is the study of computation, automation, and information, spanning theoretical disciplines to practical software and hardware engineering."),
            ("What is Data Science?", "Data Science is an interdisciplinary field that uses scientific methods, processes, algorithms and systems to extract knowledge and insights from noisy, structured and unstructured data."),
            ("What is Django?", "Django is a high-level Python web framework that encourages rapid development and clean, pragmatic design."),
            ("How do I install Django?", "You can install Django using pip: pip install django"),
            ("What is a model in Django?", "A model is the single, definitive source of truth about your data. It contains the essential fields and behaviors of the data you’re storing."),
            ("What is a view in Django?", "A view function, or view for short, is a Python function that takes a Web request and returns a Web response."),
            ("How does Django handle templates?", "Django provides a built-in template engine that allows you to define HTML with placeholders and logic to dynamically generate pages."),
            ("What is the Django admin site?", "The admin site is a built-in interface for authorized users to manage the contents of the database."),
            ("How do I create a superuser?", "Run the command: python manage.py createsuperuser"),
            ("What is a queryset?", "A QuerySet represents a collection of objects from your database. It can have zero, one or many filters."),
            ("How do I filter a queryset?", "You can use the filter() method on a manager, e.g., Model.objects.filter(field=value)."),
            ("What is a migration in Django?", "Migrations are Django’s way of propagating changes you make to your models into your database schema."),
            ("How do I create a migration?", "Run the command: python manage.py makemigrations"),
            ("How do I apply migrations?", "Run the command: python manage.py migrate"),
            ("What is middleware?", "Middleware is a framework of hooks into Django’s request/response processing. It’s a light, low-level plugin system for globally altering Django’s input or output."),
            ("How do I configure static files?", "Set STATIC_URL in settings.py and use the {% static %} template tag."),
            ("What is CSRF?", "Cross-Site Request Forgery. Django provides built-in protection against CSRF attacks."),
            ("How do I use the CSRF token in a form?", "Use the {% csrf_token %} tag inside your HTML form."),
            ("What is a URL dispatcher?", "It maps URLs to views using the urls.py file."),
            ("How do I include URLs from another app?", "Use the include() function in your urls.py file."),
            ("What is a class-based view?", "Class-based views provide an alternative way to implement views as Python objects instead of functions."),
            ("How do I serve media files?", "Configure MEDIA_URL and MEDIA_ROOT, and append them to urls.py during development."),
            ("What is the difference between blank and null in models?", "null is database-related (allows NULL in DB), whereas blank is validation-related (allows empty field in forms)."),
            ("How do I set up a one-to-many relationship?", "Use a ForeignKey field in your model."),
            ("How do I set up a many-to-many relationship?", "Use a ManyToManyField in your model."),
            ("How do I set up a one-to-one relationship?", "Use a OneToOneField in your model."),
            ("What is Django ORM?", "Django ORM (Object-Relational Mapping) allows you to interact with your database, like querying and saving, using Python code instead of SQL."),
            ("How do I optimize Django queries?", "Use select_related() for single-valued relationships and prefetch_related() for multi-valued relationships."),
            ("What are Django signals?", "Signals allow decoupled applications get notified when actions occur elsewhere in the framework."),
            ("How do I handle file uploads?", "Use FileField or ImageField in your model and handle it via request.FILES in your view."),
            ("What is a Django form?", "Django forms handle HTML form generation, data validation, and conversion to Python types."),
            ("How do I customize the admin interface?", "Create a ModelAdmin class and register it with your model using admin.site.register().")
        ]

        count = 0
        for q, a in faqs:
            obj, created = FAQ.objects.get_or_create(question=q, defaults={'answer': a})
            if created:
                count += 1

        # Retraining is handled by the caller or view, avoiding recursion.

        self.stdout.write(self.style.SUCCESS(f'Successfully loaded {count} FAQs.'))
