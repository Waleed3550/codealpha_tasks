from enum import Enum

class RoleEnum(str, Enum):
    SUPER_ADMIN = 'Super Admin'
    ADMIN = 'Admin'
    PROJECT_MANAGER = 'Project Manager'
    TEAM_LEAD = 'Team Lead'
    TEAM_MEMBER = 'Team Member'
    GUEST = 'Guest'

# Define hierarchical role levels for easy permission checking
ROLE_LEVELS = {
    RoleEnum.SUPER_ADMIN: 100,
    RoleEnum.ADMIN: 90,
    RoleEnum.PROJECT_MANAGER: 80,
    RoleEnum.TEAM_LEAD: 70,
    RoleEnum.TEAM_MEMBER: 50,
    RoleEnum.GUEST: 10,
}
