from django.urls import path
from . import views

urlpatterns = [
    path('auth/csrf', views.get_csrf),
    path('auth/login', views.login_view),
    path('auth/signup', views.create_user_view),
    path('auth/logout', views.logout_view),
    path('auth/session', views.session_view),
    path('auth/getauthuser', views.get_auth_user_view),
    path('auth/emailexists', views.email_exists_view),
    path('boards', views.create_board_view),
    path('boards/<int:id>', views.get_full_board),
    path('boards/<int:id>/guests', views.board_guests),
    path('boards/<int:id>/categories', views.get_board_categories),
    path('boards/guests/<int:guest_id>', views.boards_from_guest),
    path('boards/<int:board_id>/columns', views.columns_view),
    path('user/<int:owner_id>/boards', views.boards_from_owner),
    path('columns/<int:column_id>', views.edit_columns_view),
    path('columns/<int:column_id>/notes', views.notes_view),
    path('notes/<int:note_id>', views.edit_note_view),
    path('notes/<int:note_id>/column',views.change_note_column)
]