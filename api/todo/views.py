from django.http.response import HttpResponseForbidden, HttpResponseNotFound
from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_http_methods
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
import json
from todo.models import *
# Create your views here.

# ------------AUTH-----------------------------------------------------------------------------


def get_csrf(request):
    response = JsonResponse({'detail': 'CSRF cookie set'})
    response['X-CSRFToken'] = get_token(request)
    return response


@csrf_exempt
@require_http_methods(['POST'])
def create_user_view(request: HttpRequest):
    req = json.loads(request.body)
    new_user = User.objects.create_user(
        username=req['username'], email=req['email'], password=req['password'])
    return JsonResponse({'username': new_user.username, 'email': new_user.email}, status=201)

# header X-CSRFToken


@csrf_exempt
@require_http_methods(['POST'])
def login_view(request: HttpRequest):
    req = json.loads(request.body)
    user =User.objects.filter(email=req['email']).first() #ta cochino pero quiero logear con mail
    user = authenticate(
        request, username=user.username, password=req['password'])
    if user is None:
        return JsonResponse({'detail': 'Invalid credentials.'}, status=401)
    login(request, user)
    token = get_token(request)
    response = JsonResponse(
        {'email': user.email,'username':user.username,'id':user.id})
    response['X-CSRFToken'] = token
    return response


@require_http_methods(['POST'])
def logout_view(request: HttpRequest):
    if not request.user.is_authenticated:
        return JsonResponse({'detail': 'You\'re not logged in.'}, status=400)
    logout(request)
    return JsonResponse({'detail': 'Successfully logged out.'})


def session_view(request: HttpRequest):
    if not request.user.is_authenticated:
        return JsonResponse({'isAuthenticated': False})
    return JsonResponse({'isAuthenticated': True})


def get_auth_user_view(request: HttpRequest):
    if not request.user.is_authenticated:
        return JsonResponse({'isAuthenticated': False})
    return JsonResponse({'username': request.user.username})


@require_http_methods(['POST'])
def email_exists_view(request: HttpRequest):
    exists = User.objects.filter(
        email=json.loads(request.body)['email']).exists()
    return JsonResponse({'exists': str(exists).lower()})

# ----------------BOARD---------------------


@require_http_methods(['POST'])
def create_board_view(request: HttpRequest):
    req = json.loads(request.body)
    user = request.user
    new_board = Board(owner=user, name=req['name'])
    new_board.save()
    return JsonResponse({'detail': 'Board created'}, status=201)


@require_http_methods(['GET'])
def boards_from_owner(request: HttpRequest, owner_id: int):
    user = request.user
    if user.id != owner_id:
        return HttpResponseForbidden()
    boards = Board.objects.filter(owner=user)
    status = 200 if boards.count() > 0 else 204
    return JsonResponse(list(boards.values("id", "name", "owner")), safe=False, status=status)

@require_http_methods(['GET'])
def boards_from_guest(request: HttpRequest, guest_id: int):
    user = request.user
    if user.id != guest_id:
        return HttpResponseForbidden()
    boards = Board.objects.filter(guests=user)
    status = 200 if boards.count() > 0 else 204
    return JsonResponse(list(boards.values("id", "name", "owner")), safe=False, status=status)


# ----------------COLUMNS--------------------------------------------------

@require_http_methods(['POST', 'GET'])
def columns_view(request: HttpRequest, board_id: int):
    board = Board.objects.filter(id=board_id).first()
    if board is None:
        return HttpResponseNotFound()
    else:
        is_guest = Board.objects.filter(
            id=board.id, guests__exact=request.user).exists()
        if request.user.id != board.owner.id and not is_guest:
            return HttpResponseForbidden()
        else:
            if request.method == 'POST':
                req = json.loads(request.body)
                Column.objects.create(name=req['name'], board=board)
                return JsonResponse({'detail': 'Column created'}, status=201)
            elif request.method == 'GET':
                columns = Column.objects.filter(board=board)
                status = 200 if columns.count() > 0 else 204
                return JsonResponse(list(columns.values("id", "name")), safe=False, status=status)


@require_http_methods(['PUT', 'DELETE'])
def edit_columns_view(request: HttpRequest, column_id: int):
    column = Column.objects.filter(id=column_id).first()
    if column is None:
        return HttpResponseNotFound()
    else:
        is_guest = Board.objects.filter(
            id=column.board.id, guests__exact=request.user).exists()
        if request.user.id != column.board.owner.id and not is_guest:
            return HttpResponseForbidden()
        else:
            if request.method == 'PUT':
                req = json.loads(request.body)
                column.name = req['name']
                column.save()
                return JsonResponse({'id': column.id, 'name': column.name}, status=200)
            elif request.method == 'DELETE':
                column.delete()
                return JsonResponse({'detail': 'Column deleted'}, status=200)


# ----------------NOTES--------------------------------------------------
@require_http_methods(['POST', 'GET'])
def notes_view(request: HttpRequest, column_id: int):
    column = Column.objects.filter(id=column_id).first()
    if column is None:
        return HttpResponseNotFound()
    else:
        is_guest = Board.objects.filter(
            id=column.board.id, guests__exact=request.user).exists()
        if not is_guest and request.user.id == column.board.owner.id:
            return HttpResponseForbidden()
        else:
            if request.method == 'POST':
                req = json.loads(request.body)
                note = Note(name=req['name'],
                            description=req['description'], column=column, creator=request.user)
                note.save()
                return JsonResponse({'detail': 'Note created'}, status=201)
            elif request.method == 'GET':
                notes = Note.objects.filter(column=column)
                status = 200 if notes.count() > 0 else 204
                return JsonResponse(list(notes.values("id", "name", "state", "description", "category", "column")), safe=False, status=status)


@require_http_methods(['PUT', 'DELETE'])
def edit_note_view(request: HttpRequest, note_id: int):
    note = Note.objects.filter(id=note_id).first()
    if note is None:
        return HttpResponseNotFound()
    else:
        user = request.user
        is_guest = Board.objects.filter(
            id=note.column.board.id, guests__exact=user).exists()
        if not is_guest and user.id == note.column.board.owner.id:
            return HttpResponseForbidden()
        else:
            if request.method == 'PUT':
                req = json.loads(request.body)
                column = note.column if req['column'] == note.column.id else Column.objects.get(
                    id=req['column'])
                note.name = req['name']
                note.description = req['description']
                note.state = req['state']
                note.column = column
                note.save()
                return JsonResponse({'id': note.id, 'name': note.name, 'description': note.description, 'column': note.column.id, 'state': note.state, 'creator': note.creator.id}, status=200)
            elif request.method == 'DELETE':
                note.delete()
                return JsonResponse({'detail': 'Note deleted'}, status=200)
