import base64
import random
import uuid
from datetime import datetime
from django.core.files.base import ContentFile
from rest_framework import serializers, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404

from recipes.models import Tag, Ingredient, Recipe, IngredientWithQuantity, \
    Favourite, ShoppingCard
from users.models import User


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор рецепта."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeFavouritePostSerializer(serializers.Serializer):
    """Сериализатор добавления избранного рецепта."""

    def validate(self, data):
        if self.context['favourite'].exists():
            raise ValidationError(
                {'error': 'the recipe is already in favorites'})
        return data


class RecipeFavouriteDelteSerializer(serializers.Serializer):
    """Сериализатор исключения избранного рецепта."""

    def validate(self, data):
        if not self.context['favourite'].exists():
            raise ValidationError(
                {'error': 'the recipe is not in favorites yet'})
        return data


class RecipeShoppingCardPostSerializer(serializers.Serializer):
    """Сериализатор добавления в список покупок."""

    def validate(self, data):
        if self.context['shopping_card'].recipes.filter(
                pk=self.context['recipe'].pk).exists():
            raise ValidationError(
                {'error': 'the recipe is already in shopping card'})
        return data


class RecipeShoppingCardDeleteSerializer(serializers.Serializer):
    """Сериализатор исключения из списка покупок."""

    def validate(self, data):
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

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return user.subscription_set.get(user=user).subscriptions.filter(
                pk=obj.pk).exists()
        return False

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed')


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


class UserResponseWithRecipesForPostSerializer(serializers.Serializer):
    """Сериализатор подписки."""

    def validate(self, data):
        if self.context['current_user'] == self.context['user']:
            raise ValidationError(
                {'error': 'it is not possible to subscribe to yourself'})
        if self.context['subscribe'].subscriptions.filter(
                pk=self.context['user'].pk).exists():
            raise ValidationError(
                {'error': 'it is not possible to subscribe to this user'})
        return data


class UserResponseWithRecipesForDeleteSerializer(serializers.Serializer):
    """Сериализатор отмены подписки."""

    def validate(self, data):
        if not self.context['subscribe'].subscriptions.filter(
                pk=self.context['user'].pk).exists():
            raise ValidationError(
                {'error': 'you are not subscribed to this user'})
        return data


class SetPasswordSerializer(serializers.Serializer):
    """Сериализатор смены пароля."""

    new_password = serializers.CharField(required=True)
    current_password = serializers.CharField(required=True)

    def validate(self, data):
        if not self.context['user'].check_password(
                self.initial_data['current_password']):
            raise ValidationError('Invalid current password')
        return data


class TokenSerializer(serializers.Serializer):
    """Сериализатор токена."""

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
        fields = ('id', 'name', 'measurement_unit',)


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
    ingredients = IngredientWithQuantitySerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

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
            errors = {}
            required_filelds = ['tags', 'ingredients', 'name', 'text',
                                'cooking_time']
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
                except ValueError:
                    ingredient['amount'] = 1
                if int(ingredient['amount']) < 1:
                    ingredient['amount'] = 1
        return data

    def base_64_to_image(self):
        if self.initial_data.get('image'):
            format_image, imgstr = self.initial_data['image'].split(';base64,')
            ext = format_image.split('/')[-1]
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            random_number = random.randint(1000, 9999)
            unique_name = f"{timestamp}_{random_number}_{str(uuid.uuid4())[:8]}"
            return ContentFile(
                base64.b64decode(imgstr),
                name=f"{unique_name}.{ext}"
            )
        return None

    def get_image(self, obj):
        return obj.image.url

    def create(self, validated_data):
        image = self.base_64_to_image()
        ingredients = [IngredientWithQuantity.objects.get_or_create(
            ingredient=get_object_or_404(Ingredient, pk=item['id']),
            amount=item['amount'],
            defaults={
                'ingredient': get_object_or_404(Ingredient, pk=item['id']),
                'amount': item['amount']
            }
        )[0] for item in self.initial_data['ingredients']]
        tags = [get_object_or_404(Tag, pk=pk) for pk in
                self.initial_data['tags']]
        recipe = Recipe.objects.create(
            author=self.context['request'].user,
            name=self.initial_data['name'],
            text=self.initial_data['text'],
            image=image,
            cooking_time=self.initial_data['cooking_time']
        )
        recipe.tags.set(tags)
        recipe.ingredients.set(ingredients)
        recipe.save()
        return recipe

    def update(self, instance, validated_data):
        image = self.base_64_to_image()
        ingredients = [IngredientWithQuantity.objects.get_or_create(
            ingredient=get_object_or_404(Ingredient, pk=item['id']),
            amount=item['amount'],
            defaults={
                'ingredient': get_object_or_404(Ingredient, pk=item['id']),
                'amount': item['amount']
            }
        )[0] for item in self.initial_data['ingredients']]
        tags = [get_object_or_404(Tag, pk=pk) for pk in
                self.initial_data['tags']]
        instance.name = self.initial_data['name']
        instance.text = self.initial_data['text']
        if image:
            instance.image = image
        instance.cooking_time = self.initial_data['cooking_time']
        instance.tags.clear()
        instance.ingredients.clear()
        instance.tags.set(tags)
        instance.ingredients.set(ingredients)
        instance.save()
        return instance

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')
