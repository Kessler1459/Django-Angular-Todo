from django.urls import include, path
from django.urls.conf import re_path
from django.views.generic.base import RedirectView
from rest_framework.routers import DefaultRouter
from rest_framework.authentication import TokenAuthentication
from rest_framework_nested.routers import NestedDefaultRouter
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from .views import (
    BoardViewSet, ColumnViewSet, CategoryViewSet, GuestViewSet, UserGuestedBoards,
    NoteViewSet, permissions, Signup, LoginAPIView, Session,
    AuthUser, Logout, Email, UserBoards
)

router = DefaultRouter(trailing_slash=False)
router.register(r'boards', BoardViewSet, basename='boards')
router.register(r'columns', ColumnViewSet, basename='columns')
boards_router = NestedDefaultRouter(router, r'boards', lookup='board')
columns_router = NestedDefaultRouter(router, r'columns', lookup='column')
boards_router.register(r'columns', ColumnViewSet, basename='columns')
boards_router.register(r'categories', CategoryViewSet, basename='categories')
boards_router.register(r'guests', GuestViewSet, basename='guests')
columns_router.register(r'notes', NoteViewSet, basename='notes')

schema_view = get_schema_view(
    openapi.Info(
        title="TODO API",
        default_version='v1',
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
    authentication_classes=[TokenAuthentication]
)

urlpatterns = [
    re_path(r'swagger', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path(r'', include(router.urls)),
    path(r'', include(boards_router.urls)),
    path(r'', include(columns_router.urls)),
    path('auth', RedirectView.as_view(url='auth/login', permanent=True)),
    path('auth/signup', Signup.as_view()),
    path('auth/login', LoginAPIView.as_view()),
    path('auth/session', Session.as_view()),
    path('auth/user', AuthUser.as_view()),
    path('auth/logout', Logout.as_view()),
    path('auth/emailexists', Email.as_view()),
    path('users/<int:id>/boards', UserBoards.as_view()),
    path('users/<int:id>/guest-boards', UserGuestedBoards.as_view())
]
