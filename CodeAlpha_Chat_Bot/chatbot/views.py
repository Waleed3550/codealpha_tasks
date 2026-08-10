import json
import logging
import traceback
import time
from django.shortcuts import render
from django.http import JsonResponse
from .chatbot_engine import engine
from .models import FAQ

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

from django.views.decorators.csrf import csrf_exempt
from .models import FAQ, Conversation, Message

def index(request):
    return render(request, 'chatbot/index.html')

@csrf_exempt
def get_response(request):
    start_time = time.time()
    logger.info("=== INCOMING REQUEST ===")
    logger.info(f"HTTP Method: {request.method}")
    
    if request.method == 'POST':
        try:
            body_text = request.body.decode('utf-8')
            if not body_text.strip():
                return JsonResponse({'response': 'Empty request body.'}, status=400)
                
            data = json.loads(body_text)
            user_message = data.get('message', '')
            
            if not user_message.strip():
                return JsonResponse({'response': "Please enter a question."})
                
            logger.info(f"User Message: '{user_message}'")
            
            # Session-based Conversation tracking
            conv_id = request.session.get('conversation_id')
            if not conv_id:
                logger.info("Database Operation: Creating new Conversation")
                conv = Conversation.objects.create(title=user_message[:50])
                request.session['conversation_id'] = conv.id
            else:
                try:
                    conv = Conversation.objects.get(id=conv_id)
                    logger.info(f"Database Operation: Fetched Conversation {conv.id}")
                except Conversation.DoesNotExist:
                    logger.warning("Database Operation: Conversation missing, creating new.")
                    conv = Conversation.objects.create(title=user_message[:50])
                    request.session['conversation_id'] = conv.id
            
            # Save User Message
            logger.info("Database Operation: Saving User Message")
            Message.objects.create(
                conversation=conv,
                sender='user',
                message=user_message
            )
            
            # Train the engine on the fly (retrieves from DB)
            try:
                engine.train()
            except Exception as e:
                logger.error(f"NLP Training Error: {e}")
                return JsonResponse({'response': 'Error initializing NLP engine.'}, status=200)
            
            response_text, confidence = engine.get_response(user_message)
            
            # Save Bot Message
            logger.info("Database Operation: Saving Bot Message")
            Message.objects.create(
                conversation=conv,
                sender='bot',
                message=response_text,
                confidence_score=confidence
            )
            
            execution_time = time.time() - start_time
            logger.info(f"Response Time: {execution_time:.4f} seconds")
            
            return JsonResponse({'response': response_text, 'confidence': confidence})
            
        except json.JSONDecodeError as e:
            logger.error(f"JSONDecodeError: {str(e)}")
            return JsonResponse({'response': 'Invalid JSON format.'}, status=400)
        except RuntimeError as e:
            logger.error(f"RuntimeError (NLTK): {str(e)}")
            return JsonResponse({'response': str(e)}, status=200)
        except Exception as e:
            logger.error(f"Unexpected Exception: {str(e)}\n{traceback.format_exc()}")
            return JsonResponse({
                'response': f"An unexpected error occurred: {str(e)}. Please try again."
            }, status=200)
            
    return JsonResponse({'response': 'Invalid request method.'}, status=400)

@csrf_exempt
def chat_history(request):
    """Return a list of recent conversations (GET /chat-history/)."""
    if request.method == 'GET':
        convs = Conversation.objects.order_by('-created_at')[:20]
        data = [{'id': c.id, 'title': c.title} for c in convs]
        return JsonResponse({'conversations': data})
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def conversation_detail(request, conv_id):
    """Handle GET and DELETE for a specific conversation."""
    try:
        conv = Conversation.objects.get(id=conv_id)
    except Conversation.DoesNotExist:
        return JsonResponse({'error': 'Conversation not found'}, status=404)
        
    if request.method == 'GET':
        # Load chat into session
        request.session['conversation_id'] = conv.id
        
        # Return messages for the conversation
        messages = Message.objects.filter(conversation=conv).order_by('created_at')
        data = [{
            'id': m.id,
            'sender': m.sender,
            'text': m.message,
            'timestamp': m.created_at.timestamp() * 1000
        } for m in messages]
        return JsonResponse({'messages': data})
        
    elif request.method == 'DELETE':
        # Delete the conversation
        conv.delete()
        if request.session.get('conversation_id') == int(conv_id):
            request.session.pop('conversation_id', None)
        return JsonResponse({'status': 'deleted'})
        
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def get_messages_current(request):
    """Return messages for the current session conversation."""
    conv_id = request.session.get('conversation_id')
    if not conv_id:
        return JsonResponse({'messages': []})
    return conversation_detail(request, conv_id)

@csrf_exempt
def new_chat(request):
    """Start a new chat by clearing the session conversation_id."""
    request.session.pop('conversation_id', None)
    return JsonResponse({'status': 'ok'})

@csrf_exempt
def search_chats(request):
    """Search conversation titles and their messages."""
    query = request.GET.get('q', '').strip()
    if not query:
        return chat_history(request)
        
    from django.db.models import Q
    convs = Conversation.objects.filter(
        Q(title__icontains=query) | Q(messages__message__icontains=query)
    ).distinct().order_by('-created_at')[:20]
    
    data = [{'id': c.id, 'title': c.title} for c in convs]
    return JsonResponse({'conversations': data})

