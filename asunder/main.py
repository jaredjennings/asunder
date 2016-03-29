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
import time
import getopt
import os.path
from asunder.detect.via_udisks2 import disc_inserted_queue
from asunder.notify.via_sleekxmpp import notify_queue
from multiprocessing import Process
from asunder.do_rip import do_rip
from ConfigParser import SafeConfigParser
import xdg.BaseDirectory

def usage():
    print >> sys.stderr, """
Usage: {progname}

Waits for audio CDs to be inserted into any drive; rips them into directories
named after the time of ripping; ejects them. Each rip happens in a subprocess
so multiple rips can be going on at the same time if you have multiple drives.
Notifies you when a disc is finished, via Jabber.

"""

def rip_forever(config):
    jid = config.get('notify', 'jid')
    password = config.get('notify', 'password')
    notify_jids = config.get('notify', 'to')
    with disc_inserted_queue() as dq:
        with notify_queue(jid, password, notify_jids) as nq:
            logging.info('waiting for everything to start up')
            time.sleep(10)
            processes = []
            while True:
                top.info('waiting for inserted disc')
                device = dq.get()
                top.info('device {!s} has disc, starting rip'.format(device))
                p = Process(target=do_rip, args=(device, nq))
                p.start()

def main():
    loglevel = logging.INFO
    ovpairs, rest = getopt.getopt(sys.argv[1:], 'v', ['help'])
    for o, v in ovpairs:
        if o == '-v':
            loglevel = logging.DEBUG
        if o == '--help':
            usage()
            sys.exit(1)
    logging.basicConfig(level=loglevel)
    log = logging.getLogger('script')
    config = SafeConfigParser()
    config_dir = xdg.BaseDirectory.load_first_config('asunder')
    config_file = os.path.join(config_dir, 'config.ini')
    log.debug('reading configuration from file {}'.format(config_file))
    with file(config_file) as f:
        config.readfp(f)
    rip_forever(config)

if __name__ == '__main__':
    main()
