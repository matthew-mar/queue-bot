from django.urls import path
from bot_app import chat_bot_views


urlpatterns = [
    path("<str:to>/", chat_bot_views.get_signal),
]
