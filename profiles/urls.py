from django.urls import path
from . import views

urlpatterns = [
    path('<str:username>/', views.profile_view, name='profile'),
    path('edit/', views.edit_profile, name='edit_profile'),
    path('follow/<int:profile_id>/', views.follow, name='follow'),
]