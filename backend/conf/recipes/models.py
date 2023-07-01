from django.db import models

# Create your models here.
from users.models import User


class Tag(models.Model):
    name = models.CharField(max_length=201, blank=False, null=False,
                            unique=True, verbose_name='Name')
    color = models.CharField(max_length=8, blank=False, null=False,
                             unique=True, verbose_name='Color')
    slug = models.SlugField(max_length=201, blank=False, null=False,
                            unique=True, verbose_name='Slug')

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'recipes'
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'


class Ingredient(models.Model):
    name = models.CharField(max_length=201, blank=False, null=False,
                            verbose_name='Name')
    measurement_unit = models.CharField(max_length=201, blank=False,
                                        null=False,
                                        verbose_name='Measurement unit')

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'recipes'
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'


class IngredientWithQuantity(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE,
                                   blank=False, null=False,
                                   verbose_name='Ingredient')
    amount = models.IntegerField(blank=False, null=False,
                                 verbose_name='Amount')

    def __str__(self):
        return self.ingredient

    class Meta:
        app_label = 'recipes'
        verbose_name = 'IngredientWithQuantity'
        verbose_name_plural = 'IngredientsWithQuantity'


class Recipe(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False,
                            verbose_name='Name')
    image = models.ImageField(upload_to='recipe/', blank=False, null=False,
                              verbose_name='Image')
    text = models.TextField(blank=False, null=False, verbose_name='Text')
    cooking_time = models.IntegerField(blank=False, null=False,
                                       verbose_name='Cooking time')
    ingredients = models.ManyToManyField(IngredientWithQuantity,
                                         related_name='ingredients',
                                         blank=False,
                                         verbose_name='Ingredients')
    tags = models.ManyToManyField(Tag, related_name='tags',
                                  blank=False, verbose_name='Tags')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               verbose_name='Author')

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'recipes'
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'


class Favourite(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               verbose_name='Recipe')
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             verbose_name='User')

    def __str__(self):
        return self.recipe

    class Meta:
        app_label = 'recipes'
        verbose_name = 'Favourite'
        verbose_name_plural = 'Favourites'


class Subscription(models.Model):
    subscriptions = models.ManyToManyField(User,
                                           related_name='subscriptions',
                                           blank=False,
                                           verbose_name='Subscriptions')
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             verbose_name='User')

    def __str__(self):
        return self.user

    class Meta:
        app_label = 'recipes'
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'


class ShoppingCard(models.Model):
    recipes = models.ManyToManyField(Recipe,
                                     related_name='recipes',
                                     blank=False,
                                     verbose_name='Recipes')
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             verbose_name='User')

    def __str__(self):
        return self.user

    class Meta:
        app_label = 'recipes'
        verbose_name = 'ShoppingCard'
        verbose_name_plural = 'ShoppingCards'
