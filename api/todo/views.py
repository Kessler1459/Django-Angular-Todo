from django.contrib.auth import login
from django.contrib.auth.models import User, update_last_login
from django.core.validators import EmailValidator
from rest_framework import  permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView, ListAPIView, get_object_or_404
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin,DestroyModelMixin
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from todo.mailer import sendEmail
from todo.models import *
from todo.permissions import IsOwner
from todo.serializers import *
from todo.validations import ConflictError
from drf_yasg.utils import swagger_auto_schema

# ------------AUTH-----------------------------------------------------------------------------

class Signup(CreateAPIView):
    model = User
    permission_classes = [permissions.AllowAny]
    serializer_class = UserSerializer
    @swagger_auto_schema(request_body=UserSerializer,security=[])
    def post(self, request:Request):
        return super().post(self,request)
        

class LoginAPIView(APIView):
    permission_classes=[permissions.AllowAny]
    serializer_class=LoginSerializers
    @swagger_auto_schema(request_body=LoginSerializers,security=[])
    def post(self, request:Request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        update_last_login(None, user)
        token = Token.objects.get_or_create(user=user)
        login(request,user)
        return Response({"status": status.HTTP_200_OK, "Token": token[0].key})

class Session(APIView):
    permission_classes=[permissions.AllowAny]
    @swagger_auto_schema()
    def get(self,request):
        return Response({'isAuthenticated': request.user.is_authenticated})

class AuthUser(APIView):
    def get(self,request):
        serializer=UserSerializer(request.user)
        return Response(serializer.data)

class Logout(APIView):
    def post(self,request: Request):  
        request.user.auth_token.delete()
        return Response({'detail': 'Successfully logged out.'}) 

class Email(APIView):
    permission_classes=[permissions.AllowAny]
    @swagger_auto_schema(request_body=EmailSerializer,security=[])
    def post(self,request:Request):
        if 'email' not in request.data:
            raise ValidationError({'email':'Email required'})
        exists = User.objects.filter(email=request.data['email']).exists()
        return Response({'exists': str(exists).lower()})
           
# ----------------BOARD---------------------
class BoardViewSet(GenericViewSet,RetrieveModelMixin,CreateModelMixin,DestroyModelMixin):
    serializer_class=BoardSerializer
    def get_permissions(self):
        if self.action=='destroy': 
            return [IsOwner()]
        else: 
            return super().get_permissions()
    def get_queryset(self):
        return (Board.objects.filter(owner=self.request.user.id)|(Board.objects.filter(guests=self.request.user.id))).distinct()
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    
class GuestViewSet(GenericViewSet,ListModelMixin,CreateModelMixin):
    serializer_class=UserSerializer
    permission_classes=[IsOwner]
    def get_queryset(self):
        board=self.get_object()
        return board.guests
    def get_object(self):
        board=get_object_or_404(Board,id=self.kwargs.get('board_pk'))
        self.check_object_permissions(self.request, board)
        return board
    def create(self, request, *args, **kwargs):
        board=self.get_object()
        email=EmailValidator(request.data['email'])
        guest=get_object_or_404(User,email=email.message)
        if guest ==request.user: raise ConflictError("You can't be your own guest")
        board.guests.add(guest)
        sendEmail('Added as guest in board '+board.name+' by '+board.owner.username,email.message)
        return Response(BoardSerializer(board).data)

class CategoryViewSet(GenericViewSet,ListModelMixin,CreateModelMixin):
    serializer_class=CategorySerializer
    permission_classes=[IsOwner]
    def get_object(self):
        board=get_object_or_404(Board,id=self.kwargs.get('board_pk'))
        self.check_object_permissions(self.request, board)
        return board
    def get_queryset(self):
        return Category.objects.filter(board=self.get_object()) 
    def perform_create(self, serializer):
        serializer.save(board=self.get_object())
        
class ColumnViewSet(ModelViewSet):
    serializer_class=ColumnSerializer
    def get_queryset(self):
        return Column.objects.filter(board_id=self.kwargs.get('board_pk')) 
    def perform_create(self, serializer):
        serializer.save(board_id=self.kwargs.get('board_pk'))

class UserBoards(ListAPIView):
    serializer_class=SimpleBoardSerializer
    def get_queryset(self):
        return Board.objects.filter(owner_id=self.kwargs.get('id'))
    
class UserGuestedBoards(ListAPIView):
    serializer_class=SimpleBoardSerializer
    def get_queryset(self):
        return Board.objects.filter(guests=self.kwargs.get('id'))
    
# ----------------NOTES--------------------------------------------------

class NoteViewSet(ModelViewSet):
    def get_serializer_class(self):
        if self.action in ['create','update','partial_update']:
            return NoteInputSerializer
        else:
            return NoteSerializer
    def get_queryset(self):
        return Note.objects.filter(column_id=self.kwargs.get('column_pk'))
    def perform_create(self, serializer):
        serializer.save(creator=self.request.user,column=get_object_or_404(Column,id=self.kwargs.get('column_pk')))
