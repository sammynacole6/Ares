from django.db import models
from ares.settings import *


class Run(models.Model):
    user = models.ForeignKey('User')
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


class User(models.Model):
    name = models.CharField(max_length=255)
    numruns = models.IntegerField(default=0)
