from collections import OrderedDict
from django.test.utils import override_settings
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_201_CREATED, HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT
from django.contrib.auth.models import User
from todo.models import Board, Category, Column, Note
from todo.serializers import BoardSerializer, ColumnSerializer, LoginSerializers, NoteSerializer, SimpleBoardSerializer, UserSerializer


class AuthTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='testing_login@gmail.com',
            username='testing_username',
            password='passsegura'
        )

    def test_signup_created(self):
        response = self.client.post('/api/auth/signup',
                                    {'email': 'pepe@gmail.com', "username": "usname", "password": "passsegura"},
                                    'json')
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertDictContainsSubset({'email': 'pepe@gmail.com', "username": "usname"}, response.data)

    def test_signup_bad_request(self):
        response = self.client.post('/api/auth/signup', format='json')
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_signup_existing_email(self):
        response = self.client.post('/api/auth/signup', {'email': 'testing_login@gmail.com', "username": "usname", "password": "passsegura"}, format='json')
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_login_success(self):
        data = {"email": "testing_login@gmail.com", "password": "passsegura"}
        response = self.client.post('/api/auth/login', data, format='json')
        serializer = LoginSerializers(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertTrue('Token' in response.data)

    def test_login_fail(self):
        data = {"email": "testing_login@gmail.com", "password": "pashghfgh"}
        response = self.client.post('/api/auth/login', data, format='json')
        serializer = LoginSerializers(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertFalse('Token' in response.data)

    def test_session_auth(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/auth/session')
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data, {'isAuthenticated': True})

    def test_session_not_auth(self):
        response = self.client.get('/api/auth/session')
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data, {'isAuthenticated': False})

    def test_auth_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/auth/user')
        self.assertTrue(response.data.keys() >= {'id', 'username', 'email'})

    def test_auth_user_not_auth(self):
        response = self.client.get('/api/auth/user')
        self.assertEqual(response.status_code, HTTP_401_UNAUTHORIZED)

    def test_logout_ok(self):
        token = Token.objects.get_or_create(user=self.user)
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/auth/logout', **{'Authentication': 'Token '+str(token[0])})
        self.assertTrue('detail' in response.data)
        self.assertFalse(Token.objects.filter(user=self.user).exists())
        self.assertTrue(response.status_code, HTTP_200_OK)

    def test_logout_not_auth(self):
        response = self.client.post('/api/auth/logout')
        self.assertTrue(response.status_code, HTTP_200_OK)

    def test_email_exists_bad_request(self):
        response = self.client.post('/api/auth/emailexists')
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_email_exists_false(self):
        response = self.client.post('/api/auth/emailexists', {'email': 'asdasd@gmail.com'})
        self.assertDictEqual(response.data, {'exists': False})
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_email_exists_true(self):
        response = self.client.post('/api/auth/emailexists', {'email': 'testing_login@gmail.com'})
        self.assertDictEqual(response.data, {'exists': True})
        self.assertEqual(response.status_code, HTTP_200_OK)


class BoardCreateTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='testing_login@gmail.com',
            username='testing_username',
            password='passsegura'
        )
        self.board = Board.objects.create(name='boardsito', owner=self.user)
        self.client.force_authenticate(user=self.user)

    def test_create_board_ok(self):
        response = self.client.post('/api/boards', {'name': 'boardsito'}, format='json')
        self.assertTrue('name' in response.data and 'boardsito' == response.data['name'])
        self.assertTrue(Board.objects.filter(owner=self.user, name='boardsito').exists())
        self.assertEqual(response.status_code, HTTP_201_CREATED)

    def test_create_board_bad_request(self):
        response = self.client.post('/api/boards')
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)


class BoardGetByIdTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='testing_login@gmail.com',
            username='testing_username',
            password='passsegura'
        )
        self.board = Board.objects.create(name='boardsito', owner=self.user)
        self.client.force_authenticate(user=self.user)

    def test_get_board_found(self):
        response = self.client.get('/api/boards/'+str(self.board.id))
        serializer = BoardSerializer(self.board)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_get_board_not_found(self):
        response = self.client.get('/api/boards/0')
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)


class BoardDeleteByIdTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='testing_login@gmail.com',
            username='testing_username',
            password='passsegura'
        )
        self.board = Board.objects.create(name='boardsito', owner=self.user)
        self.client.force_authenticate(user=self.user)

    def test_delete_board_owner(self):
        board = Board.objects.create(name='delboard', owner=self.user)
        response = self.client.delete('/api/boards/'+str(board.id))
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)

    def test_delete_board_not_owner(self):
        board = Board.objects.create(name='delboard', owner=User.objects.create(username='pepe', email='pepe@example.com'))
        response = self.client.delete('/api/boards/'+str(board.id))
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)

    def test_delete_board_not_found(self):
        response = self.client.delete('/api/boards/0')
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)


class GuestsFromBoardTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='testing_login@gmail.com',
            username='testing_username',
            password='passsegura'
        )
        guest = User.objects.create_user(
            email='guest@gmail.com',
            username='guest_username',
            password='passsegura'
        )
        self.board: Board = Board.objects.create(name='boardsito', owner=self.user)
        self.board.guests.add(guest)
        self.client.force_authenticate(user=self.user)

    def test_guests_from_board_ok(self):
        response = self.client.get('/api/boards/'+str(self.board.id)+'/guests')
        self.assertTrue(len(response.data) == 1)
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_guests_from_board_not_found(self):
        response = self.client.get('/api/boards/0/guests')
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)


class ListBoardsFromUserTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='testing_login@gmail.com',
            username='testing_username',
            password='passsegura'
        )
        self.board: Board = Board.objects.create(name='boardsito', owner=self.user)
        self.client.force_authenticate(user=self.user)

    def test_list_ok(self):
        response = self.client.get(f'/api/users/{self.user.id}/boards')
        serializer = SimpleBoardSerializer(data=self.user.boards.all(), many=True)
        serializer.is_valid()
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_list_not_found(self):
        response = self.client.get(f'/api/users/0/boards')
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)


class ListGuestedBoardsFromUserTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='testing_login@gmail.com',
            username='testing_username',
            password='passsegura'
        )
        self.guest = User.objects.create_user(
            email='guest@gmail.com',
            username='guest_username',
            password='passsegura'
        )
        self.board: Board = Board.objects.create(name='boardsito', owner=self.user)
        self.board.guests.add(self.guest)
        self.client.force_authenticate(user=self.user)

    def test_list_ok(self):
        response = self.client.get(f'/api/users/{self.guest.id}/guest-boards')
        serializer = SimpleBoardSerializer(data=self.guest.guested_boards.all(), many=True)
        serializer.is_valid()
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_list_not_found(self):
        response = self.client.get(f'/api/users/0/guest-boards')
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)


class AddGuestToBoardTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='testing_login@gmail.com',
            username='testing_username',
            password='passsegura'
        )
        self.guest = User.objects.create_user(
            email='guest@gmail.com',
            username='guest_username',
            password='passsegura'
        )
        self.board: Board = Board.objects.create(name='boardsito', owner=self.user)
        self.client.force_authenticate(user=self.user)

    def test_create_guest_board_not_found(self):
        response = self.client.get('/api/boards/0/guests')
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)

    def test_create_guest_not_found(self):
        response = self.client.post('/api/boards/'+str(self.board.id)+'/guests', {'email': 'notfound@gmail.com'})
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)

    def test_create_guest_is_owner(self):
        response = self.client.post('/api/boards/'+str(self.board.id)+'/guests', {'email': self.user.email})
        self.assertEqual(response.status_code, HTTP_409_CONFLICT)

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.console.EmailBackend')
    def test_create_guest_ok(self):
        response = self.client.post('/api/boards/'+str(self.board.id)+'/guests', {'email': self.guest.email})
        self.assertEqual(response.data['guests'], [OrderedDict(UserSerializer(self.guest).data)])
        self.assertEqual(response.status_code, HTTP_200_OK)


class AddCategoryToBoardTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='testing_login@gmail.com',
            username='testing_username',
            password='passsegura'
        )
        self.board: Board = Board.objects.create(name='boardsito', owner=self.user)
        self.client.force_authenticate(user=self.user)

    def test_create_category_to_board_not_found(self):
        response = self.client.post('/api/boards/0/categories', data={'name': 'catee'}, format='json')
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)

    def test_create_category_to_board_not_owner(self):
        not_owner = User.objects.create_user(
            email='notowner@gmail.com',
            username='notowner',
            password='passsegura'
        )
        self.client.force_authenticate(user=not_owner)
        response = self.client.post('/api/boards/'+str(self.board.id)+'/categories', data={'name': 'catee'})
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    def test_create_category_to_board_ok(self):
        response = self.client.post('/api/boards/'+str(self.board.id)+'/categories', data={'name': 'catee'})
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(response.data.get('name'), 'catee')


class ListCategoriesFromBoardTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='testing_login@gmail.com',
            username='testing_username',
            password='passsegura'
        )
        self.board: Board = Board.objects.create(name='boardsito', owner=self.user)
        self.category = Category.objects.create(
            name='nuevacat', board=self.board
        )
        self.client.force_authenticate(user=self.user)

    def test_list_categories_ok(self):
        response = self.client.get('/api/boards/'+str(self.board.id)+'/categories')
        self.assertTrue(next((sub for sub in response.data if sub['name'] == 'nuevacat'), None) is not None)
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_list_categories_not_found(self):
        response = self.client.get('/api/boards/0/categories')
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)


class ListColumnsFromBoardTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='testing_login@gmail.com',
            username='testing_username',
            password='passsegura'
        )
        self.board: Board = Board.objects.create(name='boardsito', owner=self.user)
        self.column = Column.objects.create(
            name='nuevacol', board=self.board
        )
        self.client.force_authenticate(user=self.user)

    def test_list_columns_ok(self):
        response = self.client.get('/api/boards/'+str(self.board.id)+'/columns')
        self.assertTrue(next((sub for sub in response.data if sub['name'] == 'nuevacol'), None) is not None)
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_list_columns_not_found(self):
        response = self.client.get('/api/boards/0/columns')
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)


class CreateColumnToBoardTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='testing_login@gmail.com',
            username='testing_username',
            password='passsegura'
        )
        self.board: Board = Board.objects.create(name='boardsito', owner=self.user)
        self.client.force_authenticate(user=self.user)

    def test_create_column_board_not_found(self):
        response = self.client.post('/api/boards/'+str(self.board.id)+'/columns', {'name': 'columnita'}, format='json')
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(response.data.get('name'), 'columnita')

    def test_create_column_board_not_found(self):
        response = self.client.post('/api/boards/0/columns', {'name': 'columnita'})
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)


class RetrieveColumnFromBoardTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='testing_login@gmail.com',
            username='testing_username',
            password='passsegura'
        )
        self.board: Board = Board.objects.create(name='boardsito', owner=self.user)
        self.column = Column.objects.create(
            name='nuevacol', board=self.board
        )
        self.client.force_authenticate(user=self.user)

    def test_retrieve_column_ok(self):
        response = self.client.get('/api/boards/'+str(self.board.id)+'/columns/'+str(self.column.id))
        self.assertEqual(response.data, ColumnSerializer(self.column).data)
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_retrieve_column_ok(self):
        response = self.client.get('/api/boards/'+str(self.board.id)+'/columns/0')
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)


class UpdateColumnFromBoardTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='testing_login@gmail.com',
            username='testing_username',
            password='passsegura'
        )
        self.board: Board = Board.objects.create(name='boardsito', owner=self.user)
        self.column = Column.objects.create(
            name='nuevacol', board=self.board
        )
        self.client.force_authenticate(user=self.user)

    def test_update_column_ok(self):
        response = self.client.put('/api/boards/'+str(self.board.id)+'/columns/'+str(self.column.id),
                                   data={'name': "nuevoname"},
                                   format='json')
        self.assertEqual(response.data.get('name'), 'nuevoname')
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_update_column_not_found(self):
        response = self.client.put('/api/boards/'+str(self.board.id)+'/columns/0',
                                   data={'name': "nuevoname"})
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)

    def test_update_column_bad_request(self):
        response = self.client.put('/api/boards/'+str(self.board.id)+'/columns/'+str(self.column.id),
                                   data={'n': "nuevoname"})
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)


class DestroyColumnFromBoardTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='testing_login@gmail.com',
            username='testing_username',
            password='passsegura'
        )
        self.board: Board = Board.objects.create(name='boardsito', owner=self.user)
        self.column = Column.objects.create(
            name='nuevacol', board=self.board
        )
        self.client.force_authenticate(user=self.user)

    def test_delete_column_ok(self):
        response = self.client.delete('/api/boards/'+str(self.board.id)+'/columns/'+str(self.column.id))
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)

    def test_delete_column_not_found(self):
        response = self.client.delete('/api/boards/'+str(self.board.id)+'/columns/0')
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)


class ListNotesFromColumnTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='testing_login@gmail.com',
            username='testing_username',
            password='passsegura'
        )
        self.board: Board = Board.objects.create(name='boardsito', owner=self.user)
        self.column = Column.objects.create(
            name='nuevacol', board=self.board
        )
        cat = self.board.categories.all().first()
        self.note = Note.objects.create(name='notita', category=cat, description='descriptionlarga', column=self.column, creator=self.user)
        self.client.force_authenticate(user=self.user)

    def test_list_notes(self):
        response = self.client.get(f'/api/columns/{self.column.id}/notes')
        serializer = NoteSerializer(data=self.column.notes.all(), many=True)
        serializer.is_valid()
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_list_not_found(self):
        response = self.client.get(f'/api/columns/0/notes')
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)


class RetrieveNoteFromColumnTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='testing_login@gmail.com',
            username='testing_username',
            password='passsegura'
        )
        self.board: Board = Board.objects.create(name='boardsito', owner=self.user)
        self.column = Column.objects.create(
            name='nuevacol', board=self.board
        )
        cat = self.board.categories.all().first()
        self.note = Note.objects.create(name='notita', category=cat, description='descriptionlarga', column=self.column, creator=self.user)
        self.client.force_authenticate(user=self.user)

    def test_retrieve_note_ok(self):
        response = self.client.get(f'/api/columns/{self.column.id}/notes/{self.note.id}')
        serializer = NoteSerializer(instance=self.note, many=False)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_retrieve_note_not_found(self):
        response = self.client.get(f'/api/columns/{self.column.id}/notes/0')
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)


class CreateNoteInColumnTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='testing_login@gmail.com',
            username='testing_username',
            password='passsegura'
        )
        self.board: Board = Board.objects.create(name='boardsito', owner=self.user)
        self.column = Column.objects.create(
            name='nuevacol', board=self.board
        )
        self.client.force_authenticate(user=self.user)

    def test_create_note(self):
        cat = cat = self.board.categories.all().first()
        response = self.client.post(f'/api/columns/{self.column.id}/notes',
                                    {"name": "notita", "description": "desc", "category": cat.id},
                                    format='json')
        self.assertEqual(response.status_code, HTTP_201_CREATED)

    def test_create_note_not_found(self):
        cat = cat = self.board.categories.all().first()
        response = self.client.post(f'/api/columns/0/notes',
                                    {"name": "notita", "description": "desc", "category": cat.id},
                                    format='json')
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)


class DestroyNoteInColumnTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='testing_login@gmail.com',
            username='testing_username',
            password='passsegura'
        )
        self.board: Board = Board.objects.create(name='boardsito', owner=self.user)
        self.column = Column.objects.create(
            name='nuevacol', board=self.board
        )
        cat = self.board.categories.all().first()
        self.note = Note.objects.create(name='notita', category=cat, description='descriptionlarga', column=self.column, creator=self.user)
        self.client.force_authenticate(user=self.user)

    def test_delete_note_not_found(self):
        response = self.client.delete(f'/api/columns/{self.column.id}/notes/0')
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)

    def test_delete_note(self):
        response = self.client.delete(f'/api/columns/{self.column.id}/notes/{self.note.id}')
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)


class UpdateNoteInColumnTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='testing_login@gmail.com',
            username='testing_username',
            password='passsegura'
        )
        self.board: Board = Board.objects.create(name='boardsito', owner=self.user)
        self.column = Column.objects.create(
            name='nuevacol', board=self.board
        )
        cat = self.board.categories.all().first()
        self.note = Note.objects.create(name='notita', category=cat, description='descriptionlarga', column=self.column, creator=self.user)
        self.client.force_authenticate(user=self.user)

    def test_update_note(self):
        response = self.client.put(f'/api/columns/{self.column.id}/notes/{self.note.id}',
                                   {'name': 'newname', 'description': 'newDesc', 'category': self.note.category.id},
                                   format='json')
        self.assertEqual(response.status_code,HTTP_200_OK)

    def test_update_not_found(self):
        response = self.client.put(f'/api/columns/{self.column.id}/notes/0',
                                   {'name': 'newname', 'description': 'newDesc', 'category': self.note.category.id},
                                   format='json')
        self.assertEqual(response.status_code,HTTP_404_NOT_FOUND)

    def test_update_note_bad_request(self):
        response = self.client.put(f'/api/columns/{self.column.id}/notes/{self.note.id}',
                                   {'nae': 'newname', 'description': 'newDesc', 'category': self.note.category.id},
                                   format='json')
        self.assertEqual(response.status_code,HTTP_400_BAD_REQUEST)

class PartialUpdateNoteInColumnTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='testing_login@gmail.com',
            username='testing_username',
            password='passsegura'
        )
        self.board: Board = Board.objects.create(name='boardsito', owner=self.user)
        self.column = Column.objects.create(
            name='nuevacol', board=self.board
        )
        cat = self.board.categories.all().first()
        self.note = Note.objects.create(name='notita', category=cat, description='descriptionlarga', column=self.column, creator=self.user)
        self.client.force_authenticate(user=self.user)

    def test_update_note(self):
        aux_column=self.board.columns.all().first()
        response = self.client.patch(f'/api/columns/{self.column.id}/notes/{self.note.id}',
                                   {'column': aux_column.id},
                                   format='json')
        self.assertEqual(response.status_code,HTTP_200_OK)

    def test_update_not_found(self):
        aux_column=self.board.columns.all().first()
        response = self.client.patch(f'/api/columns/{self.column.id}/notes/0',
                                   {'column': aux_column.id},
                                   format='json')
        self.assertEqual(response.status_code,HTTP_404_NOT_FOUND)