from django.contrib.admin import (ModelAdmin, register, TabularInline)

from . import models


@register(models.Ingredient)
class IngredientAdmin(ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)


@register(models.Tag)
class TagAdmin(ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug')
    list_editable = ('name', 'color', 'slug')
    search_fields = ('name',)


@register(models.Recipe)
class RecipeAdmin(ModelAdmin):
    list_display = ('pk', 'name', 'author', 'in_favorites')
    readonly_fields = ('in_favorites',)
    list_filter = ('name', 'author')
    save_on_top = True

    def in_favorites(self, obj):
        return obj.favorite_recipe.count()

    in_favorites.short_description = 'В избранном'


@register(models.Favourite)
class FavoriteAdmin(ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
    list_editable = ('user', 'recipe')

