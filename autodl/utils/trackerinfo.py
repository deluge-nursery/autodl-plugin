# -*- coding: utf-8 -*-
from ..Lib.xml.etree import ElementTree as XMLParser
import re


class TrackerInfoException(Exception):
    pass


class TrackerInfo(object):
    """contain a .tracker file information"""
    def __init__(self, doc):
        """
        initialize a new TrackerInfo object
        :param doc: a string presentation of the .tracker file
        """
        root = XMLParser.fromstring(doc)
        self.settings = []
        self.servers = []
        self.type = root.attrib['type']
        self.shortName = root.attrib['shortName']
        self.longName = root.attrib['longName']

        self._parse_servers(root.find('servers'))
        self._parse_settings(root.find('settings'))

    def _parse_servers(self, servers):
        if servers is None:
            raise TrackerInfoException('No servers found')

        _server = {}
        for server in servers.iter('server'):
            _server['network'] = server.attrib['network']
            _server['serverNames'] = server.attrib['serverNames']
            _server['channelNames'] = server.attrib['channelNames']
            _server['announcerNames'] = server.attrib['announcerNames']
            self.servers.append(_server)

    def _parse_settings(self, settings):
        if settings is None:
            raise TrackerInfoException('No settings found')

        for child in settings:
            setting = {}
            for attrib_name in child.attrib:
                setting[attrib_name] = child.attrib[attrib_name]
            setting['defaultValue'] = ''
            setting['isDownloadVar'] = True
            self._init_settings(setting, child.tag)
            self.settings.append(setting)

    def _init_settings(self, setting, elem_name):
        def set_prop(name, value):
            if name not in setting or setting[name] is None:
                setting[name] = value

        if elem_name == 'gazelle_description':
            set_prop('type', 'description')
            set_prop('text', self.longName)
        elif elem_name == 'gazelle_authkey':
            set_prop('type', 'textbox')
            set_prop('name', 'authkey')
            set_prop('text', 'authkey')
            set_prop('placeholder', self.longName + ' ' + setting['name'])
            set_prop('tooltiptext', self.longName)
            set_prop('pasteGroup', 'authkey,torrent_pass')
            set_prop('pasteRegex', '[\\?&]authkey=([\\da-zA-Z]{32})')
        elif elem_name == 'gazelle_torrent_pass':
            set_prop('type', 'textbox')
            set_prop('name', 'torrent_pass')
            set_prop('text', 'torrent_pass')
            set_prop('placeholder', self.longName + ' ' + setting['name'])
            set_prop('tooltiptext', self.longName)
            set_prop('pasteGroup', 'authkey,torrent_pass')
            set_prop('pasteRegex', '[\\?&]torrent_pass=([\\da-zA-Z]{32})')
        elif elem_name == 'description':
            set_prop('type', 'description')
        elif elem_name == 'authkey':
            set_prop('type', 'textbox')
            set_prop('name', 'authkey')
            set_prop('text', 'authkey')
            set_prop('placeholder', self.longName + ' ' + setting['name'])
            set_prop('tooltiptext', self.longName)
            set_prop('pasteGroup', 'authkey')
            set_prop('pasteRegex', '[\\?&]authkey=([\\da-fA-F]{32})')
        elif elem_name == 'passkey':
            set_prop('type', 'textbox')
            set_prop('name', 'passkey')
            set_prop('text', 'passkey')
            set_prop('placeholder', self.longName + ' passkey')
            set_prop('tooltiptext', self.longName)
            set_prop('pasteGroup', 'passkey')
            set_prop('pasteRegex', '[\\?&]passkey=([\\da-fA-F]{32})')
        elif elem_name == 'cookie_description':
            set_prop('type', 'description')
            set_prop('text', '1')
        elif elem_name == 'cookie':
            set_prop('type', 'textbox')
            set_prop('name', 'cookie')
            set_prop('text', 'Cookie')
            set_prop('placeholder', self.longName + ' ' + setting['name'])
            set_prop('tooltiptext', self.longName)
        elif elem_name == 'integer':
            set_prop('type', 'integer')
            set_prop('minValue', '-999999999')
        elif elem_name == 'delta':
            set_prop('type', 'integer')
            set_prop('name', 'delta')
            set_prop('text', '2')
            set_prop('minValue', '-999999999')
        elif elem_name == 'textbox':
            set_prop('type', 'textbox')
            set_prop('placeholder', self.longName + ' ' + setting['name'])

        # if 'pasteRegex' in setting and setting['pasteRegex'] is not None:
        #    setting['pasteRegex'] = re.compile(setting['pasteRegex'])

    def get_all(self):
        tracker_info = {
            'type': self.type,
            'shortName': self.shortName,
            'longName': self.longName,
            'settings': self.settings,
            'servers': self.servers
        }
        return tracker_info
