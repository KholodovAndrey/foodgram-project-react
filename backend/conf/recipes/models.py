from django.core.validators import RegexValidator, MinValueValidator
from django.db import models

from users.models import User

hex_validator = RegexValidator(regex=r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
                               message='Введите корректное hex-значение.')


class Tag(models.Model):
    """Модель тега."""

    name = models.CharField(max_length=201, blank=False, null=False,
                            unique=True, verbose_name='Имя')
    color = models.CharField(max_length=8, blank=False, null=False,
                             unique=True, verbose_name='Цвет',
                             validators=[hex_validator])
    slug = models.SlugField(max_length=201, blank=False, null=False,
                            unique=True, verbose_name='Слаг')

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'recipes'
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'


class Ingredient(models.Model):
    """Модель ингридиента."""

    name = models.CharField(max_length=201, blank=False, null=False,
                            verbose_name='Имя')
    measurement_unit = models.CharField(max_length=201, blank=False,
                                        null=False,
                                        verbose_name='Единица измерения')

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'recipes'
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


class IngredientWithQuantity(models.Model):
    """Модель количества ингридиента."""

    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE,
                                   blank=False, null=False,
                                   related_name='ingredientwithquantity_set',
                                   verbose_name='Ингредиент')
    recipe = models.ForeignKey('Recipe', on_delete=models.CASCADE,
                               blank=False, null=False,
                               related_name='ingredientwithquantity_set',
                               verbose_name='Рецепт')
    amount = models.PositiveSmallIntegerField(blank=False, null=False,
                                              verbose_name='Количество',
                                              validators=[
                                                  MinValueValidator(1)])

    def __str__(self):
        return f'{self.ingredient.name} - {self.amount}'

    class Meta:
        app_label = 'recipes'
        verbose_name = 'ИнгредиентСКоличеством'
        verbose_name_plural = 'ИнгредиентыСКоличеством'


class Recipe(models.Model):
    """Модель рецепта."""

    name = models.CharField(max_length=255, blank=False, null=False,
                            verbose_name='Имя')
    image = models.ImageField(upload_to='recipe/', blank=False, null=False,
                              verbose_name='Картинка')
    text = models.TextField(blank=False, null=False, verbose_name='Текст')
    cooking_time = models.IntegerField(blank=False, null=False,
                                       verbose_name='Время готовки',
                                       validators=[
                                           MinValueValidator(1)]
                                       )
    ingredients = models.ManyToManyField(Ingredient,
                                         through=IngredientWithQuantity,
                                         related_name='ingredients',
                                         blank=False,
                                         verbose_name='Ингредиенты')
    tags = models.ManyToManyField(Tag, related_name='tags',
                                  blank=False, verbose_name='Тэги')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='recipe_set',
                               verbose_name='Автор')

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'recipes'
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class Favourite(models.Model):
    """Модель избранного."""

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='favourite_set',
                               verbose_name='Рецепт')
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='favourite_set',
                             verbose_name='Пользователь')

    def __str__(self):
        return self.recipe.name

    class Meta:
        app_label = 'recipes'
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'


class Subscription(models.Model):
    """Модель подписки."""

    subscriptions = models.ForeignKey(User,
                                      related_name='user_subscriptions',
                                      on_delete=models.CASCADE,
                                      blank=True, null=True,
                                      verbose_name='Подписки')

    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='subscription_set',
                             verbose_name='Пользователь')

    def __str__(self):
        return self.user.username

    class Meta:
        app_label = 'recipes'
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'


class ShoppingCard(models.Model):
    """Модель списка покупок."""

    recipes = models.ManyToManyField(Recipe,
                                     related_name='recipes',
                                     blank=True,
                                     verbose_name='Рецепты')
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='shoppingcard_set',
                             verbose_name='Пользователь')

    def __str__(self):
        return self.user.username

    class Meta:
        app_label = 'recipes'
        verbose_name = 'СписокПокупок'
        verbose_name_plural = 'СпискиПокупок'
