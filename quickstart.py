""" Quickstart script for YoutubePy usage """

# imports
from youtubepy import YoutubePy
from youtubepy import smart_run
from socialcommons.file_manager import set_workspace
from youtubepy import settings

import random

# set workspace folder at desired location (default is at your home folder)
set_workspace(settings.Settings, path=None)

# get an YoutubePy session!
session = YoutubePy(use_firefox=True)

with smart_run(session):
    """ Activity flow """
    # general settings
    session.set_dont_include(["friend1", "friend2", "friend3"])

    session.set_do_follow(enabled=True, percentage=40, times=1)

    targets = ['janandd', 'M0nica', 'gaearon', 'rauchg']
    number = random.randint(3, 5)
    random_targets = targets

    if len(targets) <= number:
        random_targets = targets
    else:
        random_targets = random.sample(targets, number)
    session.search_and_comment(query="Giveaway")