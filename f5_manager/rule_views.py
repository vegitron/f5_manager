from django.template.loader import get_template
from django.template import Context

def redirect_view(url):
    template = get_template('irules/redirect.html')
    return template.render(Context({ "url": url }))


def outside_rule_view(definition):
    template = get_template('irules/outside_rule.html')
    return template.render(Context({ "definition": definition }))


