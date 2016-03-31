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
import textwrap

from buildbot.util import raml
from collections import OrderedDict
from twisted.trial import unittest


class TestRaml(unittest.TestCase):

    def setUp(self):
        self.api = raml.RamlSpec()

    def test_api(self):
        self.assertIsNotNone(self.api.api)

    def test_endpoints(self):
        self.assertIn(
            "/masters/{masterid}/builders/{builderid}/workers/{workerid}",
            self.api.endpoints.keys())

    def test_endpoints_uri_parameters(self):
        # comparaison of OrderedDict do not take in account order :(
        # this is why we compare str repr, to make sure the endpoints are in the right order
        self.assertEqual(str(self.api.endpoints[
            "/masters/{masterid}/builders/{builderid}/workers/{workerid}"]['uriParameters']),
            str(OrderedDict([
                ('masterid', OrderedDict([
                    ('type', 'number'), ('description', 'the id of the master')])),
                ('builderid', OrderedDict([
                    ('type', 'number'), ('description', 'the id of the builder')])),
                ('workerid', OrderedDict([
                    ('type', 'number'), ('description', 'the id of the worker')]))]))
        )

    def test_types(self):
        self.assertIn(
            "log",
            self.api.types.keys())

    def test_json_example(self):
        self.assertEqual(
            textwrap.dedent(self.api.format_json(self.api.types["build"]['example'], 0)),
            textwrap.dedent("""
            {
                "builderid": 10,
                "buildid": 100,
                "buildrequestid": 13,
                "workerid": 20,
                "complete": false,
                "complete_at": null,
                "masterid": 824,
                "number": 1,
                "results": null,
                "started_at": 1451001600,
                "state_string": "created",
                "properties": {}
            }""").strip())

    def test_endpoints_by_type(self):
        self.assertIn(
            "/masters/{masterid}/builders/{builderid}/workers/{workerid}",
            self.api.endpoints_by_type['worker'].keys())