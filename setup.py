#!/usr/bin/env python
__author__ = "Zack Cerza <zcerza@redhat.com>"

from distutils.core import setup
from distutils.command.bdist_rpm import bdist_rpm

setup (
	name = 'dogtail',
	version = '0.4',
	description = """GUI test tool and automation framework that uses Accessibility (a11y) technologies to communicate with desktop applications.""",
	author = """Zack Cerza <zcerza@redhat.com>,
Ed Rousseau <rousseau@redhat.com>, 
David Malcolm <dmalcolm@redhat.com>""",
	author_email = 'dogtail-maint@gnome.org',
	url = 'http://gnome.org/projects/dogtail/',
	packages = ['dogtail', 'dogtail.apps', 'dogtail.apps.wrappers'],
	scripts = ['sniff/sniff'],
	data_files = [
				('share/doc/dogtail/examples',
					['examples/gedit-test-utf8-procedural-api.py']),
				('share/doc/dogtail/examples/data', 
					['examples/data/UTF-8-demo.txt']),
				('share/dogtail/glade', ['sniff/sniff.glade']),
				('share/applications', ['sniff/sniff.desktop'])
				],
	cmdclass = {
		'bdist_rpm': bdist_rpm
		}
)

# vim: sw=4 ts=4 sts=4 noet ai

