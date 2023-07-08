from django.contrib import admin
from django import forms

from recipes.models import (Recipe, Tag, IngredientWithQuantity, ShoppingCard,
                            User, Ingredient, Subscription, Favourite)


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        color = cleaned_data.get('color')
        if not isinstance(color, str) or len(color) != 7 or color[0] != "#":
            raise forms.ValidationError(
                "Поле color должно иметь тип вида #000000")
        return cleaned_data


class IngredientWithQuantityForm(forms.ModelForm):
    class Meta:
        model = IngredientWithQuantity
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        amount = cleaned_data.get('amount')
        if amount < 1:
            raise forms.ValidationError(
                "Поле amount должно быть больше или равно 1")
        return cleaned_data


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
    form = TagForm
    prepopulated_fields = {'slug': ('name',)}


@admin.register(IngredientWithQuantity)
class IngredientWithQuantityAdmin(admin.ModelAdmin):
    list_display = ('ingredient', 'amount')
    form = IngredientWithQuantityForm


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
