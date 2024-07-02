# -*- coding: utf-8 -*-
from dogtail.tree import root
from dogtail.utils import run


def gedit_stress_test_tree_api():
    run("gedit")

    gedit = root.application("gedit")

    for _ in range(100):
        gedit.child("Menu", "toggle button").click() # open
        gedit.child("Menu", "toggle button").click() # close

        gedit.child("Save", "push button").click()
        gedit.child("Cancel", "push button").click()

gedit_stress_test_tree_api()
