import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_project.settings')
django.setup()

from apps.users.models import User
from apps.organizations.models import Organization, Workspace, Role, WorkspaceMember, Team
from apps.projects.models import Project, ProjectMember
from apps.tasks.models import Task
from rest_framework.test import APIClient

def setup_and_test_rbac():
    print("Initializing RBAC Data Structure...")
    
    # 1. Ensure SuperAdmin exists to own the Org
    try:
        superadmin = User.objects.get(email="superadmin@nexus.com")
        superadmin.set_password("SuperAdmin@123")
        superadmin.is_superuser = True
        superadmin.is_staff = True
        superadmin.save()
    except User.DoesNotExist:
        superadmin = User.objects.create_user(
            email="superadmin@nexus.com",
            password="SuperAdmin@123",
            is_superuser=True,
            is_staff=True,
            first_name="Super",
            last_name="Admin"
        )
    
    # 2. Create Demo Hierarchy
    org, _ = Organization.objects.get_or_create(
        name="Demo Organization",
        defaults={'domain': 'nexus.com', 'owner': superadmin}
    )
    
    workspace, _ = Workspace.objects.get_or_create(
        name="Demo Workspace",
        organization=org,
        defaults={'description': 'Demo workspace for RBAC'}
    )
    
    project, _ = Project.objects.get_or_create(
        name="Demo Project",
        workspace=workspace,
        defaults={'description': 'RBAC Testing Project', 'status': 'active'}
    )
    
    team, _ = Team.objects.get_or_create(
        name="Demo Team",
        workspace=workspace,
        defaults={'description': 'Core dev team'}
    )
    
    # 3. Create Roles
    roles_definition = ["Super Admin", "Admin", "Project Manager", "Team Lead", "Employee", "Client"]
    roles_map = {}
    for r in roles_definition:
        role_obj, _ = Role.objects.get_or_create(name=r, workspace=workspace)
        roles_map[r] = role_obj

    # 4. Create Users
    users_data = [
        {"email": "superadmin@nexus.com", "pass": "SuperAdmin@123", "role": "Super Admin", "is_super": True, "is_staff": True},
        {"email": "admin@nexus.com", "pass": "Admin@123", "role": "Admin", "is_super": False, "is_staff": True},  # Changed Ad3 to Admin@123 for Django validator
        {"email": "manager@nexus.com", "pass": "Manager@123", "role": "Project Manager", "is_super": False, "is_staff": False},
        {"email": "lead@nexus.com", "pass": "Lead@123", "role": "Team Lead", "is_super": False, "is_staff": False},
        {"email": "employee@nexus.com", "pass": "Employee@123", "role": "Employee", "is_super": False, "is_staff": False},
        {"email": "client@nexus.com", "pass": "Client@123", "role": "Client", "is_super": False, "is_staff": False},
    ]

    for ud in users_data:
        try:
            user = User.objects.get(email=ud["email"])
            user.set_password(ud["pass"])
            user.is_superuser = ud["is_super"]
            user.is_staff = ud["is_staff"]
            user.save()
        except User.DoesNotExist:
            user = User.objects.create_user(
                email=ud["email"],
                password=ud["pass"],
                is_superuser=ud["is_super"],
                is_staff=ud["is_staff"],
                first_name=ud["role"].split()[0],
                last_name="User"
            )
            
        # Assign to workspace
        wsm, _ = WorkspaceMember.objects.get_or_create(user=user, workspace=workspace)
        wsm.role = roles_map[ud["role"]]
        wsm.save()
        
        # Specific assignments based on role
        if ud["role"] in ["Project Manager", "Team Lead", "Employee", "Client"]:
            ProjectMember.objects.get_or_create(user=user, project=project)
        if ud["role"] in ["Team Lead", "Employee"]:
            team.members.add(user)
    
    print("Database records generated successfully!\n")
    print("Testing Authentication and Authorization...")
    
    client = APIClient()
    
    # 5. Automated Tests
    for ud in users_data:
        # Test Login
        response = client.post('/api/v1/auth/login/', {'email': ud["email"], 'password': ud["pass"]}, format='json')
        if response.status_code == 200:
            print(f"[OK] {ud['role']} Logged in successfully (JWT received)")
            token = response.data.get('access')
            client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
            
            # Test Authorization (Projects list - Everyone assigned should see 1 project, except if rules differ)
            proj_resp = client.get('/api/v1/projects/')
            if proj_resp.status_code == 200:
                if isinstance(proj_resp.data, list):
                    count = len(proj_resp.data)
                else:
                    count = len(proj_resp.data.get('results', []))
                print(f"    - Authorized to read projects. Found: {count}")
            else:
                print(f"    - [!] Failed to read projects: {proj_resp.status_code}")
                
            # Test Organization read
            org_resp = client.get('/api/v1/organizations/')
            if org_resp.status_code == 200:
                print(f"    - Authorized to read organizations.")
            
            # Reset credentials
            client.credentials()
        else:
            print(f"[X] {ud['role']} Login failed! Status: {response.status_code}")
            
    print("\nRBAC Configuration and Validation Complete.")

if __name__ == '__main__':
    setup_and_test_rbac()
