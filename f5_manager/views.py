# Create your views here.
from django.shortcuts import render_to_response
from f5_manager.models import VirtualHost

def home(request):
    data = {}
    data["hosts"] = []
    hosts = VirtualHost.objects.all()

    for host in hosts:
        data["hosts"].append({
            "partition": host.partition,
            "hostname": host.hostname,
            "url": host.view_url(),
        })

    return render_to_response('hosts.html', data)

def virtualhost(request, hostname, host_id):
    return render_to_response('virtualhost.html')

