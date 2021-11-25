from django.http.response import HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotFound
from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_http_methods
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.core import serializers
import json
from todo.mailer import sendEmail
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
    new_user = User.objects.create_user(username=req['username'], email=req['email'], password=req['password'])
    return JsonResponse({'id':new_user.id,'username': new_user.username, 'email': new_user.email}, status=201)

# header X-CSRFToken


@csrf_exempt
@require_http_methods(['POST'])
def login_view(request: HttpRequest):
    req = json.loads(request.body)
    # ta cochino pero quiero logear con mail
    user = User.objects.filter(email=req['email']).first()
    user = authenticate(request, username=user.username, password=req['password'])
    if user is None:
        return JsonResponse({'detail': 'Invalid credentials.'}, status=401)
    login(request, user)
    token = get_token(request)
    response = JsonResponse({'email': user.email, 'username': user.username, 'id': user.id})
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
    return JsonResponse({'username': request.user.username, 'email': request.user.email, 'id': request.user.id})

@csrf_exempt
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
    new_board: Board = Board.objects.create(owner=user, name=req['name'])
    return JsonResponse(new_board.to_dict(), status=201)


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
    return JsonResponse(list(boards.values("id", "name")), safe=False, status=status)


@require_http_methods(['GET', 'DELETE'])
def get_full_board(request: HttpRequest, id: int):
    board: Board = Board.objects.filter(id=id).first()
    if board is None:
        return HttpResponseNotFound()
    else:
        is_guest = Board.objects.filter(id=board.id, guests__exact=request.user).exists()
        if request.method == 'GET':
            if request.user.id != board.owner.id and not is_guest:
                return HttpResponseForbidden()
            return JsonResponse(board.to_dict(), safe=False)
        elif request.method == 'DELETE':
            if request.user.id != board.owner.id:
                return HttpResponseForbidden()
            board.delete()
            return JsonResponse({'detail': 'Board deleted'}, status=200)


@require_http_methods(['GET', 'POST'])
def board_guests(request: HttpRequest, id: int):
    board: Board = Board.objects.filter(id=id).first()
    if board is None:
        return HttpResponseNotFound()
    elif request.user.id != board.owner.id:
        return HttpResponseForbidden()
    else:
        if request.method == 'GET':
            dict = []
            guests = board.guests.all()
            for guest in guests:
                dict.append({"id": guest.id, "username": guest.username, "email": guest.email})
            status = 200 if board.guests.count() > 0 else 204
            return JsonResponse(dict, status=status, safe=False)
        elif request.method == 'POST':
            guest_email = json.loads(request.body)['email']
            guest: User = User.objects.filter(email=guest_email).first()
            if request.user==guest:     #que no se agregue a si mismo
                return HttpResponseBadRequest()
            board.guests.add(guest)
            sendEmail('Added as guest in board '+board.name+' by '+board.owner.username,guest_email)
            return JsonResponse({"id": guest.id, "username": guest.username, "email": guest.email}, status=200)


@require_http_methods(['GET','POST'])
def get_board_categories(request: HttpRequest, id: int):
    board: Board = Board.objects.filter(id=id).first()
    if board is None:
        return HttpResponseNotFound()
    elif request.user.id != board.owner.id:
        return HttpResponseForbidden()
    else:
        if request.method=='GET':
            dict = []
            categories: list[Category] = board.categories.all()
            for cat in categories:
                dict.append(cat.to_dict())
            status = 200 if categories.count() > 0 else 204
            return JsonResponse(dict, status=status, safe=False)
        elif request.method=='POST':
            newCat: Category= Category.objects.create(name=json.loads(request.body)['name'],board=board)
            return JsonResponse(newCat.to_dict(),status=200)
        
# ----------------COLUMNS--------------------------------------------------


@require_http_methods(['POST', 'GET'])
def columns_view(request: HttpRequest, board_id: int):
    board = Board.objects.filter(id=board_id).first()
    if board is None:
        return HttpResponseNotFound()
    else:
        is_guest = Board.objects.filter(id=board.id, guests__exact=request.user).exists()
        if request.user.id != board.owner.id and not is_guest:
            return HttpResponseForbidden()
        else:
            if request.method == 'POST':
                req = json.loads(request.body)
                newCol: Column = Column.objects.create(name=req['name'], board=board)
                return JsonResponse(newCol.to_dict(), status=201)
            elif request.method == 'GET':
                columns = Column.objects.filter(board=board)
                status = 200 if columns.count() > 0 else 204
                return JsonResponse(list(columns.values("id", "name")), safe=False, status=status)


@require_http_methods(['PUT', 'DELETE'])
def edit_columns_view(request: HttpRequest, column_id: int):
    column: Column = Column.objects.filter(id=column_id).first()
    if column is None:
        return HttpResponseNotFound()
    else:
        is_guest = Board.objects.filter(id=column.board.id, guests__exact=request.user).exists()
        if request.user.id != column.board.owner.id and not is_guest:
            return HttpResponseForbidden()
        else:
            if request.method == 'PUT':
                req = json.loads(request.body)
                column.name = req['name']
                column = column.save()
                return JsonResponse(column.to_dict(), status=200)
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
        is_guest = Board.objects.filter(id=column.board.id, guests__exact=request.user).exists()
        if not is_guest and request.user.id != column.board.owner.id:
            return HttpResponseForbidden()
        else:
            if request.method == 'POST':
                req = json.loads(request.body)
                category = Category.objects.filter(id=req['category']).first()
                note: Note = Note.objects.create(name=req['name'], description=req['description'], category=category, column=column, creator=request.user)
                return JsonResponse(note.to_dict(), status=201)
            elif request.method == 'GET':
                notes = Note.objects.filter(column=column)
                status = 200 if notes.count() > 0 else 204
                return JsonResponse(list(notes.values("id", "name", "state", "description", "category", "column")), safe=False, status=status)


@require_http_methods(['PUT', 'DELETE'])
def edit_note_view(request: HttpRequest, note_id: int):
    note: Note = Note.objects.filter(id=note_id).first()
    if note is None:
        return HttpResponseNotFound()
    else:
        user = request.user
        is_guest = Board.objects.filter(id=note.column.board.id, guests__exact=user).exists()
        if not is_guest and user.id != note.column.board.owner.id:
            return HttpResponseForbidden()
        else:
            if request.method == 'PUT':
                req = json.loads(request.body)
                note.name = req['name']
                note.description = req['description']
                note.state = req['state']
                note.category = Category.objects.filter(id=req['category']['id']).first()
                note.save()
                return JsonResponse(note.to_dict(), status=200)
            elif request.method == 'DELETE':
                note.delete()
                return JsonResponse({'detail': 'Note deleted'}, status=200)


def change_note_column(request: HttpRequest, note_id: int):
    note: Note = Note.objects.filter(id=note_id).first()
    if note is None:
        return HttpResponseNotFound()
    else:
        user = request.user
        is_guest = Board.objects.filter(id=note.column.board.id, guests__exact=user).exists()
        if not is_guest and user.id != note.column.board.owner.id:
            return HttpResponseForbidden()
        else:
            new_col = json.loads(request.body)['column']
            column: Column = note.column if new_col == note.column.id else Column.objects.filter(id=new_col).first()
            note.column = column
            note.save()
            return JsonResponse({'column':"Column changed"}, status=200)
