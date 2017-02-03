# This file is part of Buildbot.  Buildbot is free software: you can
# redistribute it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright Buildbot Team Members

from __future__ import absolute_import
from __future__ import print_function

import mock

from twisted.internet import defer
from twisted.trial import unittest

from buildbot import config
from buildbot.process import janitor
from buildbot.test.fake import fakemaster
from buildbot.util import service


class FakeManhole(service.AsyncService):
    pass


class TestJanitor(unittest.TestCase):

    def setUp(self):
        self.master = fakemaster.make_master(testcase=self, wantData=True)
        self.config = config.MasterConfig()
        return self.master.startService()

    def tearDown(self):
        return self.master.stopService()

    @defer.inlineCallbacks
    def test_reconfigService(self):
        jn = janitor.JanitorService()
        yield jn.setServiceParent(self.master)
