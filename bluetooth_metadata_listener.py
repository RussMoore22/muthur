# bluetooth_metadata_listener.py
import dbus
import dbus.mainloop.glib
from gi.repository import GLib
import json
import os
import json
import logging

# Configure logging
logging.basicConfig(
    filename="/home/rcmoore/muthur/muthur.log",
    filemode='a',
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

METADATA_FILE = "/home/rcmoore/muthur/bluetooth_metadata.json"

current_metadata = {
    "Title": "",
    "Artist": "",
    "Album": "",
    "Genre": "",
    "Duration": ""
}

def save_metadata():
    try:
        with open(METADATA_FILE, "w") as f:
            json.dump(current_metadata, f)
    except Exception as e:
        print(f"[Error saving metadata]: {e}")

def properties_changed(interface, changed, invalidated, path):
    if "Metadata" in changed:
        metadata = changed["Metadata"]
        updated = False
        for key in current_metadata:
            value = metadata.get(key)
            if value:
                current_metadata[key] = str(value)
                updated = True
        if updated:
            print("[Metadata Updated]", current_metadata)
            save_metadata()

dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
bus = dbus.SystemBus()

bus.add_signal_receiver(
    handler_function=properties_changed,
    signal_name="PropertiesChanged",
    dbus_interface="org.freedesktop.DBus.Properties",
    path_keyword="path"
)

# Optionally preload metadata file if it exists
if os.path.exists(METADATA_FILE):
    try:
        with open(METADATA_FILE) as f:
            current_metadata.update(json.load(f))
    except:
        pass

loop = GLib.MainLoop()
loop.run()