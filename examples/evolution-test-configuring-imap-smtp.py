#!/usr/bin/env python
# Dogtail demo script
__author__ = 'David Malcolm <dmalcolm@redhat.com>'


# Test configuring an IMAP and SMTP account
#
# Assumes evolution is configured and is running

from dogtail.apps.wrappers.evolution import *

account = MixedAccount(fullName="John Doe",
                       emailAddress="jdoe@example.com",
                       receiveMethod = IMAPSettings(server="mail.example.com",
                                                    username="jdoe",
                                                    useSecureConnection=UseSecureConnection.ALWAYS,
                                                    authenticationType="password"),
                       sendMethod = SMTPSettings(server="smtp.example.com",
                                                 useSecureConnection=UseSecureConnection.NEVER))
evo = EvolutionApp()
evo.createAccount(account, "test IMAP/SMTP account")
