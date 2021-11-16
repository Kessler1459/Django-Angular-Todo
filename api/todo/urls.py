from django.urls import path
from . import views

urlpatterns = [
    path('csrf', views.get_csrf),
    path('login', views.login_view),
    path('signup', views.create_user_view),
    path('logout', views.logout_view),
    path('session', views.session_view),
    path('getauthuser', views.get_auth_user_view),
    path('boards', views.create_board_view),
    path('user/<int:owner_id>/boards', views.boards_from_owner),
    path('boards/<int:board_id>/columns', views.columns_view),
    path('columns/<int:column_id>', views.edit_columns_view),
    path('columns/<int:column_id>/notes', views.notes_view),
    path('notes/<int:note_id>', views.edit_note_view)
]