from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    message = "Только владелец может управлять этим объектом."

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
