from django_filters import AllValuesMultipleFilter
from django_filters.rest_framework import FilterSet, filters
from rest_framework.filters import SearchFilter


from recipes.models import Recipe


class IngredientSearchFilter(SearchFilter):
    search_param = 'name'


class RecipeFilter(FilterSet):
    tags = AllValuesMultipleFilter(field_name="tags__slug")
    is_favorited = filters.BooleanFilter(
        method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(favorite_recipe__user=user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(shopping_recipe__user=user)
        return queryset

    class Meta:
        model = Recipe
        fields = ('tags', 'author',)
