from django.http import HttpResponse
import subprocess
from django.shortcuts import render_to_response
import os

from ares.models import *


def index(request):
    if request.method == 'POST':
        user = 1  # TODO: actually get the user
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

        try:
            c = subprocess.check_output(['gcc', '-Wall', '-ansi', '-o', r.binary, r.source], stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            return HttpResponse(status=412, content=e.output)

        try:
            c = subprocess.check_output([r.binary], stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            os.remove(r.binary)
            c = e.output
        os.remove(r.binary)
        return HttpResponse(content=c)
    else:
        return render_to_response('index.html', mimetype='text/html')

# everything below this line will become a static serve file, but that's in the future.
def js(request):
    return render_to_response('index.js', mimetype='text/javascript')


def css(request):
    return render_to_response('index.css', mimetype='text/css')
