# -*- coding: utf-8 -*-
import xml.etree.ElementTree as XMLParser
import re


class TrackerInfo(object):
    type = None
    shortName = None
    longName = None
    settings = []
    servers = []

    def __init__(self, doc):
        root = XMLParser.fromstring(doc)
        self.type = root.attrib['type']
        self.shortName = root.attrib['shortName']
        self.longName = root.attrib['longName']

        self._parse_servers(root.find('servers'))
        self._parse_settings(root.find('settings'))

    def _parse_servers(self, servers):
        if servers is None:
            raise 'No servers found'

        _server = {}
        for server in servers.iter('server'):
            _server['network'] = server.attrib['network']
            _server['serverNames'] = server.attrib['serverNames']
            _server['channelNames'] = server.attrib['channelNames']
            _server['announcerNames'] = server.attrib['announcerNames']
            self.servers.append(_server)

    def _parse_settings(self, settings):
        if settings is None:
            raise 'No settings found'

        for child in settings:
            setting = {}
            for attrib_name in child.attrib:
                setting[attrib_name] = child.attrib[attrib_name]
            setting['defaultValue'] = ''
            setting['isDownloadVar'] = True
            self._test(setting, child.tag)
            self.settings.append(setting)

    def _test(self, setting, elemName):
        def set_prop(name, value):
            if name not in setting or setting[name] is None:
                setting[name] = value

        if elemName == 'gazelle_description':
            set_prop('type', 'description')
            set_prop('text', self.longName)
        elif elemName == 'gazelle_authkey':
            set_prop('type', 'textbox')
            set_prop('name', 'authkey')
            set_prop('text', 'authkey')
            set_prop('placeholder', self.longName + ' ' + setting['name'])
            set_prop('tooltiptext', self.longName)
            set_prop('pasteGroup', 'authkey,torrent_pass')
            set_prop('pasteRegex', '[\\?&]authkey=([\\da-zA-Z]{32})')
        elif elemName == 'gazelle_torrent_pass':
            set_prop('type', 'textbox')
            set_prop('name', 'torrent_pass')
            set_prop('text', 'torrent_pass')
            set_prop('placeholder', self.longName + ' ' + setting['name'])
            set_prop('tooltiptext', self.longName)
            set_prop('pasteGroup', 'authkey,torrent_pass')
            set_prop('pasteRegex', '[\\?&]torrent_pass=([\\da-zA-Z]{32})')
        elif elemName == 'description':
            set_prop('type', 'description')
        elif elemName == 'authkey':
            set_prop('type', 'textbox')
            set_prop('name', 'authkey')
            set_prop('text', 'authkey')
            set_prop('placeholder', self.longName + ' ' + setting['name'])
            set_prop('tooltiptext', self.longName)
            set_prop('pasteGroup', 'authkey')
            set_prop('pasteRegex', '[\\?&]authkey=([\\da-fA-F]{32})')
        elif elemName == 'passkey':
            set_prop('type', 'textbox')
            set_prop('name', 'passkey')
            set_prop('text', 'passkey')
            set_prop('placeholder', self.longName + ' passkey')
            set_prop('tooltiptext', self.longName)
            set_prop('pasteGroup', 'passkey')
            set_prop('pasteRegex', '[\\?&]passkey=([\\da-fA-F]{32})')
        elif elemName == 'cookie_description':
            set_prop('type', 'description')
            set_prop('text', '1')
        elif elemName == 'cookie':
            set_prop('type', 'textbox')
            set_prop('name', 'cookie')
            set_prop('text', 'Cookie')
            set_prop('placeholder', self.longName + ' ' + setting['name'])
            set_prop('tooltiptext', self.longName)
        elif elemName == 'integer':
            set_prop('type', 'integer')
            set_prop('minValue', '-999999999')
        elif elemName == 'delta':
            set_prop('type', 'integer')
            set_prop('name', 'delta')
            set_prop('text', '2')
            set_prop('minValue', '-999999999')
        elif elemName == 'textbox':
            set_prop('type', 'textbox')
            set_prop('placeholder', self.longName + ' ' + setting['name'])

        if 'pasteRegex' in setting and setting['pasteRegex'] is not None:
            setting['pasteRegex'] = re.compile(setting['pasteRegex'])
