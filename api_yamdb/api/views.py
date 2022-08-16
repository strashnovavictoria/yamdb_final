from api.exceptions import UserValueException
from api.permisions import IsAdmin, IsAdminOrReadOnly, ReviewCommentPermission
from api.serializers import (CategoryReadSerializer, CategorySerializer,
                             CommentSerializer, ConfirmationSerializer,
                             GenreSerializer, ReviewSerializer,
                             TitlePostSerializer, TitleSerializer,
                             TokenSerializer, UsersSerializer)
from api_yamdb.settings import DEFAULT_FROM_EMAIL
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from reviews.models import Category, Genre, Review, Title, User

from .filters import TitlesFilter


@api_view(["POST"])
@permission_classes([AllowAny])
def get_confirmation_code(request):
    serializer = ConfirmationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.data.get("email")
    username = serializer.data.get("username")
    user, created = User.objects.get_or_create(username=username, email=email)
    if not created:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    confirmation_code = default_token_generator.make_token(user)
    mail_subject = "Подтверждение доступа на api_yamdb"
    message = f"Ваш код подтверждения: {confirmation_code}"
    send_mail(mail_subject, message, DEFAULT_FROM_EMAIL, [email],
              fail_silently=False)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([AllowAny])
def get_jwt_token(request):
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(User, username=serializer.data.get("username"))
    if not user:
        raise UserValueException("Ошибка имени пользователя")
    confirmation_code = serializer.data.get("confirmation_code")
    if not default_token_generator.check_token(user, confirmation_code):
        return Response(
            {"Код введен неверно. Повторите попытку."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    refresh = RefreshToken.for_user(user)
    return Response({"access": str(refresh.access_token)},
                    status=status.HTTP_200_OK)


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    lookup_field = "username"
    permission_classes = (IsAdmin,)
    pagination_class = PageNumberPagination

    @action(
        detail=False, methods=["get", "patch"],
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        user = request.user
        if request.method == "GET":
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(role=user.role, partial=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (ReviewCommentPermission,)
    pagination_class = PageNumberPagination

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get("title_id"))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get("title_id"))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (ReviewCommentPermission,)
    pagination_class = PageNumberPagination

    def get_queryset(self):
        review = get_object_or_404(
            Review, id=self.kwargs.get("review_id"),
            title=self.kwargs.get("title_id")
        )
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(Review, pk=self.kwargs.get("review_id"))
        serializer.save(title=review.title, review=review,
                        author=self.request.user)


class TitlesViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all().annotate(rating=Avg("reviews__score"))
    serializer_class = TitleSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = TitlesFilter
    ordering = "name"

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return TitleSerializer
        return TitlePostSerializer


class DestroyCreateViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    pass


class CategoryViewSet(DestroyCreateViewSet):
    queryset = Category.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)
    lookup_field = "slug"

    def get_serializer_class(self):
        if self.action == "list":
            return CategoryReadSerializer
        return CategorySerializer


class GenreViewSet(DestroyCreateViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)
    lookup_field = "slug"
