# -*- coding: utf-8 -*-
from dogtail.tree import root
from dogtail.utils import run


def gedit_stress_test_tree_api():
    run("gedit")

    gedit = root.application("gedit")

    for _ in range(100):
        gedit.child("Menu", "toggle button").click() # open
        gedit.child("Menu", "toggle button").click() # close

        gedit.findChild(lambda x: x.name == "Save" and x.roleName in ("button", "push button")).click()
        gedit.findChild(lambda x: x.name == "Cancel" and x.roleName in ("button", "push button")).click()

gedit_stress_test_tree_api()
