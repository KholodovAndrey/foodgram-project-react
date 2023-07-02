from django.urls import path, include
from rest_framework import routers
from recipes.views import UserViewSet, TokenViewSet

users = routers.SimpleRouter()
users.register(r'users', UserViewSet)

urlpatterns = [
    path('', UserViewSet.as_view({'get': 'me'}),
         name='user-me'),
    path('', UserViewSet.as_view({'post': 'set_password'}),
         name='user-set-password'),
    path('', UserViewSet.as_view({'get': 'subscriptions'}),
         name='user-subscriptions'),
    path('', UserViewSet.as_view({'post': 'subscribe'}),
         name='user-subscribe'),
    path('auth/token/login/', TokenViewSet.as_view({'post': 'login'}),
         name='token-login'),
    path('auth/token/logout/', TokenViewSet.as_view({'post': 'logout'}),
         name='token-logout'),
    path('', include(users.urls)),
]
