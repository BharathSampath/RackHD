# Copyright 2016, EMC, Inc.

'''
This script tests base case of the OnRack BootImage API and OS bootstrap workflows
The test will select a single eligible node to run all currently supported bootstrap workflows
This is a LONG-RUNNING script which will typically take 1-2 hours to execute
'''

import os
import sys
import subprocess
import random

# set path to common libraries
sys.path.append(subprocess.check_output("git rev-parse --show-toplevel", shell=True).rstrip("\n") + "/test/common")
import fit_common

# This node catalog section will be replaced with fit_common.node_select() when it is checked in
NODECATALOG = fit_common.node_select()

NODE = ""
# Select one node at random
NODE = NODECATALOG[random.randint(0, len(NODECATALOG)-1)]

# this routine polls a task ID for completion
def wait_for_task_complete(taskid, retries=60):
    for dummy in range(0, retries):
        result = fit_common.rackhdapi(taskid)
        if result['json']['TaskState'] == 'Running' or result['json']['TaskState'] == 'Pending':
            if fit_common.VERBOSITY >= 2:
                print "OS Install workflow state: {}".format(result['json']['TaskState'])
            fit_common.time.sleep(30)
        elif result['json']['TaskState'] == 'Completed':
            if fit_common.VERBOSITY >= 2:
                print "OS Install workflow state: {}".format(result['json']['TaskState'])
            return True
        else:
            break
    print "Task failed with the following state: " + result['json']['TaskState']
    return False

# download OS proxy config from host
httpProxies = fit_common.rackhdapi('/api/2.0/config')['json']['httpProxies']
# helper routine for selecting OS image path by matching proxy path
def proxySelect(tag):
    for entry in httpProxies:
        if tag in entry['localPath']:
            return entry['localPath']
    return ''

