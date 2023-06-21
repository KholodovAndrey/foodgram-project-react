from django.db.transaction import atomic
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers, exceptions, status
from rest_framework.validators import UniqueValidator
from djoser.serializers import UserCreateSerializer, UserSerializer
from recipes.models import (Ingredient,
                            Recipe,
                            RecipeConstructor,
                            Tag)
from users.models import Follows, User
from drf_extra_fields.fields import Base64ImageField


class UserSerializer(UserSerializer):
    """Сериализатор пользователя."""

    is_folowed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'is_folowed'
        )

    def get_is_follower(self, obj):
        if (self.context.get('request')
           and not self.context['request'].user.is_anonymous):
            return Follows.objects.filter(
                                        user=self.context['request'].user,
                                        author=obj
                                    ).exists()
        return False


class UserCreateSerializer(UserCreateSerializer):
    """Сериализатор создания пользователя."""

    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())])
    username = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all())])

    class Meta:
        model = User
        fields = (
            'id',
            'password',
            'username',
            'email',
            'first_name',
            'last_name'
        )


class UserShowSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed')

    def get_is_subscribed(self, obj):
        if (self.context.get('request')
           and not self.context['request'].user.is_anonymous):
            return Follows.objects.filter(user=self.context['request'].user,
                                          author=obj).exists()
        return False


class SetPasswordSerializer(serializers.Serializer):
    """Сериализатор смены пароля."""

    new_pass = serializers.CharField(required=True)
    current_pass = serializers.CharField(required=True)

    def validate(self, obj):
        try:
            validate_password(obj['new_password'])
        except exceptions.ValidationError as e:
            raise serializers.ValidationError(
                {'new_password': list(e.messages)}
            )
        return super().validate(obj)

    class Meta:
        model = User
        fields = "__all__"


class TagsSerializer(serializers.ModelSerializer):
    """Сериализатор Тэгов."""

    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ('name',
                            'color',
                            'slug',)


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(read_only=True)
    read_only_fields = ('name', 'cooking_time')

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class FollowedSerializer(serializers.ModelSerializer):
    """Сериализатор подписки."""
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    read_only_fields = ('username', 'email')

    class Meta:
        model = User
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'is_followed',
                  'recipes',
                  'recipes_count')

    def validate(self, data):
        author = self.instance
        user = self.context.get('request').user
        if Follows.objects.filter(user=user, author=author).exists():
            raise exceptions.ValidationError(
                detail='Уже подписаны!',
                code=status.HTTP_400_BAD_REQUEST
            )
        if user == author:
            raise exceptions.ValidationError(
                detail='Нельзя подписаться на самого себя!',
                code=status.HTTP_400_BAD_REQUEST
            )
        return data

    def get_is_followed(self, obj):
        return (
            self.context.get('request').user.is_authenticated
            and Follows.objects.filter(user=self.context['request'].user,
                                       author=obj).exists()
        )

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор конструктора рецептов."""

    read_only_fields = ('ingredient.id',
                        'ingredient.name',
                        'ingredient.measurement_unit',)

    class Meta:
        model = RecipeConstructor
        fields = ('id',
                  'name',
                  'measurement_unit',
                  'amount')


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания ингридиента."""

    id = serializers.IntegerField()

    class Meta:
        model = RecipeConstructor
        fields = ('id',
                  'amount')


class RecipeShowSerializer(serializers.ModelSerializer):
    """Сериализатор отображения рецепта."""

    author = UserShowSerializer(read_only=True)
    tags = TagsSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientSerializer(
                                   many=True,
                                   read_only=True,
                                   source='recipes'
                                )

    image = Base64ImageField(read_only=True)

    class Meta:
        model = Recipe
        exclude = ('pub_date')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор Ингридиентов."""

    class Meta:
        model = Ingredient
        fields = '__all__'
        read_only_fields = ('name', 'measurement_unit',)


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания рецептов."""
    image = Base64ImageField()
    author = UserShowSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(many=True,
                                              queryset=Tag.objects.all())
    ingredients = RecipeIngredientCreateSerializer(many=True)

    class Meta:
        model = Recipe
        exclude = ('pub_date')

    def create_ingredients(self, recipe, ingredients):
        RecipeConstructor.objects.bulk_create(
            [RecipeConstructor(
                recipe=recipe,
                ingredient=Ingredient.objects.get(pk=ingredient['id']),
                amount=ingredient['amount']
            ) for ingredient in ingredients]
        )

    @atomic
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=self.context['request'].user,
                                       **validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)
        return recipe

    @atomic
    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.create_ingredients(recipe=instance, ingredients=ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeShowSerializer(instance,
                                    context=self.context).data