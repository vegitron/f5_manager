# Create your views here.
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.conf import settings
from django.http import HttpResponseRedirect
from f5_manager.models import VirtualHost, iRule

# F5 SOAP interface
import pycontrol

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

    return render_to_response('hosts.html', data, RequestContext(request))

def virtualhost(request, hostname, host_id):

    if not hasattr(settings, "F5_BIGIP_HOST"):
        raise Exception("Missing required configuration key: 'F5_BIGIP_HOST'")

    host = VirtualHost.objects.get(id=host_id)
    big_ip = pycontrol.BIGIP(
        hostname = settings.F5_BIGIP_HOST,
        username = host.admin_user,
        password = host.admin_pass,
        fromurl = True,
        wsdls = ['LocalLB.Rule', 'LocalLB.VirtualServer', 'Management.Partition']
    )

    if host.partition:
        big_ip.Management.Partition.set_active_partition(host.partition)

    enabled_rules = big_ip.LocalLB.VirtualServer.get_rule(["/%s/%s" % (host.partition, host.hostname)])[0]

    rules = big_ip.LocalLB.Rule.query_all_rules()

    all_rules = {}
    for rule in rules:
        all_rules[rule.rule_name] = rule

    current_rules = []
    other_rules = []
    admin_rules = []

    for rulex in enabled_rules:
        rule = rulex
        if rule.rule_name in all_rules:
            full_rule = all_rules[rule.rule_name]
            del all_rules[rule.rule_name]
            current_rules.append({
                "rule_name": rule.rule_name,
                "priority": rule.priority,
                "description": iRule().get_description_from_definition(full_rule.rule_definition),
            })
        else:
            # XXX - i'm not sure if there can be rules applied to a virtualhost that would be listed.
            admin_rules.append({
                "rule_name": rule.rule_name
            })

    for rule_name in all_rules:
        rule = all_rules[rule_name]
        other_rules.append({
            "rule_name": rule.rule_name,
            "description": iRule().get_description_from_definition(rule.rule_definition),
        })

    return render_to_response('virtualhost.html', { "current": current_rules, "admin_rules": admin_rules, "available": other_rules, "host_id": host.id }, RequestContext(request))



def disable_rule(request):
    host = VirtualHost.objects.get(id=request.POST["host_id"])
    big_ip = pycontrol.BIGIP(
        hostname = settings.F5_BIGIP_HOST,
        username = host.admin_user,
        password = host.admin_pass,
        fromurl = True,
        wsdls = ['LocalLB.Rule', 'LocalLB.VirtualServer']
    )

    rule_set = big_ip.LocalLB.VirtualServer.typefactory.create('LocalLB.VirtualServer.VirtualServerRule')
    rule_set.rule_name = request.POST["rule_name"]
    rule_set.priority = 1

    rule_seq = big_ip.LocalLB.VirtualServer.typefactory.create('LocalLB.VirtualServer.VirtualServerRuleSequence')

    rule_seq.item = [rule_set]

    big_ip.LocalLB.VirtualServer.remove_rule(["/%s/%s" % (host.partition, host.hostname)], [[rule_seq]])

    return HttpResponseRedirect(host.view_url())

def enable_rule(request):
    host = VirtualHost.objects.get(id=request.POST["host_id"])
    big_ip = pycontrol.BIGIP(
        hostname = settings.F5_BIGIP_HOST,
        username = host.admin_user,
        password = host.admin_pass,
        fromurl = True,
        wsdls = ['LocalLB.Rule', 'LocalLB.VirtualServer']
    )

    rule_set = big_ip.LocalLB.VirtualServer.typefactory.create('LocalLB.VirtualServer.VirtualServerRule')
    rule_set.rule_name = request.POST["rule_name"]
    rule_set.priority = 1 # XXX - make this come in, configurable

    rule_seq = big_ip.LocalLB.VirtualServer.typefactory.create('LocalLB.VirtualServer.VirtualServerRuleSequence')

    rule_seq.item = [rule_set]

    big_ip.LocalLB.VirtualServer.add_rule(["/%s/%s" % (host.partition, host.hostname)], [[rule_seq]])

    return HttpResponseRedirect(host.view_url())


