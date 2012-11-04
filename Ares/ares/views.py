from django.http import HttpResponse
from django.http import HttpResponseForbidden
from django.http import HttpResponseRedirect

import subprocess
import os

from django.shortcuts import render_to_response
from django.template import RequestContext

from django.contrib.auth.models import User
from django.contrib import auth

from django.utils import timezone

from ares.command import *
from ares.models import *

import datetime


def user_auth(request, user):
    return request.user.is_authenticated() and request.user == user


def clean_output(path, output):
    return output.replace(path, 'Ares')


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if user is not None and user.is_active:
            auth.login(request, user)
            return HttpResponseRedirect("./" + str(user.pk))
        else:
            return render_to_response("login.html", {'retry': True}, context_instance=RequestContext(request))
    else:
        return render_to_response("login.html", {'retry': False}, context_instance=RequestContext(request))


def projectselect(request, user_id):
    user = User.objects.get(pk=user_id)
    if not user_auth(request, user):
        return HttpResponseForbidden(content="User not authorized")
    if request.method == 'POST':
        Project(name=request.POST['projectname'], user=User.objects.get(pk=user_id)).save()
    return render_to_response('projectselect.html', {'user': user, 'projects': Project.objects.filter(user=user)}, context_instance=RequestContext(request))


def project(request, user_id, project_id):
    user = User.objects.get(pk=user_id)
    project = Project.objects.get(pk=project_id)

    valid = user_auth(request, user) and project.user == user

    if not valid:
        return HttpResponseForbidden(content="User not authenticated")
    if request.method == 'GET':
        return render_to_response('index.html', {'files': File.objects.filter(project=project)}, context_instance=RequestContext(request))
    else:
        if request.POST['mode'] == 'new':
            File.create(name=request.POST['filename'], project=project).save()
        elif request.POST['mode'] == 'delete':
            File.objects.filter(project=project).filter(pk=request.POST['file']).delete()
        return render_to_response('filelist.html', {'files': File.objects.filter(project=project)})


def file(request, user_id, project_id, file_id):
    user = User.objects.get(pk=user_id)
    project = Project.objects.get(pk=project_id)
    file = File.objects.get(pk=file_id)

    valid = user_auth(request, user) and file.project == project and project.user == user
    if not valid:
        return HttpResponseForbidden(content="Something went wrong retrieving your file")
    f = open(file.name, 'r')
    return HttpResponse(status=200, content=f.read(), mimetype='text/data')


def ding(request, user_id, project_id, file_id):
    user = User.objects.get(pk=user_id)
    project = Project.objects.get(pk=project_id)
    file = File.objects.get(pk=file_id)

    valid = user_auth(request, user) and file.project == project and project.user == user
    if not valid:
        return HttpResponseForbidden(content="User not authenticated")

    session_key = request.session.session_key

    can_claim = file.last_seen_open == None or timezone.now() - file.last_seen_open > datetime.timedelta(seconds=4)
    is_mine = file.last_opened_by == session_key
    is_iffy = timezone.now() - file.last_seen_open < datetime.timedelta(seconds=1)

    if is_iffy:
        return HttpResponse(status=409, content="File is iffy")

    if can_claim or is_mine:
        file.last_opened_by = session_key
        file.last_seen_open = timezone.now()
        file.save()
        return HttpResponse(status=200, content="File ding'd")

    else:
        return HttpResponse(status=409, content="File claimed by someone else")


def file_status(request, user_id, project_id, file_id):
    user = User.objects.get(pk=user_id)
    project = Project.objects.get(pk=project_id)
    file = File.objects.get(pk=file_id)

    valid = user_auth(request, user) and file.project == project and project.user == user
    if not valid:
        return HttpResponse(content="ui-icon-circle-close")

    is_mine = file.last_opened_by == request.session.session_key

    # Usually an open file is dinged every 2 seconds. if a file is dinged twice in this period, it is likely 
    # someone using the same session has the file open. (or we have some serious lag?)
    can_claim = file.last_seen_open == None or timezone.now() - file.last_seen_open > datetime.timedelta(seconds=4)
    
    if is_mine or can_claim:
        return HttpResponse(content="ui-icon-check")
    else:
        return HttpResponse(content="ui-icon-alert")


def run(request, user, project):
    if not user_auth(request, user):
        return HttpResponseForbidden(content="User not authenticated")
    u = User.objects.get(pk=user)

    r = Run.create(user=u)
    r.save()

    directory = os.path.dirname(r.source)
    if not os.path.exists(directory):
        os.makedirs(directory)

    cmd = request.POST['cmd']
    f = open(r.source, 'w')
    f.write(cmd)
    f.close()

    inp = request.POST['input']
    f = open(r.binary + '.in', 'w')
    f.write(inp)
    f.close()

    comp = ''
    try:
        command = Command(['gcc', '-Wall', '-ansi', '-o', r.binary, r.source])
        comp += command.run(timeout=3)
    except subprocess.CalledProcessError as e:
        comp += e.output
        comp = clean_output(r.binary, comp)
        return render_to_response('results.html', {'compilation': comp})

    comp = clean_output(r.binary, comp)

    run = ''
    try:
        command = Command([r.binary], inputfile=r.binary + '.in')
        run += command.run(timeout=3)
    except subprocess.CalledProcessError as e:
        run += e.output
    except ValueError as e:
        run += e.strerror
    if(os.path.exists(r.binary)):
        os.remove(r.binary)

    run = clean_output(r.binary, run)
    return render_to_response('results.html', {'compilation': comp, 'run': run})
