from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):

    def has_permission(self, request, view):

        # 1️⃣ Anyone can read
        if request.method in SAFE_METHODS:
            return True

        # 2️⃣ For write — user must be logged in
        if not request.user or not request.user.is_authenticated:
            return False

        # 3️⃣ Only admin can modify
        return request.user.is_staff