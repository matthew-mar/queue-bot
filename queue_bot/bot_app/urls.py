from django.urls import path
from bot_app import views


urlpatterns = [
    path("test/", views.test_view)
]
