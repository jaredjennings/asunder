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


class Device:
    def __init__(self, q, bus, device_name):
        self.q = q
        self.name = device_name
        self.obj = bus.get_object('org.freedesktop.UDisks', self.name)
        self.frob = dbus.Interface(self.obj, 'org.freedesktop.UDisks.Device')
        self.props = dbus.Interface(self.obj, dbus.PROPERTIES_IFACE)
        self.log = logging.getLogger(self.name.split('/')[-1])
        self.last_state = None

    def is_candidate(self):
        return self.props.Get('org.freedesktop.UDisks.Device', 'DeviceIsRemovable')

    def changed(self):
        all = self.props.GetAll('org.freedesktop.UDisks.Device')
        if self.last_state is not None:
            common_keys = list(set(all.keys()) & set(self.last_state.keys()))
            changed_keys = [x for x in common_keys if all[x] != self.last_state[x]]
            disc_with_audio_inserted = True
            for propname, requirement in {
                    'DeviceIsMediaAvailable': lambda x: x == 1,
                    'DeviceIsOpticalDisc': lambda x: x == 1,
                    'OpticalDiscNumAudioTracks': lambda x: x > 0,
                }.items():
                if propname in changed_keys:
                    if not requirement(all[propname]):
                        disc_with_audio_inserted = False
                else:
                    disc_with_audio_inserted = False
            
            if disc_with_audio_inserted:
                self.q.put(str(all['DeviceFile']))
                self.log.info('A disc with {} audio tracks has been inserted'.format(all['OpticalDiscNumAudioTracks']))

            for k in changed_keys:
                self.log.debug('{}: {} -> {}'.format(k, self.last_state[k], all[k]))
        self.last_state = all

    def receive_changes(self, bus):
        bus.add_signal_receiver(self.changed, 'Changed',
                'org.freedesktop.UDisks.Device')

def process(q):
    FORMAT = '%(asctime)-15s %(levelname)s %(name)s %(message)s'
    logging.basicConfig(format=FORMAT, stream=sys.stderr, level=logging.DEBUG)
    top = logging.getLogger(__name__)

    top.debug('beginning')
    DBusGMainLoop(set_as_default=True)

    # http://stackoverflow.com/questions/5067005/python-udisks-enumerating-device-information
    bus = dbus.SystemBus()
    ud_manager_obj = bus.get_object('org.freedesktop.UDisks', '/org/freedesktop/UDisks')
    ud_manager = dbus.Interface(ud_manager_obj, 'org.freedesktop.UDisks')

    top.debug('enumerating devices')
    for path in ud_manager.EnumerateDevices():
        d = Device(q, bus, path)
        if d.is_candidate():
            top.info('removable drive {}'.format(path))
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
