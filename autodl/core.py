#
# core.py
#
# Copyright (C) 2016 DirectorX <DirectorX@users.noreply.github.com>
# Copyright (C) 2016 DjLegolas <DjLegolas@users.noreply.github.com>
#
# Basic plugin template created by:
# Copyright (C) 2008 Martijn Voncken <mvoncken@gmail.com>
# Copyright (C) 2007-2009 Andrew Resch <andrewresch@gmail.com>
# Copyright (C) 2009 Damien Churchill <damoxc@gmail.com>
#
# Deluge is free software.
#
# You may redistribute it and/or modify it under the terms of the
# GNU General Public License, as published by the Free Software
# Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# deluge is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with deluge.    If not, write to:
# 	The Free Software Foundation, Inc.,
# 	51 Franklin Street, Fifth Floor
# 	Boston, MA  02110-1301, USA.
#
#    In addition, as a special exception, the copyright holders give
#    permission to link the code of portions of this program with the OpenSSL
#    library.
#    You must obey the GNU General Public License in all respects for all of
#    the code used other than OpenSSL. If you modify file(s) with this
#    exception, you may extend this exception to your version of the file(s),
#    but you are not obligated to do so. If you do not wish to do so, delete
#    this exception statement from your version. If you delete this exception
#    statement from all source files in the program, then also delete it here.
#

from deluge.log import LOG as log
from deluge.plugins.pluginbase import CorePluginBase
import deluge.component as component
import deluge.configmanager
from deluge.core.rpcserver import export

from utils.autodlSocket import *
from utils.configfile import ConfigFile
from utils.trackerinfo import *

DEFAULT_PREFS = {
    'port': 0,
    'password': ''
}

class Core(CorePluginBase):
    def enable(self):
        self.config = deluge.configmanager.ConfigManager("autodl.conf", DEFAULT_PREFS)
        self.port = self.config['port']
        self.password = self.config['password']
        try:
            self._socket = AutdlSocket(self.port, self.password)
            self.configfile = ConfigFile()
            self.trackerinfos = []
            self._init_data()
        except AutodlSocketException as ex:
            log.debug(ex.message)

    def disable(self):
        self.config["port"] = self.port
        self.config["password"] = self.password

    def update(self):
        pass

    @export
    def set_config(self, config):
        """Sets the config dictionary"""
        for key in config.keys():
            self.config[key] = config[key]
        self.config.save()

    @export
    def get_config(self):
        """Returns the config dictionary"""
        return self.config.config

    @export
    def get_trackers_info(self):
        """returns the trackers names dictionary"""
        trackers = []
        for tracker_info in self.trackerinfos:
            trackers.append(tracker_info.get_all())
            # trackers.append(tracker_info.longName)
        return trackers

    def _send_command(self, command):
        try:
            self._socket.connect()
            self._socket.send(command)
            response = self._socket.recv()
            self._socket.disconnect()
        except AutodlSocketConnectionRefused as excr:
            response = ''
            log.debug(excr.message)
        except AutodlSocketException:
            response = ''
            log.debug(AutodlSocketException.message)
        return response

    def _get_files_names(self):
        get_files_command = {
            'command': 'getfiles'
        }
        self._files_names = self._send_command(get_files_command)['files']

    def _init_data(self):
        self._get_files_names()
        self._init_config()
        self._init_trackers_info()

    def _init_config(self):
        get_config_file = {
            'command': 'getfile',
            'name': 'autodl.cfg'
        }
        config_file = self._send_command(get_config_file)
        self.configfile.parse(config_file)

    def _init_trackers_info(self):
        import re
        for file_name in self._files_names:
            if re.match(ur'.*(\.tracker)', file_name):
                get_tracker = {
                    'command': 'getfile',
                    'name': file_name
                }
                tracker = self._send_command(get_tracker)
                try:
                    self.trackerinfos.append(TrackerInfo(tracker['data']))
                except UnicodeEncodeError as e:
                    pass
