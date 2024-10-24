#!/usr/bin/env python
__author__ = "Zack Cerza <zcerza@redhat.com>"

from setuptools import setup

def examples():
    import os
    ex_list = os.listdir(os.curdir + '/examples/')
    result = []
    for ex in ex_list:
        if ex.split('.')[-1] == 'py':
            result = result + ['examples/' + ex]
    return result

def examples_data():
    import os
    data_list = os.listdir(os.curdir + '/examples/data/')
    result = []
    for data in data_list:
        result = result + ['examples/data/' + data]
    return result

def tests():
    import os
    ex_list = os.listdir(os.curdir + '/tests/')
    result = []
    for ex in ex_list:
        if ex.split('.')[-1] == 'py':
            result = result + ['tests/' + ex]
    return result

def sniff_icons():
    import os
    list = os.listdir(os.curdir + '/sniff/icons/')
    result = []
    for file in list:
        if file.split('.')[-1] in ('png'):
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

with open("README.rst", "r") as fh:
    long_desc = fh.read()

setup(
    name='dogtail',
    version='1.0.2',
    description="GUI test tool and automation framework " +
    "that uses Accessibility (a11y) technologies to " +
    "communicate with desktop applications.",
    long_description_content_type="text/x-rst",
    long_description=long_desc,
    author="""Zack Cerza <zcerza@redhat.com>,
Ed Rousseau <rousseau@redhat.com>,
David Malcolm <dmalcolm@redhat.com>,
Vitezslav Humpa <vhumpa@redhat.com>,
Michal Odehnal <modehnal@redhat.com>""",
    author_email='dogtail-list@gnome.org',
    url='https://gitlab.com/dogtail/dogtail',
    packages=['dogtail'],
    scripts=scripts(),
    data_files=[
        ('share/doc/dogtail/examples',
        examples()),
        ('share/doc/dogtail/examples/data',
        examples_data()),
        ('share/doc/dogtail/tests',
        tests()),
        ('share/dogtail/glade', ['sniff/sniff.ui']),
        ('share/dogtail/icons', sniff_icons()),
        ('share/applications', ['sniff/sniff.desktop']),
        ('share/icons/hicolor/scalable/apps', icons('svg'))
    ],
    options = {
    'build_scripts': {
        'executable': '/usr/bin/python3',
    }
}
)

# vim: sw=4 ts=4 sts=4 noet ai
