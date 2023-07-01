from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from recipes.models import Tag, Ingredient
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password',)


class UserResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',)


class SetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True)
    current_password = serializers.CharField(required=True)

    def validate(self, data):
        if not self.context['user'].check_password(
                self.initial_data['current_password']):
            raise ValidationError('Invalid current password')
        return data


class TokenSerializer(serializers.Serializer):

    def validate(self, data):
        if not self.context['user'].check_password(
                self.initial_data['password']):
            raise ValidationError('Invalid current password')
        return data


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)
