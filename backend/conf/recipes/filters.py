import django_filters

from .models import Ingredient


class IngredientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name',
                                     lookup_expr='icontains')

    class Meta:
        model = Ingredient
        fields = ['name']


class RecipeFilter(django_filters.FilterSet):
    is_favorited = django_filters.BooleanFilter(field_name='name',
                                     lookup_expr='icontains')

    class Meta:
        model = Ingredient
        fields = ['name']
