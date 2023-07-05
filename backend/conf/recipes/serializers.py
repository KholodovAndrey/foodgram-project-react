import base64
import uuid

from datetime import datetime
from django.core.files.base import ContentFile
from django.db import transaction
from rest_framework import serializers, permissions
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404

from recipes.models import (Tag, Ingredient, Recipe, IngredientWithQuantity,
                            Favourite, ShoppingCard)
from users.models import User


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор рецепта."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeFavouriteSerializer(serializers.ModelSerializer):
    """Сериализатор избранного рецепта."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')

    def get_fields(self, *args, **kwargs):
        fields = super().get_fields(*args, **kwargs)
        for field in fields:
            fields[field].read_only = True
        return fields

    def validate(self, data):
        if self.context.get('method') == 'POST':
            if self.context['favourite'].exists():
                raise ValidationError(
                    {'error': 'the recipe is already in favorites'})
            return data
        if not self.context['favourite'].exists():
            raise ValidationError(
                {'error': 'the recipe is not in favorites yet'})
        return data


class RecipeShoppingCardSerializer(serializers.ModelSerializer):
    """Сериализатор списка покупок."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')

    def get_fields(self, *args, **kwargs):
        fields = super().get_fields(*args, **kwargs)
        for field in fields:
            fields[field].read_only = True
        return fields

    def validate(self, data):
        if self.context.get('method') == 'POST':
            if self.context['shopping_card'].recipes.filter(
                    pk=self.context['recipe'].pk).exists():
                raise ValidationError(
                    {'error': 'the recipe is already in shopping card'})
            return data
        if not self.context['shopping_card'].recipes.filter(
                pk=self.context['recipe'].pk).exists():
            raise ValidationError(
                {'error': 'the recipe is not in shopping card'})
        return data


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя."""

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password',)


class UserResponseSerializer(serializers.ModelSerializer):
    """Сериализатор отображения пользователя."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return user.subscription_set.get(user=user).subscriptions.filter(
                pk=obj.pk).exists()
        return False


class UserResponseWithRecipesSerializer(serializers.ModelSerializer):
    """Сериализатор принадлежности пользователя и рецепта."""

    recipes = RecipeSerializer(source='recipe_set', many=True)
    is_subscribed = serializers.BooleanField(default=False)
    recipes_count = serializers.IntegerField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count')


class UserResponseWithRecipesWithValidateSerializer(
    serializers.ModelSerializer
):
    """Сериализатор подписки."""

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',)

    def get_fields(self, *args, **kwargs):
        fields = super().get_fields(*args, **kwargs)
        for field in fields:
            fields[field].read_only = True
        return fields

    def validate(self, data):
        if self.context.get('method') == 'POST':
            if self.context['current_user'] == self.context['user']:
                raise ValidationError(
                    {'error': 'it is not possible to subscribe to yourself'})
            if self.context['subscribe'].subscriptions.filter(
                    pk=self.context['user'].pk).exists():
                raise ValidationError(
                    {'error': 'it is not possible to subscribe to this user'})
            return data
        if not self.context['subscribe'].subscriptions.filter(
                pk=self.context['user'].pk).exists():
            raise ValidationError(
                {'error': 'you are not subscribed to this user'})
        return data


class SetPasswordSerializer(serializers.ModelSerializer):
    """Сериализатор смены пароля."""

    new_password = serializers.CharField(required=True)
    current_password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = (
            'new_password', 'current_password',)

    def get_fields(self, *args, **kwargs):
        fields = super().get_fields(*args, **kwargs)
        for field in fields:
            fields[field].read_only = True
        return fields

    def validate(self, data):
        if not self.context['user'].check_password(
                self.initial_data['current_password']):
            raise ValidationError('Invalid current password')
        return data


