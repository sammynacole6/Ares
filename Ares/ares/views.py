from django.http import HttpResponse
import subprocess
from django.shortcuts import render_to_response
import os
from django.template import RequestContext
from django.core.context_processors import csrf

from ares.command import *
from ares.models import *


def clean_output(path, output):
    return output.replace(path, 'Ares')


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
    else:
        return render_to_response('index.html', mimetype='text/html', context_instance=RequestContext(request))

# everything below this line will become a static serve file, but that's in the future.


def js(request):
    return render_to_response('index.js', mimetype='text/javascript', context_instance=RequestContext(request))


def css(request):
    return render_to_response('index.css', mimetype='text/css', context_instance=RequestContext(request))


def js_layout(request):
    return render_to_response('jquery.layout-latest.min.js', mimetype='text/javascript', context_instance=RequestContext(request))
