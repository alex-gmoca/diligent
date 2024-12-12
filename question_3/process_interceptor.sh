#!/bin/bash

# Detect and kill existing Chromium processes
echo "Cleaning up Chromium processes..."
pkill -f "chromium"
pkill -f "chrome"
pkill -f "google-chrome"

original_command="$1"
chromium_flags="$2"

# Add custom flags to original command
modified_command="${original_command} ${chromium_flags}"
echo "Modified Command: $modified_command"
exec $modified_command