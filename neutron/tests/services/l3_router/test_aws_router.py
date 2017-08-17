"""
Copyright (c) 2017 Platform9 Systems Inc.
Licensed under the Apache License, Version 2.0 (the "License"); you may
not use this file except in compliance with the License. You may obtain
a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either expressed or implied. See the
License for the specific language governing permissions and limitations
under the License.
"""

import mock
import os
from neutron.common import exceptions
from neutron_lib import constants as const

from neutron.services.l3_router.aws_router_plugin import AwsRouterPlugin
from neutron.tests.common.gce import gce_mock
from neutron.common.aws_utils import AwsUtils
from neutron.common.aws_utils import cfg

from neutron.tests import base
from neutron.tests.unit.extensions import test_securitygroup as test_sg

import boto3
from moto import mock_ec2

DATA_DIR = os.path.dirname(os.path.abspath("gce_mock.py")) + '/data'
L3_NAT_WITH_DVR_DB_MIXIN = 'neutron.db.l3_dvr_db.L3_NAT_with_dvr_db_mixin'
AWS_ROUTER = 'neutron.services.l3_router.aws_router_plugin.AwsRouterPlugin'
GCE_UTILS = 'neutron.common.gceutils'
EXTRAROUTE_DB = 'neutron.db.extraroute_db.ExtraRoute_dbonly_mixin'


class TestAWSRouterPlugin(test_sg.SecurityGroupsTestCase, base.BaseTestCase):
    @mock_ec2
    def setUp(self):
        super(TestAWSRouterPlugin, self).setUp()
	cfg.CONF.AWS.secret_key = 'aws_access_key'
	cfg.CONF.AWS.access_key = 'aws_secret_key'
	cfg.CONF.AWS.region_name = 'us-east-1'
        self._driver = AwsRouterPlugin()
        self.context = self._create_fake_context()

    def _create_fake_context(self):
        context = mock.Mock()
        context.current = {}
        context.current['id'] = "fake_id_1234"
        context.current['cidr'] = "192.168.1.0/24"
        context.current['network_id'] = "fake_network_id_1234"

    @mock_ec2
    @mock.patch(L3_NAT_WITH_DVR_DB_MIXIN + '.create_floatingip')
    @mock.patch(AWS_ROUTER + '._associate_floatingip_to_port')
    def test_create_floatingip1(self, mock_assoc, mock_create):

        floatingip = {'floatingip': {'port_id': True}}

	mock_assoc.return_value = None
	mock_create.return_value = None

        self.assertIsNone(self._driver.create_floatingip(self.context, floatingip))
        self.assertTrue(mock_assoc.called)
	mock_create.assert_called_once_with(
	    self.context, floatingip, initial_status=const.FLOATINGIP_STATUS_DOWN)

    @mock_ec2
    @mock.patch(L3_NAT_WITH_DVR_DB_MIXIN + '.create_floatingip')
    @mock.patch(AWS_ROUTER + '._associate_floatingip_to_port')
    def test_create_floatingip2(self, mock_assoc, mock_create):

        floatingip = {'floatingip': {}}

	mock_assoc.return_value = None
	mock_create.return_value = None

        self.assertIsNone(self._driver.create_floatingip(self.context, floatingip))
        self.assertFalse(mock_assoc.called)
	mock_create.assert_called_once_with(
	    self.context, floatingip, initial_status=const.FLOATINGIP_STATUS_DOWN)

    @mock_ec2
    @mock.patch(L3_NAT_WITH_DVR_DB_MIXIN + '.create_floatingip')
    @mock.patch(AWS_ROUTER + '._associate_floatingip_to_port')
    def test_create_floatingip_with_exception1(self, mock_assoc, mock_create):

        floatingip = {'floatingip': {'port_id': True}}

        mock_assoc.side_effect = exceptions.PhysicalNetworkNameError()
        mock_create.return_value = None

        self.assertRaises(
            exceptions.PhysicalNetworkNameError, self._driver.create_floatingip,
            self.context, floatingip)
        self.assertTrue(mock_assoc.called)

    @mock_ec2
    @mock.patch(L3_NAT_WITH_DVR_DB_MIXIN + '.create_floatingip')
    @mock.patch(AWS_ROUTER + '._associate_floatingip_to_port')
    def test_create_floatingip_with_exception2(self, mock_assoc, mock_create):

        floatingip = {'floatingip': {'port_id': True}}

        mock_create.side_effect = exceptions.PhysicalNetworkNameError()
        mock_assoc.return_value = None

        self.assertRaises(
            exceptions.PhysicalNetworkNameError, self._driver.create_floatingip,
            self.context, floatingip)
        self.assertTrue(mock_assoc.called)
