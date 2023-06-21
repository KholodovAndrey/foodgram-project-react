from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.core import exceptions
from djoser.serializers import UserCreateSerializer, UserSerializer
from recipes.models import (Top,
                            Ingredient,
                            Recipe,
                            RecipeConstructor,
                            Ingridient_list,
                            Tag)
from users.models import Follows, User


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

    def get_is_subscribed(self, obj):
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
        read_only_fields = ('name', 'color', 'slug',)


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор Ингридиентов."""

    class Meta:
        model = Ingredient
        fields = '__all__'
