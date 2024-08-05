# your_app_name/auth_backend.py

from django.contrib.auth.backends import BaseBackend # type: ignore
from django.contrib.auth.models import User # type: ignore
from .models import Agent
from django.contrib.auth.hashers import check_password # type: ignore

class AgentBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            agent = Agent.objects.get(username=username)
            if agent and check_password(password, agent.password):
                return agent.user
        except Agent.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
