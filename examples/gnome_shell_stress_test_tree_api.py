#!/usr/bin/python3

"""
Example of working with GNOME Shell, running clicks in loop.
"""

from dogtail.tree import root

def gnome_shell_stress_test_tree_api():
    """
    Run click to GNOME Shell in loop.
    """

    shell = root.application("gnome-shell")

    # Search the tree only once and use the object afterwards for clicks.
    activities_toggle_button = shell.child("Activities", "toggle button")
    system_menu = shell.child("System", "menu")

    for iteration in range(100):
        print(f"Iteration '{iteration}' - click on Activities toggle button.")

        # Depending on the initial state, first click will open and second will close.
        # Or wise versa.
        activities_toggle_button.click()
        activities_toggle_button.click()

        print(f"Iteration '{iteration}' - click on System menu.")
        # First click will open the menu.
        system_menu.click()
        # Second click will close the menu.
        system_menu.click()

gnome_shell_stress_test_tree_api()
