import pycontrol
from django.conf import settings
import re
import time

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


    def get_hosts_for_pool(self, pool_name):
        host = self._host
        big_ip = pycontrol.BIGIP(
            hostname = settings.F5_BIGIP_HOST,
            username = host.admin_user,
            password = host.admin_pass,
            fromurl = True,
            wsdls = ['LocalLB.Pool']
        )

        members = big_ip.LocalLB.Pool.get_member_v2([pool_name])
        return members[0]


    def get_pools(self):
        big_ip = pycontrol.BIGIP(
            hostname = settings.F5_BIGIP_HOST,
            username = self._host.admin_user,
            password = self._host.admin_pass,
            fromurl = True,
            wsdls = ['LocalLB.Pool', 'Management.Partition']
        )
        if self._host.partition:
            big_ip.Management.Partition.set_active_partition(self._host.partition)

        pool_names = big_ip.LocalLB.Pool.get_list()
        members = big_ip.LocalLB.Pool.get_member_v2(pool_names)

        return_list = []
        for index in range(0, len(pool_names)):
            return_list.append({
                "name": pool_names[index],
                "members": members[index],
            })

        return return_list

    def get_hosts(self):
        big_ip = pycontrol.BIGIP(
            hostname = settings.F5_BIGIP_HOST,
            username = self._host.admin_user,
            password = self._host.admin_pass,
            fromurl = True,
            wsdls = ['LocalLB.NodeAddressV2', 'Management.Partition']
        )
        if self._host.partition:
            big_ip.Management.Partition.set_active_partition(self._host.partition)


        host_strings = big_ip.LocalLB.NodeAddressV2.get_list()
        host_addresses = big_ip.LocalLB.NodeAddressV2.get_address(host_strings)

        return_list = []

        for index in range(0, len(host_strings)):
            return_list.append({
                "name": host_strings[index],
                "ip": host_addresses[index],
            })

        return return_list


    def create_pool_for_hosts(self, hosts):
        host = self._host
        big_ip = pycontrol.BIGIP(
            hostname = settings.F5_BIGIP_HOST,
            username = host.admin_user,
            password = host.admin_pass,
            fromurl = True,
            wsdls = ['LocalLB.Pool', 'Management.Partition']
        )

        if host.partition:
            big_ip.Management.Partition.set_active_partition(host.partition)

        lbmeth = big_ip.LocalLB.Pool.typefactory.create('LocalLB.LBMethod')
        mem_sequence = big_ip.LocalLB.Pool.typefactory.create('Common.IPPortDefinitionSequence')

        items = []
        for host in hosts:
            member = big_ip.LocalLB.Pool.typefactory.create('Common.AddressPort')
            member.address = host
            member.port = 443 # XXX - should we handle non-https requests?

            items.append(member)

        mem_sequence.items = items

        pool_name = "pl_f5manager_%s_%s" % (self._clean_name("-".join(hosts)), time.time())

        big_ip.LocalLB.Pool.create_v2(
            pool_names = ["%s" % (pool_name)],
            lb_methods = [lbmeth.LB_METHOD_ROUND_ROBIN],
            members = [mem_sequence]
        )

        return pool_name

    def create_url_map_to_pool(self, match_type, url_match, pool_name):
        host = self._host
        big_ip = pycontrol.BIGIP(
            hostname = settings.F5_BIGIP_HOST,
            username = host.admin_user,
            password = host.admin_pass,
            fromurl = True,
            wsdls = ['LocalLB.Rule', 'Management.Partition']
        )

        if host.partition:
            big_ip.Management.Partition.set_active_partition(host.partition)

        irule = """
            when HTTP_REQUEST {
                if { [HTTP::uri] %s "%s" } {
                    pool %s
                }
            }
            """ % (match_type, url_match, pool_name)

        r_def = big_ip.LocalLB.Rule.typefactory.create('LocalLB.Rule.RuleDefinition')

        long_name = "ir_f5manager_%s_%s_%s" % (self._clean_name(host.hostname), self._clean_name(url_match), self._clean_name(pool_name))

        r_def.rule_name = long_name
        r_def.rule_definition = irule

        big_ip.LocalLB.Rule.create(rules = [r_def])


    def create_offline_rule(self, destination):
        host = self._host
        big_ip = pycontrol.BIGIP(
            hostname = settings.F5_BIGIP_HOST,
            username = host.admin_user,
            password = host.admin_pass,
            fromurl = True,
            wsdls = ['LocalLB.Rule', 'Management.Partition']
        )

        if host.partition:
            big_ip.Management.Partition.set_active_partition(host.partition)

        irule = """
            when HTTP_REQUEST {
                HTTP::respond 302 Location %s
            }
            """ % (destination)

        r_def = big_ip.LocalLB.Rule.typefactory.create('LocalLB.Rule.RuleDefinition')

        long_name = "ir_f5manager_offline_%s" % (self._clean_name(destination))

        r_def.rule_name = long_name
        r_def.rule_definition = irule

        big_ip.LocalLB.Rule.create(rules = [r_def])


    def _clean_name(self, name):
        return re.sub('[^\w]+', '-', name)

