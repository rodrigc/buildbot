from twisted.internet import defer

from buildbot.www.plugin import Application
from buildbot.schedulers.forcesched import ChoiceStringParameter


class BranchSelector(ChoiceStringParameter):

    spec_attributes = ["selectors"]
    type = "branchselector"
    selectors = None

# create the interface for the setuptools entry point
ep = Application(__name__, "Buildbot branch selector")
