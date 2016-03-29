# This file is part of asunder.
# asunder, Copyright 2013, Jared Jennings <jjenning@fastmail.fm>.
#
# asunder is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# asunder is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with asunder.  If not, see <http://www.gnu.org/licenses/>.

import sys
import logging
import dbus
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GObject
from multiprocessing import Process, Queue
from contextlib import contextmanager

OFUD2 = 'org.freedesktop.UDisks2'
OFUD2B = OFUD2 + '.Block'
OFUD2D = OFUD2 + '.Drive'
OFDOM = 'org.freedesktop.DBus.ObjectManager'


class Device:
    def __init__(self, q, device_file_name, bus, device_name):
        self.q = q
        self.name = device_name
        self.dev = device_file_name
        self.obj = bus.get_object(OFUD2, self.name)
        self.frob = dbus.Interface(self.obj, OFUD2D)
        self.props = dbus.Interface(self.obj, dbus.PROPERTIES_IFACE)
        self.log = logging.getLogger(self.name.split('/')[-1])

    def changed(self, interface_name, changed, invalidated):
        if (
                changed.get('MediaAvailable', False) and
                changed.get('Optical', False) and
                changed.get('OpticalNumAudioTracks', 0) > 0):
            # disc with audio inserted
            self.log.info('A disc with {} audio tracks has been '
                          'inserted'.format(changed['OpticalNumAudioTracks']))
            self.q.put(self.dev)
        for k, v in changed.items():
            self.log.debug('{} is now {!r}'.format(k, v))

    def receive_changes(self, bus):
        bus.add_signal_receiver(self.changed, 'PropertiesChanged',
                'org.freedesktop.DBus.Properties', path=self.name)


def process(q):
    FORMAT = '%(asctime)-15s %(levelname)s %(name)s %(message)s'
    logging.basicConfig(format=FORMAT, stream=sys.stderr, level=logging.DEBUG)
    top = logging.getLogger(__name__)

    top.debug('beginning')
    DBusGMainLoop(set_as_default=True)

    # http://stackoverflow.com/questions/5067005/python-udisks-enumerating-device-information
    bus = dbus.SystemBus()
    ud_om_obj = bus.get_object(OFUD2, '/org/freedesktop/UDisks2')
    ud_om = dbus.Interface(ud_om_obj, OFDOM)

    top.debug('enumerating devices')
    erthing = ud_om.GetManagedObjects()
    for name, info in erthing.items():
        for interface_name, bga in info.items():
            if interface_name == OFUD2B:
                device_file_name = bytes(bga['Device']).rstrip(b'\x00').decode('ascii')
                drive_path = bga['Drive']
                if drive_path != '/': # if it is, this Block has no Drive
                    dga = erthing[drive_path][OFUD2D]
                    if (
                            dga['MediaRemovable'] and
                            dga['MediaChangeDetected'] and 
                            any(z.startswith('optical')
                                for z in dga['MediaCompatibility'])):
                        top.info('removable drive {}'.format(device_file_name))
                        d = Device(q, device_file_name, bus, drive_path)
                        d.receive_changes(bus)
    loop = GObject.MainLoop()
    loop.run()

@contextmanager
def disc_inserted_queue():
    q = Queue()
    p = Process(target=process, args=(q,))
    p.start()
    yield q
    q.close()
    p.terminate()

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    process(None)
