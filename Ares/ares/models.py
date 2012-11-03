from django.db import models
from django.contrib.auth.models import User
from ares.settings import *


class Run(models.Model):
    user = models.ForeignKey('UserData')
    source = models.FilePathField(path="")
    binary = models.FilePathField(path="")

    @classmethod
    def create(cls, user):
        user.numruns += 1
        user.save()
        filename = "/".join([
            MEDIA_ROOT,
            str(user.pk),
            "%s.c" % user.numruns
        ])
        binname = "/".join([
            MEDIA_ROOT,
            str(user.pk),
            "%s" % user.numruns
        ])
        return cls(user=user, source=filename, binary=binname)


class UserData(models.Model):
    user = models.ForeignKey(User, primary_key=True)
    numruns = models.IntegerField(default=0)


class Project(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey('UserData')


class File(models.Model):
    name = models.CharField(max_length=255)
    last_seen_open = models.DateTimeField(blank=True, null=True)
    project = models.ForeignKey('Project')
