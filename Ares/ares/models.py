from django.db import models
from django.contrib.auth.models import User
from ares.settings import *

import os


class Project(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User)


class File(models.Model):

    @classmethod
    def create(cls, name, project):
        filename = MEDIA_ROOT + '/' + str(project.user.pk) + '/' + str(project.pk) + '/' + name
        book = cls(name=filename, basename=name, project=project)
        directory = os.path.dirname(filename)
        if not os.path.exists(directory):
            os.makedirs(directory)
        open(filename, 'w')
        return book

    name = models.CharField(max_length=255)
    basename = models.CharField(max_length=255)
    project = models.ForeignKey('Project')
    last_seen_open = models.DateTimeField(blank=True, null=True)
    last_opened_by = models.CharField(blank=True, null=True, max_length=32)  # md5 hash
