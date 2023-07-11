import django_filters
from django.db.models import Q

from django_filters import rest_framework
from django_filters import FilterSet

from .models import Ingredient, Recipe, Favourite, ShoppingCard


class IngredientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name',
                                     lookup_expr='icontains')

    class Meta:
        model = Ingredient
        fields = ['name']


class RecipeFilter(FilterSet):
    is_favorited = rest_framework.BooleanFilter(field_name='favourites__user',
                                                method='filter_is_favorited')
    is_in_shopping_cart = rest_framework.BooleanFilter(
        field_name='shoppingcard__user', method='filter_is_in_shopping_cart')
    author = rest_framework.CharFilter(field_name='author__username',
                                       method='filter_author')
    tags = rest_framework.CharFilter(method='filter_tags')

    class Meta:
        model = Recipe
        fields = ['is_favorited', 'is_in_shopping_cart', 'author', 'tags']

    def filter_is_favorited(self, queryset, name, value):
        request = self.request
        if value:
            recipe_pk_list = Favourite.objects.filter(
                user=request.user).values_list('recipe_id', flat=True)
            return queryset.filter(pk__in=recipe_pk_list)
        return queryset

    def filter_author(self, queryset, name, value):
        if value:
            return queryset.filter(author__id=int(value))
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        request = self.request
        if value:
            recipe_pk_list = ShoppingCard.objects.get(
                user=request.user).recipes.all().values_list('pk', flat=True)
            return queryset.filter(pk__in=recipe_pk_list)
        return queryset

    def filter_tags(self, queryset, name, value):
        tags = self.request.query_params.getlist('tags')
        if tags:
            conditions = Q()
            for tag in tags:
                conditions |= Q(tags__slug__icontains=tag)
            return queryset.filter(conditions).distinct()
        return queryset.none()
