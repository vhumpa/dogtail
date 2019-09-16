# -*- coding: utf-8 -*-
import os
from dogtail import tree
from dogtail.utils import run
from dogtail.predicate import GenericPredicate


def gedit_text_tree_api_demo():
    os.environ["LANG"] = "en_US.UTF-8"

    # Remove the output file, if it's still there from a previous run
    if os.path.isfile(os.path.join("/tmp", "UTF8demo.txt")):
        os.remove(os.path.join("/tmp", "UTF8demo.txt"))

    # Start gedit.
    # Get a handle to gedit's application object.
    os.system("killall gedit") # preventing the undesired result if the sript is started multiple times in a row
    run("gedit")
    gedit = tree.root.application("gedit")

    # Get a handle to gedit's text object.
    text_buffer = gedit.findChildren(GenericPredicate(roleName="text"))[1]
    # is equal to
    # text_buffer = gedit.findChild(lambda x: x.roleName=="text" and x.showing) # we can specify search by another attribute - showing
    # Load the UTF-8 demo file.
    # Set the attribute to the given text object
    with open(os.path.abspath(".") + "/data/UTF-8-demo.txt", "r") as open_file:
        text_buffer.text = open_file.read()


    # Get a handle to gedit's Save button and click.
    save_button = gedit.child("Save", "push button")
    save_button.click()


    # We want to save to the file name 'UTF8demo.txt'.
    dialog = gedit.findChild(lambda x: "Save As" in x.name and x.roleName == "file chooser")
    dialog.child(roleName="text").text = "/tmp/UTF8demo.txt"


    # Get a handle to gedit's Save dialog and click.
    save_as_button = gedit.findChildren(lambda x: "Save" in x.name)[-1]
    save_as_button.click()


    # Let's quit now.
    gedit.child("Menu", "toggle button").click()
    # Sometimes the node is not unique so you need to specify another attribute to look for
    gedit.findChild(lambda x: x.name == "Close" and x.showing).click()


gedit_text_tree_api_demo()
