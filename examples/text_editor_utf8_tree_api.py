#!/usr/bin/python3

"""
Example of opening an example UTF-8 file in Text Editor.
"""

# ruff: noqa: E501

import os
from time import sleep
from dogtail.tree import root
from dogtail.utils import run

def gnome_text_editor_text_tree_api_demo():
    """
    Example how to work with GNOME Text Editor.
    """

    os.environ["LANG"] = "en_US.UTF-8"

    # Remove the output file, if it's still there from a previous run.
    if os.path.isfile(os.path.join("/tmp", "UTF8demo.txt")):
        os.remove(os.path.join("/tmp", "UTF8demo.txt"))


    # Preventing the undesired result if the script is started multiple times in a row.
    print("EXAMPLE: Close any leftover application from previous run.")
    os.system("killall gnome-text-editor")
    sleep(1)

    # Start gnome-text-editor.
    print("EXAMPLE: Start GNOME Text Editor.")
    run("gnome-text-editor")
    sleep(1)

    # Get a root object to gnome-text-editor's application object.
    editor = root.application("gnome-text-editor")

    # Get a handle to gnome-text-editor's text object.
    text_buffer = editor.find_children(lambda x: x.role_name == "text")[-1]

    # First check that the file exists.
    file_location = os.path.abspath(".") + "/data/UTF-8-demo.txt"
    if not os.path.isfile(file_location):
        print(f"EXAMPLE: File was not found in expected location '{file_location}'")

    # Load the UTF-8 demo file.
    with open(file_location, "r", encoding="utf-8") as open_file:
        # Set the attribute .text to the given text object.
        # This does not always work and user has to type the text with type_text("...").
        text_buffer.text = open_file.read()

    # Get a handle to gnome-text-editor's Main menu toggle button and click on it.
    print("EXAMPLE: Left click on Main menu in GNOME Text Editor.")
    main_menu = editor.child("Main menu", "toggle button")
    main_menu.click()
    sleep(1)

    # Get a handle to gnome-text-editor's Save menu item and click on it.
    # This needs to be a little bit more complicated to get to it, as it can be hidden.
    # save_button = editor.child("Save", "menu item")
    print("EXAMPLE: Left click on Save menu item in GNOME Text Editor.")
    save_button = editor.find_child(
        lambda x: "Save" in (x.name, x.text, x.labeler.name, x.labeler.text)
        and x.role_name == "menu item"
        and x.showing
    )

    # This is a nice example how coordinates are wrong.
    # To fix this we need to click on the labeler and adjust the coordinates a little.
    # save_button.labeler.click()
    save_button.labeler.click(offset_y=20)
    sleep(1)

    # We want to save to the file name 'UTF8demo.txt'.
    print("EXAMPLE: Set location for file to save in GNOME Text Editor.")
    save_as_dialog = editor.findChild(
        lambda x: "Save As" in x.name and x.role_name in ("file chooser", "dialog")
    )
    save_as_dialog.child("Name", "text").text = "/tmp/UTF8demo.txt"
    sleep(1)

    # Get a handle to gnome-text-editor's Save push button and click.
    print("EXAMPLE: Left click on Save push button in Save As dialog GNOME Text Editor.")
    save_as_button = editor.find_children(
        lambda x: x.name == "Save"
        and x.role_name in ("button", "push button")
    )[-1]
    save_as_button.click()
    sleep(1)

    # Let's quit now.
    print("EXAMPLE: Left click on Close push button to close GNOME Text Editor.")
    close_push_button = editor.find_child(
        lambda x: x.name == "Close" and x.role_name in ("button", "push button")
    )
    close_push_button.click()

gnome_text_editor_text_tree_api_demo()
