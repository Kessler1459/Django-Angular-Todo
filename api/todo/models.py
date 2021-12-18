from django.db import models
from django.contrib.auth.models import User
from django.db.models.deletion import CASCADE
from django.utils.translation import gettext_lazy as _

# Create your models here.


class Board(models.Model):
    name = models.CharField(max_length=20, blank=False)
    owner = models.ForeignKey(User, on_delete=CASCADE, related_name="boards")
    guests = models.ManyToManyField(User, related_name="guested_boards")

    def save(self, *args, **kwargs):
        new = self.pk is None
        super(Board, self).save(*args, **kwargs)
        if new:
            column = Column(board=self, name="To do")
            column.save()
            Category.objects.create(name="Task", board=self)

    def to_dict(self):
        dict = {
            'id': self.id, 'name': self.name,
            'owner':
                {'id': self.owner.id, 'username': self.owner.username,'email': self.owner.email},
            'guests': [],
            'categories': [],
            'columns': []
        }
        for guest in self.guests.all():
            dict['guests'].append(
                {"id": guest.id, "username": guest.username, "email": guest.email})
        for category in self.categories.all():
            dict['categories'].append(category.to_dict())
        for column in self.columns.all():
            dict['columns'].append(column.to_dict())
        return dict


class Column(models.Model):
    name = models.CharField(max_length=30, blank=False)
    board = models.ForeignKey(Board, on_delete=CASCADE, related_name="columns")

    def to_dict(self):
        dict = {'id': self.id, 'name': self.name, 'notes': []}
        for note in self.notes.all():
            dict['notes'].append(note.to_dict())
        return dict


class Category(models.Model):
    name = models.CharField(max_length=30, blank=False)
    board = models.ForeignKey(Board, on_delete=CASCADE,related_name="categories")

    def to_dict(self):
        return {'id': self.id, 'name': self.name}


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
    column = models.ForeignKey(Column, on_delete=CASCADE, null=True,related_name='notes')
    category = models.ForeignKey(Category, on_delete=CASCADE, null=True)
    creator = models.ForeignKey(User, on_delete=CASCADE, null=True)
    datetime = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.category is None:
            self.category = Category.objects.filter(name="Task", board=self.column.board).first()
        super(Note, self).save(*args, **kwargs)

    def to_dict(self):
        return {'id': self.id, 'name': self.name,'state':self.state, 'description': self.description,'datetime':self.datetime, 'category': self.category.to_dict(),
                'creator': {'id': self.creator.id, 'username': self.creator.username, 'email': self.creator.email}
                }
