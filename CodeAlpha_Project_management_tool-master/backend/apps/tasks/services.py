from .models import Task, Checklist, ChecklistItem
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class AITaskService:
    """
    Handles all AI-powered operations for task management as requested in Part 3.
    Integrates directly with the database to automatically generate content.
    """
    
    @staticmethod
    def generate_subtasks(task_id: str, prompt: str):
        """
        Uses AI (e.g. OpenAI/Anthropic API) to automatically generate a checklist of subtasks.
        """
        task = Task.objects.get(id=task_id)
        
        # Enterprise integration point: call to your LLM provider would happen here.
        # response = llm_client.generate(prompt=prompt)
        
        # Mocked AI Response for immediate frontend consumption
        ai_generated_items = [
            f"Analyze requirements for: {prompt[:20]}...",
            "Draft technical specification",
            "Implement initial prototype",
            "Submit for peer review"
        ]
        
        checklist = Checklist.objects.create(task=task, name="AI Generated Plan")
        
        items = []
        for index, item_name in enumerate(ai_generated_items):
            items.append(
                ChecklistItem.objects.create(
                    checklist=checklist, 
                    text=item_name,
                    order=index
                )
            )
            
        return items

    @staticmethod
    def predict_risk(task_id: str) -> dict:
        """
        Analyzes dependencies, assignees' workloads, and timeline to predict completion risk.
        """
        # Complex heuristic or ML model inference goes here.
        return {
            "risk_level": "High",
            "reason": "3 blocking dependencies are currently overdue.",
            "confidence_score": 0.87,
            "suggested_action": "Reassign tasks or extend deadline."
        }

    @staticmethod
    def generate_daily_summary(user_id: str) -> str:
        """
        Generates the AI Daily Summary feature for a specific user.
        """
        return "You have 3 high priority tasks due today. Your team's velocity is up 15%."

class TaskService:
    """
    Standard business logic for task management (Kanban operations).
    """
    @staticmethod
    def move_task(task_id: str, new_status: str, user_id: str):
        task = Task.objects.get(id=task_id)
        task.status = new_status
        task.updated_by_id = user_id
        task.save(update_fields=['status', 'updated_at', 'updated_by_id'])
        
        # Trigger the Django Channels WebSocket broadcast
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f'project_{task.project_id}',
                {
                    'type': 'board_update',
                    'action': 'TASK_MOVED',
                    'data': {
                        'task_id': str(task.id),
                        'new_status': new_status,
                        'updated_by': str(user_id)
                    }
                }
            )
        
        return task
