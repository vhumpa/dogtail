#!/usr/bin/env python
# Use GCalcTool to calculate the Fibonacci series (and check the results)

import dogtail.tree
from dogtail.apps.wrappers.gcalctool import *
import dogtail.utils

dogtail.utils.run('gcalctool')
gcalctool = GCalcTool(dogtail.tree.root.application('gcalctool'))

import dogtail.config
dogtail.config.config.defaultDelay = 0.3

a = 1
b = 1

while True:
    gcalctool.clearEntry()
    gcalctool.typeNumber(a, 10)
    gcalctool.button('Add').click()
    gcalctool.typeNumber(b, 10)

    gcalctool.button('Calculate result').click()

    assert int(gcalctool.getText())==(a+b)

    a=b
    b=int(gcalctool.getText())
