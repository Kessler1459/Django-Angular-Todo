from django.db import models
from django.contrib.auth.models import User
from django.db.models.deletion import CASCADE
from django.utils.translation import gettext_lazy as _

# Create your models here.


class Board(models.Model):
    name = models.CharField(max_length=20, blank=False)
    owner = models.ForeignKey(User, on_delete=CASCADE, related_name="boards")
    guests = models.ManyToManyField(User)
    def save(self, *args, **kwargs):
        new = self.pk is None
        super(Board, self).save(*args, **kwargs)
        if new:
            column = Column(board=self, name="To do")
            column.save()


class Column(models.Model):
    name = models.CharField(max_length=30, blank=False)
    board = models.ForeignKey(Board, on_delete=CASCADE, related_name="columns")


class Category(models.Model):
    name = models.CharField(max_length=30, blank=False)
    board = models.ForeignKey(Board, on_delete=CASCADE,
                              related_name="categories")


class Note(models.Model):
    class State(models.TextChoices):
        TODO = 'TD', _('To do')
        INPROGRESS = 'IP', _('In progress')
        DONE = 'DN', _('Done')

    state = models.CharField(
        max_length=2,
        choices=State.choices,
        default=State.TODO,
    )
    name = models.CharField(max_length=70, blank=False)
    description = models.CharField(max_length=300)
    column = models.ForeignKey(Column, on_delete=CASCADE, null=True)
    category = models.ForeignKey(Category, on_delete=CASCADE, null=True)
    creator = models.ForeignKey(User,on_delete=CASCADE, null=True)

    def save(self, *args, **kwargs):
        if self.category is None:
            self.category=Category.objects.get_or_create(name="Task", board=self.column.board)[0]
        super(Note, self).save(*args, **kwargs)
            
