#!/bin/bash

STATE_FILE="/tmp/initial-reboot-done"

if [ -f "$STATE_FILE" ]; then
    echo "Initial reboot has been performed."
    rm -f "$STATE_FILE"
    exit 0 # Exit successfully after reboot
else
    echo "Triggering initial reboot now..."
    touch "$STATE_FILE"
    reboot
fi