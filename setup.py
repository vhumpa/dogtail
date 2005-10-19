#!/usr/bin/env python
__author__ = "Zack Cerza <zcerza@redhat.com>"

from distutils.core import setup
from distutils.command.bdist_rpm import bdist_rpm

def examples():
	import os
	exList = os.listdir(os.curdir + '/examples/')
	result = []
	for ex in exList:
		if ex.split('.')[-1] == 'py' and ex != 'crack.py':
			result = result + ['examples/' + ex]
	return result

def examples_data():
	import os
	dataList = os.listdir(os.curdir + '/examples/data/')
	result = []
	for data in dataList:
		if data != 'CVS':
			result = result + ['examples/data/' + data]
	return result

def icons():
	import os
	list = os.listdir(os.curdir + '/sniff/icons/')
	result = []
	for file in list:
		if file.split('.')[-1] in ('xpm'):
			result = result + ['sniff/icons/' + file]
	return result

def scripts():
	import os
	list = os.listdir(os.curdir + '/scripts/')
	result = ['sniff/sniff']
	for file in list:
		if file != 'CVS':
			result = result + ['scripts/' + file]
	return result

setup (
	name = 'dogtail',
	version = '0.4.2',
	description = """GUI test tool and automation framework that uses Accessibility (a11y) technologies to communicate with desktop applications.""",
	author = """Zack Cerza <zcerza@redhat.com>,
Ed Rousseau <rousseau@redhat.com>, 
David Malcolm <dmalcolm@redhat.com>""",
	author_email = 'dogtail-maint@gnome.org',
	url = 'http://people.redhat.com/zcerza/dogtail/',
	packages = ['dogtail', 'dogtail.apps', 'dogtail.apps.wrappers'],
	scripts = scripts(),
	data_files = [
				('share/doc/dogtail/examples',
					examples() ),
				('share/doc/dogtail/examples/data', 
					examples_data() ),
				('share/dogtail/glade', ['sniff/sniff.glade']),
				('share/dogtail/icons', icons() ),
				('share/applications', ['sniff/sniff.desktop'])
				],
	cmdclass = {
		'bdist_rpm': bdist_rpm
		}
)

# vim: sw=4 ts=4 sts=4 noet ai

