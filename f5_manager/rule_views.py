from django.template.loader import get_template
from django.template import Context

def redirect_view(url):
    template = get_template('irules/redirect.html')
    return template.render(Context({ "url": url }))


def outside_rule_view(definition):
    template = get_template('irules/outside_rule.html')
    return template.render(Context({ "definition": definition }))


def pool_mapping_view(action, url_match, pool_name):
    template = get_template('irules/pool_mapping.html')
    return template.render(Context({ "action": action, "url_match": url_match, "pool_name": pool_name}))

def client_ssl_cert_view(action, url_match, header):
    template = get_template('irules/client_ssl_cert.html')
    return template.render(Context({ "action": action, "url_match": url_match, "header": header }))

