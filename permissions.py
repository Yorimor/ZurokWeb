from flask_login import current_user
from database import User


def has_permission(permission:str):
    if not current_user.is_authenticated or current_user.is_anonymous:
        return False

    if "." not in permission:
        return False
    route, perm = permission.split(".")

    if route in current_user.permissions:
        if perm in current_user.permissions[route]:
            return True

    return False


def edit_permission(permission:str, user_id:str, allow:bool):
    if not has_permission("users.admin") or not has_permission(permission):
        return False

    user_q = User.objects(user_id)
    if not user_q.exists():
        return False

    user = user_q.first()

    route, perm = permission.split(".")

    if allow:
        user.permissions[route].append(perm)
    else:
        user.permissions[route].remove(perm)

    user.permissions[route] = list(set(user.permissions[route]))
    user.save()
