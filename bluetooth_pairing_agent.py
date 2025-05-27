#!/usr/bin/env python3
import dbus
import dbus.mainloop.glib
import dbus.service
import os
from gi.repository import GLib
import logging

# Configure logging
logging.basicConfig(
    filename="/home/rcmoore/muthur/bluetooth.log",
    filemode='a',
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

AGENT_PATH = "/test/agent"
DEVICE_INTERFACE = "org.bluez.Device1"

class Agent(dbus.service.Object):
    @dbus.service.method("org.bluez.Agent1", in_signature="", out_signature="")
    def Release(self):
        logging.info("Agent released")

    @dbus.service.method("org.bluez.Agent1", in_signature="o", out_signature="s")
    def RequestPinCode(self, device):
        logging.info(f"RequestPinCode for device {device}", flush=True)
        return "0000"

    @dbus.service.method("org.bluez.Agent1", in_signature="o", out_signature="u")
    def RequestPasskey(self, device):
        logging.info(f"RequestPasskey for device {device}", flush=True)
        return dbus.UInt32(123456)

    @dbus.service.method("org.bluez.Agent1", in_signature="ou", out_signature="")
    def DisplayPasskey(self, device, passkey):
        logging.info(f"DisplayPasskey {device} {passkey}", flush=True)

    @dbus.service.method("org.bluez.Agent1", in_signature="os", out_signature="")
    def AuthorizeService(self, device, uuid):
        logging.info(f"AuthorizeService {device} {uuid}", flush=True)
        return

    @dbus.service.method("org.bluez.Agent1", in_signature="os", out_signature="")
    def RequestConfirmation(self, device, passkey):
        logging.info(f"Confirming passkey {passkey} for {device}", flush=True)
        return

    @dbus.service.method("org.bluez.Agent1", in_signature="", out_signature="")
    def Cancel(self):
        logging.info("Pairing cancelled", flush=True)

def setup_bluetooth():
    bus = dbus.SystemBus()
    manager = dbus.Interface(bus.get_object("org.bluez", "/org/bluez"), "org.bluez.AgentManager1")
    adapter = dbus.Interface(bus.get_object("org.bluez", "/org/bluez/hci0"), "org.freedesktop.DBus.Properties")

    # Ensure adapter is discoverable, powered, and pairable
    adapter.Set("org.bluez.Adapter1", "Powered", dbus.Boolean(1))
    adapter.Set("org.bluez.Adapter1", "DiscoverableTimeout", dbus.UInt32(0))
    adapter.Set("org.bluez.Adapter1", "Discoverable", dbus.Boolean(1))
    adapter.Set("org.bluez.Adapter1", "Pairable", dbus.Boolean(1))

    agent = Agent(bus, AGENT_PATH)
    manager.RegisterAgent(AGENT_PATH, "NoInputNoOutput")
    manager.RequestDefaultAgent(AGENT_PATH)

    print("Bluetooth pairing agent running...")
    GLib.MainLoop().run()

if __name__ == "__main__":
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    setup_bluetooth()