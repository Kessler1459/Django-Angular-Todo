from django.db import models
from django.contrib.auth.models import User
from django.db.models.deletion import CASCADE
from django.utils.translation import gettext_lazy as _

# Create your models here.

class Board(models.Model):
    name = models.CharField(max_length=20, blank=False)
    owner = models.ForeignKey(User,on_delete=CASCADE)



class Column(models.Model):
    name = models.CharField(max_length=30, blank=False)
    board = models.ForeignKey(Board, on_delete=CASCADE)


class Note(models.Model):
    class State(models.TextChoices):
        TODO = 'FR', _('To do')
        INPROGRESS = 'IP', _('In progress')
        DONE = 'DN', _('Done')

    state = models.CharField(
        max_length=2,
        choices=State.choices,
        default=State.TODO,
    )
    name = models.CharField(max_length=70, blank=False)
    description = models.CharField(max_length=300)


class Category(models.Model):
    name = models.CharField(max_length=30, blank=False)
    board = models.ForeignKey(Board,on_delete=CASCADE)
    note = models.ManyToManyField(Note)
