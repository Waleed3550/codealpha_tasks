from .models import Invitation
from django.utils import timezone
from datetime import timedelta

class UserService:
    """
    Business logic layer for User operations.
    Keeps fat models and controllers skinny.
    """
    @staticmethod
    def create_invitation(email, inviter):
        invitation = Invitation.objects.create(
            email=email,
            created_by=inviter,
            expires_at=timezone.now() + timedelta(days=7)
        )
        # Celery task execution would go here:
        # from .tasks import send_invitation_email
        # send_invitation_email.delay(invitation.id)
        return invitation
