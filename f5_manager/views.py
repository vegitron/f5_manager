# Create your views here.
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.conf import settings
from django.http import HttpResponseRedirect
from f5_manager.models import VirtualHost, iRule
from f5_manager.big_ip import BigIP

def home(request):
    data = {}
    data["hosts"] = []
    hosts = VirtualHost.objects.all()

    for host in hosts:
        data["hosts"].append({
            "display_name": host.display_name,
            "partition": host.partition,
            "hostname": host.hostname,
            "url": host.view_url(),
        })

    return render_to_response('hosts.html', data, RequestContext(request))

def virtualhost(request, hostname, host_id):

    if not hasattr(settings, "F5_BIGIP_HOST"):
        raise Exception("Missing required configuration key: 'F5_BIGIP_HOST'")

    host = VirtualHost.objects.get(id=host_id)
    big_ip = BigIP(host)

    enabled_rules = big_ip.get_enabled_rules()

    rules = big_ip.get_all_rules()

    all_rules = {}
    for rule in rules:
        all_rules[rule.rule_name] = rule

    current_rules = []
    other_rules = []
    admin_rules = []

    enabled_rules = sorted(enabled_rules, key=lambda rule: rule.priority)
    for rulex in enabled_rules:
        rule = rulex
        if rule.rule_name in all_rules:
            full_rule = all_rules[rule.rule_name]
            del all_rules[rule.rule_name]
            description, priority = iRule().get_description_from_definition(host, full_rule.rule_definition)
            current_rules.append({
                "rule_name": rule.rule_name,
                "priority": rule.priority,
                "description": description,
            })
        else:
            # XXX - i'm not sure if there can be rules applied to a virtualhost that would be listed.
            admin_rules.append({
                "rule_name": rule.rule_name
            })

    for rule_name in all_rules:
        rule = all_rules[rule_name]
        description, priority = iRule().get_description_from_definition(host, rule.rule_definition)

        data = {
            "rule_name": rule.rule_name,
            "description": description,
        }
        if priority != None:
            data["priority"] = priority
        other_rules.append(data)

    data = {
        "current": current_rules,
        "admin_rules": admin_rules,
        "available": other_rules,
        "host_id": host.id,
        "host_name": host.display_name,
    }


    return render_to_response('virtualhost.html', data, RequestContext(request))


def disable_rule(request):
    host = VirtualHost.objects.get(id=request.POST["host_id"])

    BigIP(host).disable_rule( request.POST["rule_name"] )

    return HttpResponseRedirect(host.view_url())

def enable_rule(request):
    host = VirtualHost.objects.get(id=request.POST["host_id"])

    new_priority = None
    if "priority" in request.POST:
        new_priority = request.POST["priority"]
    else:
        current_max = BigIP(host).get_highest_rule_priority()
        reduced = int(current_max / 10)
        new_priority = (reduced + 1) * 10

    BigIP(host).enable_rule(request.POST["rule_name"], new_priority)

    return HttpResponseRedirect(host.view_url())


def create_mapping(request, host_id):
    host = VirtualHost.objects.get(id=host_id)

    if request.method == "POST":
        url_match = request.POST["url_match"]
        pool_type = request.POST["pool_type"]

        pool = None
        if pool_type == "existing":
            pool = request.POST["server_pool"]

        else:
            hosts = request.POST.getlist("server_pool_member")
            pool = BigIP(host).create_pool_for_hosts(hosts)

        BigIP(host).create_url_map_to_pool("starts_with", url_match, pool)
        return HttpResponseRedirect(host.view_url())


    pools = BigIP(host).get_pools()
    hosts = BigIP(host).get_hosts()

    data = {
        "host_id": host.id,
        "host_name": host.display_name,
        "existing_hosts": sorted(hosts, key=lambda host: host["name"]),
        "existing_pools": sorted(pools, key=lambda pool: pool["name"]),
    }

    return render_to_response('create_mapping.html', data, RequestContext(request))

def create_offline_rule(request, host_id):
    host = VirtualHost.objects.get(id=host_id)

    if request.method == "POST":
        destination = request.POST["offline_page"]
        BigIP(host).create_offline_rule(destination)
        return HttpResponseRedirect(host.view_url())

    return render_to_response('create_offline_rule.html', {"host_id": host_id}, RequestContext(request))
