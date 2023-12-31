from django.contrib import admin

from recipes.models import (Recipe, Tag, IngredientWithQuantity, ShoppingCard,
                            User, Ingredient, Subscription, Favourite)


class IngredientInline(admin.TabularInline):
    model = IngredientWithQuantity
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'favorites_score')
    filter_horizontal = ('ingredients', 'tags',)
    list_filter = ('name', 'author', 'tags',)
    search_fields = ('name', 'author', 'tags',)
    inlines = [IngredientInline]

    def favorites_score(self, instance):
        return instance.favourite_set.count()

    readonly_fields = ('favorites_score',)
    favorites_score.short_description = 'В избранном у'

    fieldsets = (
        ('Рецепт', {
            'fields': (
                'name',
                'image',
                'text',
                'cooking_time',
                'tags',
                'author',
                'favorites_score',
            ),
        }),
    )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(IngredientWithQuantity)
class IngredientWithQuantityAdmin(admin.ModelAdmin):
    list_display = ('ingredient', 'amount')


@admin.register(ShoppingCard)
class ShoppingCardAdmin(admin.ModelAdmin):
    list_display = ('user',)
    filter_horizontal = ('recipes',)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email')
    list_display_links = ('email',)
    list_filter = ('username', 'email',)
    search_fields = ('username', 'email',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user',)


@admin.register(Favourite)
class FavouriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
