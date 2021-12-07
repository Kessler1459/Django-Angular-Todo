from typing import OrderedDict
from django.db.models.fields import CharField
from django.utils.translation.trans_null import _
from rest_framework import authentication, serializers
from django.contrib.auth.models import User
from rest_framework.fields import EmailField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.validators import UniqueValidator
from todo.models import Board, Category, Column, Note

class UserSerializer(serializers.ModelSerializer):
    username =CharField()
    password=serializers.CharField(write_only=True)
    email = serializers.EmailField(validators=[UniqueValidator(queryset=User.objects.all())])
    class Meta:
        model=User
        fields=['id','username','email','password']
    

class LoginSerializers(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=128, write_only=True)    
    def validate(self, data:OrderedDict):
        email = data.get('email',None)
        password = data.get('password',None)
        if email and password:
            user=User.objects.filter(email=email).first()
            user = authentication.authenticate(username=user.username if user is not None else "", password=password)
            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "username" and "password".')
            raise serializers.ValidationError(msg, code='authorization')
        data['user'] = user
        return data
    
class EmailSerializer(serializers.ModelSerializer):
    email=EmailField()
    class Meta:
        model=User
        fields=['email']
    
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model= Category
        fields=['id','name']  

class NoteInputSerializer(serializers.ModelSerializer):
    category=PrimaryKeyRelatedField(queryset=Category.objects.all())
    class Meta:
        model= Note
        fields=['id','name','category','description','column']  

class NoteSerializer(serializers.ModelSerializer):
    creator=UserSerializer(many=False,required=False)
    category=CategorySerializer(many=False)
    class Meta:
        model= Note
        fields=['id','name','creator','category','datetime','description']  
    
class ColumnSerializer(serializers.ModelSerializer):
    notes=NoteSerializer(many=True,required=False)
    class Meta:
        model= Column
        fields=['id','name','notes']    

class BoardSerializer(serializers.ModelSerializer):
    columns=ColumnSerializer(many=True,required=False)
    owner=UserSerializer(many=False,required=False)
    categories=CategorySerializer(many=True,required=False)
    guests=UserSerializer(many=True,required=False)
    
    class Meta:
        model=Board
        fields=['id','name','owner','columns','categories','guests']   
    

class SimpleBoardSerializer(serializers.ModelSerializer):    
    class Meta:
        model=Board
        fields=['id','name']   
    
