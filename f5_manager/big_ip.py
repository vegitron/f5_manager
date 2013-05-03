import pycontrol
from django.conf import settings

class BigIP(object):
    def __init__(self, host):
        self._host = host

    def get_enabled_rules(self):
        big_ip = pycontrol.BIGIP(
            hostname = settings.F5_BIGIP_HOST,
            username = self._host.admin_user,
            password = self._host.admin_pass,
            fromurl = True,
            wsdls = ['LocalLB.VirtualServer', 'Management.Partition']
        )
        if self._host.partition:
            big_ip.Management.Partition.set_active_partition(self._host.partition)

        enabled_rules = big_ip.LocalLB.VirtualServer.get_rule(["/%s/%s" % (self._host.partition, self._host.hostname)])[0]

        return enabled_rules

    def get_highest_rule_priority(self):
        rules = self.get_enabled_rules()
        max_priority = 0
        for rule in rules:
            if rule.priority > max_priority:
                max_priority = rule.priority

        return max_priority

    def get_all_rules(self):
        big_ip = pycontrol.BIGIP(
            hostname = settings.F5_BIGIP_HOST,
            username = self._host.admin_user,
            password = self._host.admin_pass,
            fromurl = True,
            wsdls = ['LocalLB.Rule', 'Management.Partition']
        )
        if self._host.partition:
            big_ip.Management.Partition.set_active_partition(self._host.partition)

        return big_ip.LocalLB.Rule.query_all_rules()


    def disable_rule(self, rule_name):
        host = self._host
        big_ip = pycontrol.BIGIP(
            hostname = settings.F5_BIGIP_HOST,
            username = host.admin_user,
            password = host.admin_pass,
            fromurl = True,
            wsdls = ['LocalLB.Rule', 'LocalLB.VirtualServer']
        )

        rule_set = big_ip.LocalLB.VirtualServer.typefactory.create('LocalLB.VirtualServer.VirtualServerRule')
        rule_set.rule_name = rule_name
        rule_set.priority = 1

        rule_seq = big_ip.LocalLB.VirtualServer.typefactory.create('LocalLB.VirtualServer.VirtualServerRuleSequence')

        rule_seq.item = [rule_set]

        big_ip.LocalLB.VirtualServer.remove_rule(["/%s/%s" % (host.partition, host.hostname)], [[rule_seq]])

    def enable_rule(self, rule_name, priority):
        host = self._host
        big_ip = pycontrol.BIGIP(
            hostname = settings.F5_BIGIP_HOST,
            username = host.admin_user,
            password = host.admin_pass,
            fromurl = True,
            wsdls = ['LocalLB.Rule', 'LocalLB.VirtualServer']
        )


        rule_set = big_ip.LocalLB.VirtualServer.typefactory.create('LocalLB.VirtualServer.VirtualServerRule')
        rule_set.rule_name = rule_name
        rule_set.priority = priority

        rule_seq = big_ip.LocalLB.VirtualServer.typefactory.create('LocalLB.VirtualServer.VirtualServerRuleSequence')

        rule_seq.item = [rule_set]

        big_ip.LocalLB.VirtualServer.add_rule(["/%s/%s" % (host.partition, host.hostname)], [[rule_seq]])


