from django.contrib.auth.backends import ModelBackend
from .models import ClientUser

class PhoneBackend(ModelBackend):
    """Authenticate users using their phone number instead of username"""
    def authenticate(self, request, phone=None, password=None, **kwargs):
        try:
            user = ClientUser.objects.get(phone=phone)
        except ClientUser.DoesNotExist:
            return None

        if user.check_password(password):
            return user
        return None


from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from listings.models import AdminUser, ClientUser

# ----------------------
# Client backend
# ----------------------
class ClientBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = ClientUser.objects.get(phone=username)
            if user.check_password(password):
                return user
        except ClientUser.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return ClientUser.objects.get(pk=user_id)
        except ClientUser.DoesNotExist:
            return None

# ----------------------
# Admin backend
# ----------------------
class AdminBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = AdminUser.objects.get(phone=username)
            if user.check_password(password):
                return user
        except AdminUser.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return AdminUser.objects.get(pk=user_id)
        except AdminUser.DoesNotExist:
            return None
