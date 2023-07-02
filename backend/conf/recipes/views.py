import os

from django.db.models import Value, Count, F, Sum
from django.db.models.functions import Concat
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, permissions
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination

from rest_framework.response import Response

from conf.settings import BASE_DIR
from recipes.filters import IngredientFilter
from recipes.models import (Tag, Ingredient, Subscription, Recipe, Favourite,
                            ShoppingCard)
from recipes.permissions import TokenAuthPermission, UserAuthPermission, \
    RecipePermission
from users.models import User
from recipes.serializers import (UserSerializer, UserResponseSerializer,
                                 SetPasswordSerializer, TokenSerializer,
                                 TagSerializer, IngredientSerializer,
                                 UserResponseWithRecipesSerializer,
                                 RecipeSerializer, RecipeResponseSerializer,
                                 UserResponseWithRecipesForPostSerializer,
                                 UserResponseWithRecipesForDeleteSerializer,
                                 RecipeFavouritePostSerializer,
                                 RecipeFavouriteDelteSerializer,
                                 RecipeShoppingCardPostSerializer,
                                 RecipeShoppingCardDeleteSerializer, )


class UserViewSet(viewsets.ModelViewSet):
    pagination_class = PageNumberPagination
    queryset = User.objects.all()
    serializer_class = UserResponseSerializer
    permission_classes = [UserAuthPermission, ]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context

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
        Subscription.objects.create(user=user)
        ShoppingCard.objects.create(user=user)
        return Response(UserResponseSerializer(user, context={
            'request': request
        }).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get', ])
    def me(self, request):
        return Response(
            UserResponseSerializer(request.user, context={
                'request': request
            }, many=False).data,
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

    @action(detail=False, methods=['get', ])
    def subscriptions(self, request):
        subscription = Subscription.objects.get(user=request.user)
        subscription_list_pk = subscription.subscriptions.all().values_list(
            'pk', flat=True)
        users = User.objects.annotate(is_subscribed=Value(True),
                                      recipes_count=Count('recipe')).filter(
            id__in=subscription_list_pk
        )
        paginator = self.pagination_class()
        return paginator.get_paginated_response(
            UserResponseWithRecipesSerializer(paginator.paginate_queryset(
                users, request), many=True).data)

    @action(detail=True, methods=['post', 'delete'])
    def subscribe(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        user.is_subscribed = True
        user.recipes_count = user.recipe_set.all().count()
        subscribe = get_object_or_404(Subscription, user=request.user)
        if request.method == 'POST':
            serializer = UserResponseWithRecipesForPostSerializer(
                data=request.data,
                context={
                    'user': user,
                    'current_user': request.user,
                    'subscribe': subscribe,
                })
            serializer.is_valid(raise_exception=True)
            subscribe.subscriptions.add(user)
            return Response(UserResponseWithRecipesSerializer(
                user, many=False
            ).data, status=status.HTTP_201_CREATED)
        else:
            serializer = UserResponseWithRecipesForDeleteSerializer(
                data=request.data,
                context={
                    'user': user,
                    'subscribe': subscribe,
                })
            serializer.is_valid(raise_exception=True)
            subscribe.subscriptions.remove(user)
            return Response(status=status.HTTP_204_NO_CONTENT)


class TokenViewSet(viewsets.ViewSet):
    permission_classes = [TokenAuthPermission, ]

    @action(detail=False, methods=['post', ])
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

    @action(detail=False, methods=['post', ])
    def logout(self, request):
        get_object_or_404(Token, user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    pagination_class = PageNumberPagination
    queryset = Recipe.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,
                          RecipePermission]
    serializer_class = RecipeResponseSerializer

    def get_queryset(self):
        request = self.request
        queryset = Recipe.objects.all()
        if request.query_params.get('is_favorited') == 1:
            recipe_pk_list = Favourite.objects.filter(
                user=request.user).values_list('recipe_id', flat=True)
            queryset = queryset.filter(pk__in=recipe_pk_list)
        if request.query_params.get('is_in_shopping_cart') == 1:
            recipe_pk_list = ShoppingCard.objects.get(
                user=request.user).recipes.all().values_list('pk', flat=True)
            queryset = queryset.filter(pk__in=recipe_pk_list)
        if request.query_params.get('author'):
            queryset = queryset.filter(
                author=get_object_or_404(User,
                                         pk=request.query_params['author']))
        if request.query_params.get('tags'):
            queryset = queryset.filter(
                tags__in=request.query_params.getlist('tags'))
        return queryset

    @action(detail=False, methods=['get'],
            permission_classes=[RecipePermission])
    def download_shopping_cart(self, request):
        shopping_carts = ShoppingCard.objects.get(user=request.user)
        spisok = shopping_carts.recipes.values(
            name_measurement_unit=Concat(
                F('ingredients__ingredient__name'),
                Value(' ('),
                F('ingredients__ingredient__measurement_unit'),
                Value(')'))
        ).annotate(amount=Sum('ingredients__amount')).values(
            'name_measurement_unit', 'amount')
        data = {item['name_measurement_unit']: item['amount']
                for item in spisok if bool(item['amount'])}
        path = f'{str(BASE_DIR)}/shopping_list'
        if not os.path.exists(path):
            os.makedirs(path)
        file_shopping_carts = open(
            f'{path}\\shoppinglist{request.user.id}.txt', 'w+'
        )
        for key, value in data.items():
            file_shopping_carts.write(f'{key} -- {value}\n')
        file_shopping_carts.close()
        return HttpResponse(
            open(f'{path}\\shoppinglist{request.user.id}.txt'),
            content_type='text/plain'
        )

    @action(detail=True, methods=['post', 'delete'])
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        shopping_card = get_object_or_404(ShoppingCard, user=request.user)
        if request.method == 'POST':
            serializer = RecipeShoppingCardPostSerializer(
                data=request.data,
                context={
                    'recipe': recipe,
                    'shopping_card': shopping_card
                }
            )
            serializer.is_valid(raise_exception=True)
            shopping_card.recipes.add(recipe)
            return Response(RecipeSerializer(recipe, many=False).data,
                            status=status.HTTP_201_CREATED)
        else:
            serializer = RecipeShoppingCardDeleteSerializer(
                data=request.data,
                context={
                    'recipe': recipe,
                    'shopping_card': shopping_card
                }
            )
            serializer.is_valid(raise_exception=True)
            shopping_card.recipes.remove(recipe)
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        favourite = Favourite.objects.filter(user=request.user,
                                             recipe=recipe)
        if request.method == 'POST':
            serializer = RecipeFavouritePostSerializer(
                data=request.data,
                context={
                    'favourite': favourite
                }
            )
            serializer.is_valid(raise_exception=True)
            Favourite.objects.create(user=request.user, recipe=recipe)
            return Response(RecipeSerializer(recipe, many=False).data,
                            status=status.HTTP_201_CREATED)
        else:
            serializer = RecipeFavouriteDelteSerializer(
                data=request.data,
                context={
                    'favourite': favourite
                }
            )
            serializer.is_valid(raise_exception=True)
            favourite.first().delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