# ------------------------ Tests -------------------------------------
from nose.plugins.attrib import attr
@attr(all=True, regression=True)
class os_bootstrap_base(fit_common.unittest.TestCase):
    def setUp(self):
        #delete active workflows for specified node
        fit_common.cancel_active_workflows(NODE)

    @fit_common.unittest.skipUnless(proxySelect('ESXi/5.5') != '', "Skipping ESXi5.5")
    def test_bootstrap_esxi55(self):
        if fit_common.VERBOSITY >= 2:
            print 'Running ESXI 5.5 bootstrap.'
        nodehostname = 'esxi55'
        payload_data = {
                        "osName": "ESXi",
                        "version": "5.5",
                        "repo": "http://172.31.128.1:9080" + proxySelect('ESXi/5.5'),
                        "rootPassword": "1234567",
                        "hostname": nodehostname,
                        "domain": "hwimo.lab.emc.com",
                        "dnsServers": ["172.31.128.1"],
                        "users": [{
                                    "name": "onrack",
                                    "password": "Onr@ck1!",
                                    "uid": 1010,
                                }]
                       }
        result = fit_common.rackhdapi('/redfish/v1/Systems/'
                                            + NODE
                                            + '/Actions/RackHD.BootImage',
                                            action='post', payload=payload_data)
        self.assertEqual(result['status'], 202,
                         'Was expecting code 202. Got ' + str(result['status']))
        self.assertEqual(wait_for_task_complete(result['json']['@odata.id'], retries=80), True,
                         'TaskID ' + result['json']['@odata.id'] + ' not successfully completed.')


    @fit_common.unittest.skipUnless(proxySelect('ESXi/6.0') != '', "Skipping ESXi6.0")
    def test_bootstrap_esxi60(self):
        if fit_common.VERBOSITY >= 2:
            print 'Running ESXI 6.0 bootstrap.'
        nodehostname = 'esxi60'
        payload_data = {"osName": "ESXi",
                        "version": "6.0",
                        "repo": "http://172.31.128.1:9080" + proxySelect('ESXi/6.0'),
                        "rootPassword": "1234567",
                        "hostname": nodehostname,
                        "domain": "hwimo.lab.emc.com",
                        "dnsServers": ["172.31.128.1"],
                        "users": [{
                                    "name": "onrack",
                                    "password": "Onr@ck1!",
                                    "uid": 1010,
                                }]
                       }
        result = fit_common.rackhdapi('/redfish/v1/Systems/'
                                            + NODE
                                            + '/Actions/RackHD.BootImage',
                                            action='post', payload=payload_data)
        self.assertEqual(result['status'], 202,
                         'Was expecting code 202. Got ' + str(result['status']))
        self.assertEqual(wait_for_task_complete(result['json']['@odata.id'], retries=80), True,
                         'TaskID ' + result['json']['@odata.id'] + ' not successfully completed.')


    @fit_common.unittest.skipUnless(proxySelect('CentOS/6.5') != '', "Skipping Centos 6.5")
    def test_bootstrap_centos65(self):
        if fit_common.VERBOSITY >= 2:
            print 'Running CentOS 6.5 bootstrap.'
        nodehostname = 'centos65'
        payload_data = {"osName": "CentOS",
                        "version": "6.5",
                        "repo": "http://172.31.128.1:9080" + proxySelect('CentOS/6.5'),
                        "rootPassword": "1234567",
                        "hostname": nodehostname,
                        "domain": "hwimo.lab.emc.com",
                        "dnsServers": ["172.31.128.1"],
                        "users": [{
                                    "name": "onrack",
                                    "password": "onrack",
                                    "uid": 1010,
                                }]
                       }
        result = fit_common.rackhdapi('/redfish/v1/Systems/'
                                            + NODE
                                            + '/Actions/RackHD.BootImage',
                                            action='post', payload=payload_data)
        self.assertEqual(result['status'], 202,
                         'Was expecting code 202. Got ' + str(result['status']))
        self.assertEqual(wait_for_task_complete(result['json']['@odata.id']), True,
                         'TaskID ' + result['json']['@odata.id'] + ' not successfully completed.')


    @fit_common.unittest.skipUnless(proxySelect('CentOS/7.0') != '', "Skipping Centos 7.0")
    def test_bootstrap_centos70(self):
        if fit_common.VERBOSITY >= 2:
            print 'Running CentOS 7 bootstrap...'
        nodehostname = 'centos70'
        payload_data = {"osName": "CentOS",
                        "version": "7",
                        "repo": "http://172.31.128.1:9080" + proxySelect('CentOS/7.0'),
                        "rootPassword": "1234567",
                        "hostname": nodehostname,
                        "domain": "hwimo.lab.emc.com",
                        "dnsServers": ["172.31.128.1"],
                        "users": [{
                                    "name": "onrack",
                                    "password": "onrack",
                                    "uid": 1010,
                                }],

                       }
        result = fit_common.rackhdapi('/redfish/v1/Systems/'
                                            + NODE
                                            + '/Actions/RackHD.BootImage',
                                            action='post', payload=payload_data)
        self.assertEqual(result['status'], 202,
                         'Was expecting code 202. Got ' + str(result['status']))
        self.assertEqual(wait_for_task_complete(result['json']['@odata.id']), True,
                         'TaskID ' + result['json']['@odata.id'] + ' not successfully completed.')


    @fit_common.unittest.skipUnless(proxySelect('CentOS/6.5') != '', "Skipping Centos 6.5 KVM")
    def test_bootstrap_centos65_kvm(self):
        if fit_common.VERBOSITY >= 2:
            print 'Running CentOS 6.5 KVM bootstrap.'
        nodehostname = 'centos65'
        payload_data = {"osName": "CentOS+KVM",
                        "version": "6.5",
                        "repo": "http://172.31.128.1:9080" + proxySelect('CentOS/6.5'),
                        "rootPassword": "1234567",
                        "hostname": nodehostname,
                        "domain": "hwimo.lab.emc.com",
                        "dnsServers": ["172.31.128.1"],
                        "users": [{
                                    "name": "onrack",
                                    "password": "onrack",
                                    "uid": 1010,
                                }]
                       }
        result = fit_common.rackhdapi('/redfish/v1/Systems/'
                                            + NODE
                                            + '/Actions/RackHD.BootImage',
                                            action='post', payload=payload_data)
        self.assertEqual(result['status'], 202,
                         'Was expecting code 202. Got ' + str(result['status']))
        self.assertEqual(wait_for_task_complete(result['json']['@odata.id']), True,
                         'TaskID ' + result['json']['@odata.id'] + ' not successfully completed.')


    @fit_common.unittest.skipUnless(proxySelect('RHEL/7.0') != '', "Skipping Redhat 7.0")
    def test_bootstrap_rhel70_kvm(self):
        if fit_common.VERBOSITY >= 2:
            print 'Running RHEL 7 KVM bootstrap.'
        nodehostname = 'rhel70'
        payload_data = {"osName": "RHEL+KVM",
                        "version": "7",
                        "repo": "http://172.31.128.1:9080" + proxySelect('RHEL/7.0'),
                        "rootPassword": "1234567",
                        "hostname": nodehostname,
                        "domain": "hwimo.lab.emc.com",
                        "dnsServers": ["172.31.128.1"],
                        "users": [{
                                    "name": "onrack",
                                    "password": "onrack",
                                    "uid": 1010,
                                }],

                       }
        result = fit_common.rackhdapi('/redfish/v1/Systems/'
                                            + NODE
                                            + '/Actions/RackHD.BootImage',
                                            action='post', payload=payload_data)
        self.assertEqual(result['status'], 202,
                         'Was expecting code 202. Got ' + str(result['status']))
        self.assertEqual(wait_for_task_complete(result['json']['@odata.id']), True,
                         'TaskID ' + result['json']['@odata.id'] + ' not successfully completed.')

if __name__ == '__main__':
    fit_common.unittest.main()
