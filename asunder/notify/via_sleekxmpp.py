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

import time
import logging
from multiprocessing import Process, Queue
from contextlib import contextmanager

from sleekxmpp import ClientXMPP
from sleekxmpp.exceptions import XMPPError
from sleekxmpp.stanza import Message


class Notify(ClientXMPP):
    def __init__(self, jid, password):
        super(Notify, self).__init__(jid, password)
        self.add_event_handler("session_start", self.session_start)

    def session_start(self, event):
        self.send_presence()
        self.get_roster()

def process(q, jid, password, notify_jids):
    logging.basicConfig(level=logging.INFO,
                        format='%(levelname)-8s %(message)s')
    n = Notify(jid, password)
    n.connect()
    # process starts another thread, i believe
    n.process()
    while True:
        # this blocks
        content = q.get()
        for to in notify_jids:
            m = n.Message()
            m['to'] = to
            m['type'] = 'chat'
            # FIXME? we assume that message is valid as XML
            m['body'] = content
            n.send(m)


@contextmanager
def notify_queue(jid, password, notify_jids):
    q = Queue()
    p = Process(target=process, args=(q, jid, password, notify_jids))
    p.start()
    yield q
    q.close()
    p.terminate()
