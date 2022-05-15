from django.urls import path
from bot_app import chat_bot_views


urlpatterns = [
    path("chat/", chat_bot_views.test_view)
]
