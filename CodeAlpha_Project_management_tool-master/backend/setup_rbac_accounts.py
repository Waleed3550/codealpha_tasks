import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_project.settings')
django.setup()

from apps.users.models import User
from apps.organizations.models import Organization, Workspace, Role, WorkspaceMember

def create_rbac_accounts():
    print("Setting up RBAC default accounts...")

    # Find or create superadmin first for org ownership
    password = "Password@123"
    try:
        owner = User.objects.get(email="superadmin@test.com")
    except User.DoesNotExist:
        owner = User.objects.create_user(
            email="superadmin@test.com",
            password=password,
            is_superuser=True,
            is_staff=True,
            first_name="Super",
            last_name="Admin"
        )

    # Ensure Organization and Workspace exist
    org, _ = Organization.objects.get_or_create(
        name="Default Enterprise",
        defaults={'domain': 'enterprise.com', 'owner': owner}
    )

    workspace, _ = Workspace.objects.get_or_create(
        name="Main Workspace",
        organization=org,
        defaults={'description': 'Main workspace for RBAC testing'}
    )

    roles_data = [
        "Super Admin",
        "Admin",
        "Project Manager",
        "Team Lead",
        "Employee",
        "Client"
    ]

    # Create Roles in DB if they don't exist
    role_objects = {}
    for role_name in roles_data:
        role, _ = Role.objects.get_or_create(name=role_name, workspace=workspace)
        role_objects[role_name] = role

    users_to_create = [
        {"email": "superadmin@test.com", "role": "Super Admin", "is_superuser": True, "is_staff": True},
        {"email": "admin@test.com", "role": "Admin", "is_superuser": False, "is_staff": True},
        {"email": "pm@test.com", "role": "Project Manager", "is_superuser": False, "is_staff": False},
        {"email": "teamlead@test.com", "role": "Team Lead", "is_superuser": False, "is_staff": False},
        {"email": "employee@test.com", "role": "Employee", "is_superuser": False, "is_staff": False},
        {"email": "client@test.com", "role": "Client", "is_superuser": False, "is_staff": False},
    ]

    password = "Password@123"
    
    for u_data in users_to_create:
        email = u_data["email"]
        try:
            user = User.objects.get(email=email)
            print(f"User {email} already exists. Updating properties...")
            user.is_superuser = u_data["is_superuser"]
            user.is_staff = u_data["is_staff"]
            user.set_password(password)
            user.save()
        except User.DoesNotExist:
            user = User.objects.create_user(
                email=email,
                password=password,
                is_superuser=u_data["is_superuser"],
                is_staff=u_data["is_staff"],
                first_name=u_data["role"].split()[0],
                last_name="User"
            )
            print(f"Created user {email}")

        if not org.owner_id and u_data["role"] == "Super Admin":
            org.owner = user
            org.save()

        # Assign workspace membership and role
        member, created = WorkspaceMember.objects.get_or_create(
            user=user, 
            workspace=workspace,
        )
        member.role = role_objects[u_data["role"]]
        member.save()

    print("\n✅ Setup complete! You can log in using:")
    for u in users_to_create:
        print(f" - Email: {u['email']} | Password: {password} ({u['role']})")

if __name__ == '__main__':
    create_rbac_accounts()
