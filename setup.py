#!/usr/bin/env python
__author__ = "Zack Cerza <zcerza@redhat.com>"

from distutils.core import setup
from distutils.command.bdist_rpm import bdist_rpm

def examples():
    import os
    exList = os.listdir(os.curdir + '/examples/')
    result = []
    for ex in exList:
        if ex.split('.')[-1] == 'py':
            result = result + ['examples/' + ex]
    return result

def examples_data():
    import os
    dataList = os.listdir(os.curdir + '/examples/data/')
    result = []
    for data in dataList:
		result = result + ['examples/data/' + data]
    return result

def tests():
    import os
    exList = os.listdir(os.curdir + '/tests/')
    result = []
    for ex in exList:
        if ex.split('.')[-1] == 'py':
            result = result + ['tests/' + ex]
    return result

def sniff_icons():
    import os
    list = os.listdir(os.curdir + '/sniff/icons/')
    result = []
    for file in list:
        if file.split('.')[-1] in ('xpm'):
            result = result + ['sniff/icons/' + file]
    return result

def icons(ext_tuple):
    import os
    list = os.listdir(os.curdir + '/icons/')
    result = []
    for file in list:
        if file.split('.')[-1] in ext_tuple:
            result = result + ['icons/' + file]
    return result

def scripts():
    import os
    list = os.listdir(os.curdir + '/scripts/')
    result = ['sniff/sniff']
    for file in list:
		result = result + ['scripts/' + file]
    return result

def session_file():
    result = ['scripts/gnome-dogtail-headless.session']
    return result

setup (
        name = 'dogtail',
        version = '0.9.0',
        description = """GUI test tool and automation framework that uses Accessibility (a11y) technologies to communicate with desktop applications.""",
        author = """Zack Cerza <zcerza@redhat.com>,
Ed Rousseau <rousseau@redhat.com>,
David Malcolm <dmalcolm@redhat.com>
Vitezslav Humpa <vhumpa@redhat.com>""",
        author_email = 'dogtail-list@gnome.org',
        url = 'http://dogtail.fedorahosted.org/',
        packages = ['dogtail'],
        scripts = scripts(),
        data_files = [
                                ('share/doc/dogtail/examples',
                                        examples() ),
                                ('share/doc/dogtail/examples/data',
                                        examples_data() ),
                                ('share/doc/dogtail/tests',
                                        tests() ),
                                ('share/dogtail/glade', ['sniff/sniff.ui']),
                                ('share/dogtail/icons', sniff_icons() ),
                                ('share/applications', ['sniff/sniff.desktop']),
                                ('share/icons/hicolor/48x48/apps', icons('png')),
                                ('share/icons/hicolor/scalable/apps', icons('svg'))
                                ],
        cmdclass = {
                'bdist_rpm': bdist_rpm
                }
)

# vim: sw=4 ts=4 sts=4 noet ai
