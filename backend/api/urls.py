from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'recipes', views.RecipeViewSet, basename='recipes')
router.register(r'tags', views.TagViewSet, basename='tags')
router.register(r'users', views.CustomUserViewSet, basename='users')
router.register(
    r'ingredients', views.IngredientViewSet, basename='ingredients')

urlpatterns = [
    path(r'auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
