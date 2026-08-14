from utils.constants import ROLES
from users.models import User


def can_access_task(user, task):
    """
    Check if user has permission to access/modify the given task based on role.
    - TELE_USER: only tasks they created
    - TELE_ADMIN: tasks they created + team tasks + tasks by Tele Users under them
    - All other roles: full access
    """
    if user.role == ROLES.TELE_USER.value:
        return task.created_by_id == user.user_id

    if user.role == ROLES.TELE_ADMIN.value:
        if task.created_by_id == user.user_id:
            return True
        if getattr(user, 'team', None) and task.team == user.team:
            return True
        tele_user_ids = list(User.objects.filter(
            role=ROLES.TELE_USER.value,
            assign_so=user
        ).values_list('user_id', flat=True))
        return task.created_by_id in tele_user_ids

    return True
