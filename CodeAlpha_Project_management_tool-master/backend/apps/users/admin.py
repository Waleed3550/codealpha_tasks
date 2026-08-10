from django.contrib import admin
from .models import User, Profile, Invitation

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    pass

@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    pass

