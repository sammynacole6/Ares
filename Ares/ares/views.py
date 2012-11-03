from django.http import HttpResponse
from django.http import HttpResponseForbidden
from django.http import HttpResponseRedirect

import subprocess
import os

from django.shortcuts import render_to_response
from django.template import RequestContext

from django.contrib import auth

from ares.command import *
from ares.models import *


def user_auth(request, user):
    return request.user.is_authenticated() and str(request.user.pk) == user


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


def projectselect(request, user):
    if not user_auth(request, user):
        return HttpResponseForbidden(content="User not authenticated")
    if request.method == 'POST':
        Project(name=request.POST['projectname'], user=UserData.objects.get(user=user)).save()
    user, created = UserData.objects.get_or_create(user=User.objects.get(pk=user))
    return render_to_response('projectselect.html', {'user': user, 'projects': Project.objects.filter(user=user)}, context_instance=RequestContext(request))


def project(request, user, project):
    if not user_auth(request, user):
        return HttpResponseForbidden(content="User not authenticated")
    if request.method == 'GET':
        return render_to_response('index.html', {'files': File.objects.filter(project=project)}, context_instance=RequestContext(request))
    else:
        if request.POST['mode'] == 'new':
            File(name=request.POST['filename'], project=Project.objects.get(pk=project)).save()
            return HttpResponse(status=200, content='File created')


def file(request, user, project, file):
    valid = user_auth(request, user) and file.project == project and project.user == user
    if not valid:
        return HttpResponseForbidden(content="Something went wrong retrieving your file")
    f = open(user + '/' + project + '/' + file, 'r')
    return HttpResponse(status=200, content=f.read(), mimetype='text')


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
