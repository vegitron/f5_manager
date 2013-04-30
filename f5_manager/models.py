from django.db import models
from django.conf import settings
from django_fields.fields import EncryptedCharField
from django.core.urlresolvers import reverse
from f5_manager.rule_views import *
import re

# Create your models here.

class VirtualHost(models.Model):
    hostname = models.CharField(max_length=150)
    admin_user = models.CharField(max_length=150)
    admin_pass = EncryptedCharField(max_length=150)
    partition = models.CharField(max_length=150)

    def view_url(self):
        url_hostname = self.hostname
        url_hostname = re.sub(r'[^\w]+', '-', url_hostname)
        url_hostname = re.sub(r'-*$', '', url_hostname)

        return reverse('f5_manager.views.virtualhost', args=(url_hostname, self.id))

class iRule(models.Model):
    def get_description_from_definition(self, definition):
        redirect_desc = self._get_redirect_description(definition)
        if redirect_desc:
            return redirect_desc

        return outside_rule_view(definition)

    def _get_redirect_description(self, definition):
        matches = re.match('^\s*when HTTP_REQUEST {\s*HTTP::respond 302\s*(.*?)\s*}\s*$', definition)

        if matches == None:
            return None

        return redirect_view(matches.group(1))

