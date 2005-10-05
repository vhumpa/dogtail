#!/usr/bin/env python
# Dogtail demo script
__author__ = 'David Malcolm <dmalcolm@redhat.com>'


# Test configuring an account with the Exchange connector
#
# Assumes evolution is configured and is running

from dogtail.apps.wrappers.evolution import *

account = ExchangeAccount(fullName="John Doe",
                          emailAddress="jdoe@example.com",
                          windowsUsername=r'EXAMPLE\jdoe',
                          server='192.168.0.1',
                          urlForOWA='http://192.168.0.1',
                          password="password")
evo = EvolutionApp()
evo.createAccount(account, "test Exchange account")