class TokenSerializer(serializers.ModelSerializer):
    """Сериализатор токена."""

    class Meta:
        model = Token
        fields = ('__all__')

    def get_fields(self, *args, **kwargs):
        fields = super().get_fields(*args, **kwargs)
        for field in fields:
            fields[field].read_only = True
        return fields

    def validate(self, data):
        if not self.context['user'].check_password(
                self.initial_data['password']):
            raise ValidationError('Invalid current password')
        return data


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тэга."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингридиента."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientWithQuantitySerializer(serializers.ModelSerializer):
    """Сериализатор ингридиента в рецепте."""

    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientWithQuantity
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeResponseSerializer(serializers.ModelSerializer):
    """Сериализатор работы с рецептом."""

    tags = TagSerializer(many=True, read_only=True)
    author = UserResponseSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')

    def get_ingredients(self, obj):
        recipe_ingredients = IngredientWithQuantity.objects.filter(recipe=obj)
        serializer = IngredientWithQuantitySerializer(recipe_ingredients,
                                                      many=True)
        return serializer.data

    def get_is_in_shopping_cart(self, obj):
        if self.context['request'].user.is_authenticated:
            if obj.pk in ShoppingCard.objects.filter(
                    user=self.context['request'].user
            ).values_list('recipes__pk', flat=True):
                return True
        return False

    def get_is_favorited(self, obj):
        if self.context['request'].user.is_authenticated:
            if obj.pk in Favourite.objects.filter(
                    user=self.context['request'].user
            ).values_list('recipe__pk', flat=True):
                return True
        return False

    def validate(self, data):
        if self.context['request'].method not in permissions.SAFE_METHODS:
            # почему лишнее условие? если мне прилетает
            # безопасный метод, например get, то вся логика
            # валидации мне не нужна. Проверка на обязательность
            # также нужна, потому что использование required = True,
            # не возможно с использование read_only, а использование
            # read_only, нужно для получения списка записей

            errors = {}
            required_filelds = ['ingredients', 'tags']
            if self.context['request'].method != "PATCH":
                required_filelds.append('image')
            for field in required_filelds:
                if field not in self.initial_data:
                    errors[field] = "Обязательное поле"
            if errors:
                raise ValidationError(errors)
            for ingredient in self.initial_data['ingredients']:
                try:
                    int(ingredient['amount'])
                    if int(ingredient['amount']) < 1:
                        raise ValueError(
                            {'error': 'amount must be int and must be more 1'})
                except Exception:
                    raise ValueError(
                        {'error': 'amount must be int and must be more 1'})
        return data

    def base_64_to_image(self):
        if self.initial_data.get('image'):
            format_image, imgstr = self.initial_data['image'].split(';base64,')
            ext = format_image.split('/')[-1]
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            unique_name = (
                f"{timestamp}_{str(uuid.uuid4())[:8]}"
            )
            return ContentFile(
                base64.b64decode(imgstr),
                name=f"{unique_name}.{ext}"
            )
        return None

    def get_image(self, obj):
        return obj.image.url

    def create(self, validated_data):
        image = self.base_64_to_image()
        tags = [get_object_or_404(Tag, pk=pk) for pk in
                self.initial_data['tags']]
        with transaction.atomic():
            recipe = Recipe.objects.create(
                author=self.context['request'].user,
                name=self.initial_data['name'],
                text=self.initial_data['text'],
                image=image,
                cooking_time=self.initial_data['cooking_time']
            )
            recipe.tags.set(tags)
            recipe.save()
            # ingredients = [IngredientWithQuantity.objects.bulk_create([
            #     IngredientWithQuantity(
            #         ingredient=get_object_or_404(Ingredient, pk=item['id']),
            #         amount=item['amount'],
            #         recipe=recipe
            #     )]) for item in self.initial_data['ingredients']]
        return recipe
    # почему get_object_or_404 лишний? Если пользователь
    # в запросе укажет не верный id ингредиента? С помощью
    # get_object_or_404 сразу происиходит проверка входных данных.
    # Тем боле нам все равно нужно делать запрос в бд, чтобы достать
    # конкретный ингредиент для закрепления за рецептом
    # и далее так же

    def update(self, instance, validated_data):
        image = self.base_64_to_image()
        tags = [get_object_or_404(Tag, pk=pk) for pk in
                self.initial_data['tags']]
        with transaction.atomic():
            instance.name = self.initial_data['name']
            instance.text = self.initial_data['text']
            if image:
                instance.image = image
            instance.cooking_time = self.initial_data['cooking_time']
            instance.tags.set(tags)
            instance.save()
            for ingredient in IngredientWithQuantity.objects.filter(
                    recipe=instance):
                ingredient.delete()
            # ingredients = [IngredientWithQuantity.objects.bulk_create([
            #     IngredientWithQuantity(
            #         ingredient=get_object_or_404(Ingredient, pk=item['id']),
            #         amount=item['amount'],
            #         recipe=instance
            #     )]) for item in self.initial_data['ingredients']]
        return instance
