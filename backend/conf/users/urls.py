from django.urls import path, include
from rest_framework import routers
from recipes.views import UserViewSet, TokenViewSet

users = routers.SimpleRouter()
users.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(users.urls)),
    path('', UserViewSet.as_view({'get': 'me'}),
         name='user-me'),
    path('', UserViewSet.as_view({'post': 'set_password'}),
         name='user-set-password'),
    path('auth/token/login/', TokenViewSet.as_view({'post': 'login'}),
         name='token-login'),
    path('auth/token/logout/', TokenViewSet.as_view({'post': 'logout'}),
         name='token-logout'),
]
