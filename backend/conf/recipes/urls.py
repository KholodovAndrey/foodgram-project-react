from django.urls import path, include
from rest_framework import routers
from recipes.views import TagViewSet, IngredientViewSet

tags = routers.SimpleRouter()
tags.register(r'tags', TagViewSet)
ingredients = routers.SimpleRouter()
ingredients.register(r'ingredients', IngredientViewSet)

urlpatterns = [
    path('', include(tags.urls)),
    path('', include(ingredients.urls)),
]
