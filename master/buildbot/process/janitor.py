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

from twisted.application.internet import TimerService
from twisted.internet import defer
from twisted.internet import reactor

from buildbot.data import resultspec
from buildbot.process.results import RETRY
from buildbot.util import epoch2datetime
from buildbot.util import service

# time, in minutes, after which a master that hasn't checked in will be
# marked as inactive
EXPIRE_MINUTES = 10


class MrProperService(service.ClusteredBuildbotService):
    """Mr Proper is clustered, so it will run only once per cluster.
    So we know that there won't be too master doing the cleanups at the same time.
    """
    timer = None
    # we use this name in order to avoid clashing against user's scheduler.
    name = "__MrProper__"

    def activate(self):
        self.timer = TimerService(3600, self.doAllCleanups)
        return self.timer.setServiceParent(self)

    def deactivate(self):
        if self.timer is not None:
            timer, self.timer = self.timer, None
            return timer.disownServiceParent()

    @defer.inlineCallbacks
    def doAllCleanups(self):
        # we are in no rush, serialize the work.
        yield self.cleanInactiveMasters()
        yield self.cleanLogs()
        yield self.cleanBuilds()

    @defer.inlineCallbacks
    def cleanInactiveMasters(self, _reactor=reactor):
        masters = yield self.master.db.masters.getMasters()
        for m in masters:
            if not m['active']:
                self.cleanInactiveMaster(m['masterid'])

    def cleanLogs(self):
        # TODO in another PR
        pass

    def cleanBuilds(self):
        # TODO in another PR
        pass


    @defer.inlineCallbacks
    def cleanInactiveMaster(self, masterid):
        # for each build running on that instance..
        builds = yield self.master.data.get(('builds',),
                                            filters=[resultspec.Filter('masterid', 'eq', [masterid]),
                                                     resultspec.Filter('complete', 'eq', [False])])
        for build in builds:
            # stop any running steps..
            steps = yield self.master.data.get(
                ('builds', build['buildid'], 'steps'),
                filters=[resultspec.Filter('results', 'eq', [None])])
            for step in steps:
                # finish remaining logs for those steps..
                logs = yield self.master.data.get(
                    ('steps', step['stepid'], 'logs'),
                    filters=[resultspec.Filter('complete', 'eq',
                                               [False])])
                for _log in logs:
                    yield self.master.data.updates.finishLog(
                        logid=_log['logid'])
                yield self.master.data.updates.finishStep(
                    stepid=step['stepid'], results=RETRY, hidden=False)
            # then stop the build itself
            yield self.master.data.updates.finishBuild(
                buildid=build['buildid'], results=RETRY)

        # unclaim all of the build requests owned by the deactivated instance
        buildrequests = yield self.master.db.buildrequests.getBuildRequests(
            complete=False, claimed=masterid)

        yield self.master.db.buildrequests.unclaimBuildRequests(
            brids=[br['buildrequestid'] for br in buildrequests])

    # We use the scheduler tables in order to hold our MrProper cluster coordination state
    # instead of creating one specially for this one single ClusteredService

    def _getServiceId(self):
        return self.master.data.updates.findSchedulerId(self.name)

    def _claimService(self):
        return self.master.data.updates.trySetSchedulerMaster(self.serviceid,
                                                              self.master.masterid)

    def _unclaimService(self):
        return self.master.data.updates.trySetSchedulerMaster(self.serviceid,
                                                              None)


class JanitorService(service.ReconfigurableServiceMixin, service.AsyncMultiService):
    """There is one Janitor per master
    Responsible for the master heartbeat, and for hiring the MrProper
    """
    name = 'Janitor'

    def __init__(self):
        service.AsyncMultiService.__init__(self)

        self.logHorizon = None
        self.buildHorizon = None
        self.oldConfigurationHorizon = None
        self.mrproper = MrProperService()
        self.mrproper.setServiceParent(self)
        self.timer = TimerService(60, self.doHeartBeat)

    def reconfigServiceWithBuildbotConfig(self, new_config):
        self.logHorizon = new_config.logHorizon
        self.buildHorizon = new_config.buildHorizon

        # chain up
        return service.ReconfigurableServiceMixin.reconfigServiceWithBuildbotConfig(self,
                                                                                    new_config)

    @defer.inlineCallbacks
    def doHeartBeat(self):
        if self.master.masterid is not None:
            yield self.master.data.updates.masterActive(name=self.master.name,
                                                        masterid=self.master.masterid)
        yield self.expireMasters()

    def expireMasters(self, _reactor=reactor):
        too_old = epoch2datetime(_reactor.seconds() - 60 * EXPIRE_MINUTES)
        masters = yield self.master.db.masters.getMasters()
        for m in masters:
            if m['active'] and m['last_active'] is not None and m['last_active'] >= too_old:
                continue
            self.master.data.updates.masterStopped()
