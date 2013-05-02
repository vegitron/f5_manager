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

        for method in (self._get_redirect_description, self._get_pool_mapping_description, self._get_client_cert_description):
            desc = method(definition)
            if desc:
                return desc

        return outside_rule_view(definition)

    def _get_redirect_description(self, definition):
        matches = re.match('^\s*when HTTP_REQUEST {\s*HTTP::respond 302 Location \s*(.*?)\s*}\s*$', definition)

        if matches == None:
            return None

        return redirect_view(matches.group(1))

    def _get_pool_mapping_description(self, definition):
        matches = re.match('^\s*when HTTP_REQUEST {\s*if { \[HTTP::uri\] (.*?) "(.*?)" } {\s*pool (.*?)\s*}\s*}\s*$', definition)

        if matches == None:
            return None

        return pool_mapping_view(matches.group(1), matches.group(2), matches.group(3))



    def _get_client_cert_description(self, definition):
        matches = re.match('^\s*when CLIENT_ACCEPTED {\s*set collecting 0\s*set renegtried 0\s*}\s*when HTTP_REQUEST {\s*if { \$renegtried == 0\s*and \[SSL::cert count\] == 0\s*and \(\[HTTP::uri\] (.*?) "(.*?)"\) } {\s*HTTP::collect\s*set collecting 1\s*SSL::cert mode request\s*SSL::renegotiate\s*}\s*}\s*when CLIENTSSL_HANDSHAKE {\s*if { \$collecting == 1 } {\s*set renegtried 1\s*HTTP::release\s*}\s*}\s*when HTTP_REQUEST_SEND {\s*clientside {\s*HTTP::header remove "(.*?)"\s*if { \[SSL::cert count\] > 0 } {\s*HTTP::header insert "(.*?)" \[X509::subject \[SSL::cert 0\]\]\s*}\s*}\s*}\s*$', definition)

        if matches == None:
            return None

        action = matches.group(1)
        url_match = matches.group(2)
        header1 = matches.group(3)
        header2 = matches.group(4)

        if header1 != header2:
            return None

        return client_ssl_cert_view(action, url_match, header1)

