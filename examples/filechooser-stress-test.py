import sys
from dogtail.tree import root, SearchError
from dogtail.utils import run

run('gedit')

gedit = root.application('gedit')

while True:
    try:
        gedit.child('Open').click()
    except SearchError: #toolbar not present?
        gedit.child('Open...').click()

    try:
        filechooser = gedit.child(name='Open Files', roleName='file chooser')
        filechooser.childNamed('Cancel').click()
    except SearchError:
        print('File chooser did not open')
        sys.exit(1)
