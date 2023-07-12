import io

from django.db.models import Value, Count, F, Sum
from django.db.models.functions import Concat
from django.http import HttpResponse

from django_filters import rest_framework
from rest_framework import viewsets, status, permissions
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from recipes.filters import IngredientFilter, RecipeFilter
from recipes.models import (Tag, Ingredient, Subscription, Recipe, Favourite,
                            ShoppingCard)
from recipes.permissions import (RecipePermission)
from users.models import User
from recipes.serializers import (UserSerializer, UserResponseSerializer,
                                 SetPasswordSerializer, TokenSerializer,
                                 TagSerializer, IngredientSerializer,
                                 UserResponseWithRecipesSerializer,
                                 RecipeSerializer, RecipeResponseSerializer,
                                 UserResponseWithRecipesWithValidateSerializer,
                                 RecipeFavouriteSerializer,
                                 RecipeShoppingCardSerializer,
                                 RecipeResponsePostUpdateSerializer, )


class UserViewSet(viewsets.ModelViewSet):
    pagination_class = PageNumberPagination
    queryset = User.objects.all()
    serializer_class = UserResponseSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context

    def retrieve(self, request, *args, **kwargs):
        self.permission_classes = [permissions.IsAuthenticated]
        super().check_permissions(request)
        return super().retrieve(request, *args, **kwargs)

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
        ShoppingCard.objects.create(user=user)
        return Response(UserResponseSerializer(user, context={
            'request': request
        }).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get', ])
    def me(self, request):
        self.permission_classes = [permissions.IsAuthenticated]
        super().check_permissions(request)
        return Response(
            UserResponseSerializer(request.user, context={
                'request': request
            }, many=False).data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['post', ])
    def set_password(self, request):
        self.permission_classes = [permissions.IsAuthenticated]
        super().check_permissions(request)
        serializer = SetPasswordSerializer(data=request.data, context={
            'user': request.user
        })
        serializer.is_valid(raise_exception=True)
        request.user.set_password(request.data['new_password'])
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get', ])
    def subscriptions(self, request):
        self.permission_classes = [permissions.IsAuthenticated]
        super().check_permissions(request)
        subscription = Subscription.objects.filter(user=request.user)
        users = User.objects.annotate(is_subscribed=Value(True),
                                      recipes_count=Count(
                                          'recipe_set')).filter(
            id__in=subscription.values_list(
                'subscriptions__id', flat=True
            )
        )
        paginator = self.pagination_class()
        return paginator.get_paginated_response(
            UserResponseWithRecipesSerializer(paginator.paginate_queryset(
                users, request), many=True, context={
                'recipes_limit': request.query_params.get('recipes_limit')
            }).data)

    @action(detail=True, methods=['post', 'delete'])
    def subscribe(self, request, pk):
        self.permission_classes = [permissions.IsAuthenticated]
        super().check_permissions(request)
        user = get_object_or_404(User, pk=pk)
        user.is_subscribed = True
        user.recipes_count = user.recipe_set.all().count()
        serializer = UserResponseWithRecipesWithValidateSerializer(
            data=request.data,
            context={
                'user': user,
                'current_user': request.user,
                'method': request.method,
            })
        serializer.is_valid(raise_exception=True)
        if request.method == 'POST':
            Subscription.objects.create(
                user=request.user,
                subscriptions=user
            )
            return Response(UserResponseWithRecipesSerializer(
                user, many=False
            ).data, status=status.HTTP_201_CREATED)
        else:
            Subscription.objects.get(
                user=request.user,
                subscriptions=user
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class TokenViewSet(viewsets.ViewSet):

    @action(detail=False, methods=['post', ])
    def login(self, request):
        serializer = TokenSerializer(data=request.data, )
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(User, email=request.data.get('email'))
        token, created = Token.objects.get_or_create(user=user)
        return Response(
            {'auth_token': token.key},
            status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=['post', ])
    def logout(self, request):
        self.permission_classes = [permissions.IsAuthenticated]
        super().check_permissions(request)
        get_object_or_404(Token, user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [rest_framework.DjangoFilterBackend, ]
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    pagination_class = PageNumberPagination
    queryset = Recipe.objects.all().order_by('-id')
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,
                          RecipePermission]
    serializer_class = RecipeResponseSerializer
    filter_backends = [rest_framework.DjangoFilterBackend]
    filterset_class = RecipeFilter

    # def list(self, request, *args, **kwargs):
    #     if not self.request.query_params.get('tags'):
    #         self.queryset = Recipe.objects.none()
    #     return super().list(request,*args,**kwargs)

    def create(self, request, *args, **kwargs):
        serializer = RecipeResponsePostUpdateSerializer(
            data=request.data,
            context={
                'request': request
            }
        )
        serializer.is_valid(raise_exception=True)
        self.serializer_class = RecipeResponseSerializer
        instance = serializer.save()
        serializer_result = self.get_serializer(instance)
        return Response(serializer_result.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk, *args, **kwargs):
        instance = self.get_object()
        serializer = RecipeResponsePostUpdateSerializer(instance,
                                                        data=request.data)
        serializer.is_valid(raise_exception=True)
        self.serializer_class = RecipeResponseSerializer
        instance = serializer.save()
        serializer_result = self.get_serializer(instance)
        return Response(serializer_result.data)

    @action(detail=False, methods=['get'])
    def download_shopping_cart(self, request):
        self.permission_classes = [permissions.IsAuthenticated]
        super().check_permissions(request)
        shopping_carts = ShoppingCard.objects.get(user=request.user)
        spisok = shopping_carts.recipes.values(
            name_measurement_unit=Concat(
                F('ingredients__name'),
                Value(' ('),
                F('ingredients__measurement_unit'),
                Value(')'))
        ).annotate(amount=Sum('ingredientwithquantity_set__amount')).values(
            'name_measurement_unit', 'amount')
        data = {item['name_measurement_unit']: item['amount']
                for item in spisok if bool(item['amount'])}
        buffer = io.BytesIO()
        with io.TextIOWrapper(
                buffer, encoding="utf-8", write_through=True
        ) as file:
            for key, value in data.items():
                file.write(f"{key} - {value}\n")
            response = HttpResponse(
                buffer.getvalue(),
                content_type="text/plain"
            )
            response[
                "Content-Disposition"
            ] = "attachment; filename=user-shopping-ingredients.txt"
            return response

    @action(detail=True, methods=['post', 'delete'])
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        shopping_card = get_object_or_404(ShoppingCard, user=request.user)
        serializer = RecipeShoppingCardSerializer(
            data=request.data,
            context={
                'recipe': recipe,
                'shopping_card': shopping_card,
                'method': request.method
            }
        )
        serializer.is_valid(raise_exception=True)
        if request.method == 'POST':
            shopping_card.recipes.add(recipe)
            return Response(RecipeSerializer(recipe, many=False).data,
                            status=status.HTTP_201_CREATED)
        else:
            shopping_card.recipes.remove(recipe)
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        favourite = Favourite.objects.filter(user=request.user,
                                             recipe=recipe)
        serializer = RecipeFavouriteSerializer(
            data=request.data,
            context={
                'favourite': favourite,
                'method': request.method
            }
        )
        serializer.is_valid(raise_exception=True)
        if request.method == 'POST':
            Favourite.objects.create(user=request.user, recipe=recipe)
            return Response(RecipeSerializer(recipe, many=False).data,
                            status=status.HTTP_201_CREATED)
        else:
            favourite.first().delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
