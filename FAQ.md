# FAQ, lessons learned and expected usage, for example based on Issues filed.

### Why is the find_ancestor (findAncestor) method not compatible.
  - In dogtail-1.x.y this was a simple function that returned None if nothing was discovered when traversing the tree upwards.
  - Now to keep the same logic you have to use `find_ancestor(<predicate>, require_result=False, retry=False)` since it will attempt to find positive result the same way the find_child function will.


### Why was procedure.py removed?
  - This is no longer supported way to use the API.
  - Confusing usage which I have removed in favor of tree based approach.


### Why was sniff removed?
  - There are better alternatives out there
  - We have no reason to keep our own version with as limited resources as we have.
  - Try to use the `.tree()` method over your Accessible objects to find what you are searching for.


### Why was X/Y removed?
  - If there is a module or function that was frequently used and it broke your code, file an Issue.
  - I will either explain why it happened and what are the alternatives.
  - Or I will make sure to re-implement the feature back, since my approach to refactoring dogtail to 2.x.y was to remove anything I have never touched and deemed obsolete.


### We do support long key presses: https://gitlab.com/dogtail/dogtail/-/issues/42
  - Documentation is not complete, try to first go through the API on your own to see if the function exists. Most likely you will want to look through two files.
    - tree.py
    - rawinput.py


### Assistive technology can appear as if it was not enabled and failing on it: https://gitlab.com/dogtail/dogtail/-/issues/44
  - If your distribution has a different way to enable Accessibility than we are checking, turn of the check that dogtail does so you are not blocked:
  - Expected in dogtail-1.x - needs to be worked around.
  - Does not happen with dogtail-2.x - no such check present.
  - `config.check_for_a11y = False`


### The `get_accessible_id` is supported in dogtail-2.x.y: https://gitlab.com/dogtail/dogtail/-/issues/45
  - Based on user need I have added the logic, but I am not backporting it to dogtail-1.x.y
  - We do accept contributions though, if required you can open MR with this logic for the dogtail-1.x.y branch.


### Not all keyboard key events are in a format you would expect: https://gitlab.com/dogtail/dogtail/-/issues/48
  - We are not making our own key aliases usually, but it is possible.
  - If some format is not working, try to go through the Issue to look how the keys in GDK look and try to use those.
  - We can create aliases if required.


### Version from __version__ might not be accurate when building with setuptools-scm: https://gitlab.com/dogtail/dogtail/-/issues/36
  - I will try to find a solution if this problem remains after official release.
  - I had issues trying to make this work with devX versions.


### The role name `push button` no longer works: https://gitlab.com/dogtail/dogtail/-/issues/35
  - This was changed some time ago, now the role name is named `button`.


### You are getting NotImplementedErrorL https://gitlab.com/dogtail/dogtail/-/issues/34
  - Try to see if your object has this interface implemented, as this is most likely reason why this happens.

