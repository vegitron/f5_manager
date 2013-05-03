from django.template.loader import get_template
from django.template import Context
from f5_manager.big_ip import BigIP

def redirect_view(url):
    template = get_template('irules/redirect.html')
    return template.render(Context({ "url": url }))


def outside_rule_view(definition):
    template = get_template('irules/outside_rule.html')
    return template.render(Context({ "definition": definition }))


def pool_mapping_view(host, action, url_match, pool_name):
    template = get_template('irules/pool_mapping.html')

    hosts = BigIP(host).get_hosts_for_pool(pool_name)

    return template.render(Context({ "action": action, "url_match": url_match, "pool_name": pool_name, "hosts": sorted(hosts, key=lambda host: host["address"])}))

def client_ssl_cert_view(action, url_match, header):
    template = get_template('irules/client_ssl_cert.html')
    return template.render(Context({ "action": action, "url_match": url_match, "header": header }))

