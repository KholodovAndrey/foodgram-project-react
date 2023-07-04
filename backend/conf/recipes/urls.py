from django.urls import path, include
from rest_framework import routers

from recipes.views import TagViewSet, IngredientViewSet, RecipeViewSet

tags = routers.SimpleRouter()
tags.register(r'tags', TagViewSet)
ingredients = routers.SimpleRouter()
ingredients.register(r'ingredients', IngredientViewSet)
recipes = routers.SimpleRouter()
recipes.register(r'recipes', RecipeViewSet)

urlpatterns = [
    path('', include(tags.urls)),
    path('', include(ingredients.urls)),
    path('', include(recipes.urls)),
    path('', RecipeViewSet.as_view({'get': 'download_shopping_cart'}),
         name='user-download-shopping-cart'),
    path('', RecipeViewSet.as_view({'post': 'shopping_cart'}),
         name='user-download-shopping-cart'),
    path('', RecipeViewSet.as_view({'post': 'favorite'}),
         name='user-favorite'),
]
