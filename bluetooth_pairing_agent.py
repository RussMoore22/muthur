#!/usr/bin/env python3
import dbus
import dbus.service
import dbus.mainloop.glib
from gi.repository import GLib
import json
import logging

# Configure logging
logging.basicConfig(
    filename="/home/rcmoore/muthur/muthur.log",
    filemode='a',
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

AGENT_PATH = "/test/agent"

class Agent(dbus.service.Object):
    @dbus.service.method("org.bluez.Agent1", in_signature="", out_signature="")
    def Release(self):
        print("Release")

    @dbus.service.method("org.bluez.Agent1", in_signature="o", out_signature="s")
    def RequestPinCode(self, device):
        print(f"RequestPinCode for device {device}")
        return "0000"

    @dbus.service.method("org.bluez.Agent1", in_signature="ouq", out_signature="")
    def DisplayPasskey(self, device, passkey, entered):
        logging.info("DisplayPasskey %s passkey: %06d", device, passkey)
        with open("/tmp/bluetooth_code.json", "w") as f:
            json.dump({"Passkey": f"{passkey:06d}"}, f)

    @dbus.service.method("org.bluez.Agent1", in_signature="os", out_signature="")
    def RequestConfirmation(self, device, passkey):
        logging.info("RequestConfirmation %s code: %06d", device, int(passkey))
        with open("/tmp/bluetooth_code.json", "w") as f:
            json.dump({"Passkey": f"{int(passkey):06d}"}, f)
        return  # Auto-confirm

    @dbus.service.method("org.bluez.Agent1", in_signature="os", out_signature="")
    def AuthorizeService(self, device, uuid):
        print(f"AuthorizeService: {uuid} for {device}")

    @dbus.service.method("org.bluez.Agent1", in_signature="os", out_signature="")
    def RequestConfirmation(self, device, passkey):
        print(f"Confirming passkey {passkey} for {device}")
        return  # Accept pairing

    @dbus.service.method("org.bluez.Agent1", in_signature="", out_signature="")
    def Cancel(self):
        print("Pairing Cancelled")

def main():
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()

    obj = bus.get_object("org.bluez", "/org/bluez")
    manager = dbus.Interface(obj, "org.bluez.AgentManager1")

    agent = Agent(bus, AGENT_PATH)
    manager.RegisterAgent(AGENT_PATH, "KeyboardDisplay")
    manager.RequestDefaultAgent(AGENT_PATH)

    print("Bluetooth pairing agent running...")
    GLib.MainLoop().run()

if __name__ == "__main__":
    main()