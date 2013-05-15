# This file is part of asunder.
# asunder, Copyright 2013, Jared Jennings <jjennings@fastmail.fm>.
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

import logging
import time
import subprocess
import shutil
from morituri.rip import main as morituri_main

def do_rip(device, notify_queue):
    log = logging.getLogger('do_rip')
    thetime = str(int(time.time()))
    log.info('ripping to directory {!s}'.format(thetime))
    try:
        morituri_main.main(['cd', '-d', device, 'rip', '--track-template={}/track%t'.format(thetime), '--disc-template={}/disc'.format(thetime)])
    except Exception as e:
        notify_queue.put('rip failed on device {}'.format(device))
        log.exception('Some error happened ripping {}; removing'.format(thetime))
        try:
            shutil.rmtree(thetime)
        except OSError as e:
            if e.errno == errno.ENOENT:
                # it didn't exist. no sweat
                pass
            else:
                log.exception('Some error happened cleaning up {}'.format(thetime))
    log.info('ejecting {}'.format(device))
    try:
        subprocess.check_call(('eject', device))
    except subprocess.CalledProcessError:
        log.info('eject exited with error; continuing')
    log.info('notifying')
    notify_queue.put('please insert another disc into {}'.format(device))


