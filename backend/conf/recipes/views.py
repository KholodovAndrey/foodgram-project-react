from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, permissions
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination

from rest_framework.response import Response

from recipes.filters import IngredientFilter
from recipes.models import Tag, Ingredient
from recipes.permissions import TokenAuthPermission, UserAuthPermission
from users.models import User
from recipes.serializers import (UserSerializer, UserResponseSerializer,
                                 SetPasswordSerializer, TokenSerializer,
                                 TagSerializer, IngredientSerializer)


class UserViewSet(viewsets.ModelViewSet):
    pagination_class = PageNumberPagination
    queryset = User.objects.all()
    serializer_class = UserResponseSerializer
    permission_classes = [UserAuthPermission, ]

    def create(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.create_user(
            username=request.data['username'],
            first_name=request.data['first_name'],
            last_name=request.data['last_name'],
            password=request.data['password'],
            email=request.data['email'],
        )
        Token.objects.create(user=user)
        return Response(UserResponseSerializer(user).data,
                        status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get', ])
    def me(self, request):
        return Response(
            UserResponseSerializer(request.user, many=False).data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['post', ])
    def set_password(self, request):
        serializer = SetPasswordSerializer(data=request.data, context={
            'user': request.user
        })
        serializer.is_valid(raise_exception=True)
        request.user.set_password(request.data['new_password'])
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TokenViewSet(viewsets.ViewSet):
    permission_classes = [TokenAuthPermission, ]

    @action(detail=False, methods=['POST', ])
    def login(self, request):
        user = get_object_or_404(User, email=request.data['email'])
        serializer = TokenSerializer(data=request.data, context={
            'user': user
        })
        serializer.is_valid(raise_exception=True)
        token, created = Token.objects.get_or_create(user=user)
        return Response(
            {'auth_token': token.key},
            status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=['POST', ])
    def logout(self, request):
        get_object_or_404(Token, user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [DjangoFilterBackend,]
    filterset_class = IngredientFilter
