from datetime import datetime as dt
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from djoser.serializers import SetPasswordSerializer

from django.conf import settings

from recipes.models import (Top, Ingredient, Recipe,
                            RecipeConstructor, Ingridient_list, Tag)
from users.models import Subscriptions, User
from .serializers import UserCreateSerializer
from .filters import RecipeFilter, IngredientSearchFilter
from .permissions import IsAuthorOrReadOnly
from .pagination import CustomPaginator
from .serializers import (IngredientSerializer, RecipeCreateSerializer,
                          RecipeShowSerializer, RecipeSerializer,
                          FollowedSerializer, TagsSerializer,
                          UserShowSerializer)


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    pagination_class = CustomPaginator

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return UserShowSerializer
        return UserCreateSerializer

    @action(detail=False,
            methods=['get'],
            pagination_class=None,
            permission_classes=(IsAuthenticated,)
            )
    def me(self, request):
        serializer = UserShowSerializer(request.user)
        return Response(serializer.data,
                        status=status.HTTP_200_OK)

    @action(["post"], detail=False)
    def set_password(self, request, *args, **kwargs):
        user = self.request.user
        serializer = SetPasswordSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user.set_password(serializer.validated_data["new_password"])
            user.save()
            return Response({"status": "password set"})
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False,
            methods=['get'],
            permission_classes=(IsAuthenticated,),
            pagination_class=CustomPaginator
            )
    def subscriptions(self, request):
        queryset = User.objects.filter(subscribing__user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = FollowedSerializer(page,
                                        many=True,
                                        context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,)
            )
    def subscribe(self, request, **kwargs):
        author = get_object_or_404(User, id=kwargs['pk'])

        if request.method == 'POST':
            serializer = FollowedSerializer(author,
                                            data=request.data,
                                            context={"request": request})
            serializer.is_valid(raise_exception=True)
            Subscriptions.objects.create(user=request.user, author=author)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            get_object_or_404(Subscriptions, user=request.user,
                              author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny, )
    serializer_class = TagsSerializer
    pagination_class = None
    queryset = Tag.objects.all()


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (AllowAny, )
    filter_backends = (IngredientSearchFilter, )
    search_fields = ('^name', )


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = CustomPaginator
    permission_classes = (IsAuthorOrReadOnly, )
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeShowSerializer
        return RecipeCreateSerializer

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,)
            )
    def favorite(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        if request.method == 'POST':
            serializer = RecipeSerializer(recipe,
                                          data=request.data,
                                          context={"request": request})
            serializer.is_valid(raise_exception=True)
            if not Top.objects.filter(user=request.user,
                                      recipe=recipe).exists():
                Top.objects.create(user=request.user, recipe=recipe)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'DELETE':
            get_object_or_404(Top, user=request.user,
                              recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,),
            pagination_class=None
            )
    def shopping_cart(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        if request.method == 'POST':
            serializer = RecipeSerializer(recipe,
                                          data=request.data,
                                          context={"request": request})
            serializer.is_valid(raise_exception=True)
            if not Ingridient_list.objects.filter(user=request.user,
                                                  recipe=recipe).exists():
                Ingridient_list.objects.create(user=request.user,
                                               recipe=recipe)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'DELETE':
            get_object_or_404(Ingridient_list, user=request.user,
                              recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False,
            methods=['get'],
            permission_classes=(IsAuthenticated,)
            )
    def download_shopping_cart(self, request, **kwargs):
        user = request.user
        shopping_list = [
            f'Список покупок для: {user}\n'
            f'{dt.now().strftime(settings.DATE_TIME_FORMAT)}\n'
        ]
        ingredients = (
            RecipeConstructor.objects
            .filter(recipe__shopping_recipe__user=user)
            .values('ingredient')
            .annotate(total_amount=Sum('amount'))
            .values_list('ingredient__name', 'total_amount',
                         'ingredient__measurement_unit')
        )
        [shopping_list.append(
            '* {} - {} {}.'.format(*ingredient)) for ingredient in ingredients]
        response = HttpResponse('\n'.join(shopping_list),
                                content_type="text/plain")
        return response
