from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CategoryViewSet, CommentViewSet, GenreViewSet,
                    ReviewViewSet, TitlesViewSet, UsersViewSet,
                    get_confirmation_code, get_jwt_token)

router = DefaultRouter()
router.register(r'users', UsersViewSet, basename='users')
router.register(r'titles', TitlesViewSet, basename="titles")
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'genres', GenreViewSet, basename='genre')
router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)

app_name = 'api'

auth_patterns = [
    path('signup/', get_confirmation_code),
    path('token/', get_jwt_token)
]

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/', include(auth_patterns)),
    path('v1/', include('djoser.urls')),
]
