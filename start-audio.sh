#!/bin/bash

# Ensure correct environment
export XDG_RUNTIME_DIR="/run/user/$(id -u)"

# Kill any running PulseAudio process
pulseaudio --kill
pkill -9 pulseaudio
rm -rf "$XDG_RUNTIME_DIR/pulse"

# Start PulseAudio in the background
pulseaudio --start

# Give it a moment to initialize
sleep 2

# Load Bluetooth modules
pactl load-module module-bluetooth-discover
pactl load-module module-bluetooth-policy

# Set HiFiBerry DAC as default (check with `pactl list sinks short` if needed)
DEFAULT_SINK=$(pactl list short sinks | grep 'alsa_output.platform-soc_sound' | cut -f1)
if [ -n "$DEFAULT_SINK" ]; then
    pactl set-default-sink "$DEFAULT_SINK"
    echo "✅ Default sink set to: $DEFAULT_SINK"
else
    echo "⚠️ No ALSA sink found — is HiFiBerry DAC installed and detected?"
fi

echo "✅ PulseAudio and Bluetooth audio modules initialized."