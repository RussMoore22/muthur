#!/bin/bash

# --- Setup environment for PulseAudio ---
export XDG_RUNTIME_DIR="/run/user/$(id -u)"

# Kill old PulseAudio instance
pulseaudio --kill
pkill -9 pulseaudio
rm -rf "$XDG_RUNTIME_DIR/pulse"

# Start PulseAudio
pulseaudio --start
sleep 2

# Load Bluetooth modules
pactl load-module module-bluetooth-discover
pactl load-module module-bluetooth-policy

# Set HiFiBerry DAC as default sink
DAC_SINK=$(pactl list short sinks | grep 'alsa_output.platform-soc_sound' | awk '{print $1}')
if [ -n "$DAC_SINK" ]; then
    pactl set-default-sink "$DAC_SINK"
    echo "✅ Set HiFiBerry DAC as default sink: $DAC_SINK"
else
    echo "❌ Could not find HiFiBerry DAC sink."
fi

# Try to auto-connect to iPhone if previously paired
IPHONE_MAC="F4:39:A6:17:1F:"  # <-- Replace this with your phone's real MAC

echo "🔄 Attempting to connect to iPhone ($IPHONE_MAC)..."
bluetoothctl <<EOF
connect $IPHONE_MAC
EOF

sleep 5

# Move any Bluetooth audio input to the DAC
BT_INPUT=$(pactl list short sink-inputs | grep bluez | awk '{print $1}')
if [ -n "$BT_INPUT" ]; then
    echo "🔊 Moving Bluetooth input $BT_INPUT to sink $DAC_SINK"
    pactl move-sink-input "$BT_INPUT" "$DAC_SINK"
else
    echo "⚠️ No Bluetooth audio stream detected (yet)."
fi