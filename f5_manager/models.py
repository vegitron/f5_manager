from django.db import models
from django.conf import settings
from django_fields.fields import EncryptedCharField
from django.core.urlresolvers import reverse
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

