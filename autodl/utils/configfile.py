# -*- coding: utf-8 -*-
import common
import re


def sort_object_by_id(obj):
    array = []
    for key in obj:
        array.append(obj[key])

    def compare(a, b):
        return common.string_compare(a.id, b.id)
    array.sort(cmp=compare)
    return array


def canonicalize_server_name(server_name):
    array = re.match(ur'^([^:]*)', server_name)
    return array.group(1).lower()


class ConfigOption:
    def __init__(self, _id, _name, _value, _default_value=None, _option_type=None):
        self.type = 'option'
        self.id = _id
        self.name = _name.strip()
        self.value = _value.strip()
        self.defaultValue = _default_value
        self.optionType = _option_type

    def __str__(self):
        if self.defaultValue is not None:
            value = self.get_value()
            default_value = self._get_value(self.optionType, self.defaultValue, self.defaultValue)
            if value == default_value:
                return None
        return self.name + ' = ' + self.value

    @staticmethod
    def _get_value(_option_type, _value, _default_value):
        if _option_type == 'bool':
            return common.convert_string_to_bool(_value)
        if _option_type == 'int':
            return common.convert_string_to_integer(_value, _default_value)
        return _value

    def clone(self):
        return ConfigOption(self.id, self.name, self.value, self.defaultValue, self.optionType)

    def get_value(self):
        return self._get_value(self.optionType, self.value, self.defaultValue)

    def set_default_value(self, default_value, option_type):
        if default_value is not None:
            self.defaultValue = default_value
        if option_type is not None:
            self.optionType = option_type

    def set_value(self, value):
        self.value = str(value)


class ConfigComment:
    def __init__(self, _id, _name, _line):
        self.type = 'comment'
        self.id = _id
        self.name = _name
        self.value = _line

    def clone(self):
        return ConfigComment(self.id, self.name, self.value)

    def __str__(self):
        return self.value


class ConfigSection:
    def __init__(self, _id, _type, _name):
        self.id = _id
        self.type = _type.strip()
        try:
            self.name = _name.strip()
        except AttributeError:
            self.name = None
        self.nextId = 0
        self.lines = {}
        self.printEmpty = True

    def __str__(self):
        out = ''
        out += '[' + self.type
        if self.name:
            out += ' ' + self.name
        out += ']\n'

        array = sort_object_by_id(self.lines)
        opts = ''
        for element in array:
            s = str(element)
            if s is not None:
                opts += s + '\n'

        if not self.printEmpty and opts == '':
            return None
        return out + opts

    def dont_print_empty(self):
        self.printEmpty = False

    def clone(self):
        clone = ConfigSection(self.id, self.type, self.name)
        clone.nextId = self.nextId
        for key in self.lines:
            line = self.lines[key]
            clone.lines[key] = line.clone()
        return clone

    def add_option(self, name, value):
        option = ConfigOption(self.nextId, name, value)
        self.nextId += 1
        self.lines[option.name] = option

    def add_comment(self, line):
        _id = self.nextId
        self.nextId += 1
        name = ' comment {}'.format(_id)
        comment = ConfigComment(_id, name, line)
        self.lines[comment.name] = comment

    def get_option(self, name, default_value, _type):
        _hash = name.strip()
        option = self.lines[_hash]
        if not option:
            self.lines[_hash] = option = ConfigOption(self.nextId, name, default_value)
            self.nextId += 1
        option.set_default_value(default_value, _type)
        return option


class ConfigFile:
    """a container for the config file"""
    def __init__(self):
        """
        initialize the config container
        """
        self._sections = {}
        self._filters = []
        self._id = 0

    def __str__(self):
        out = ''
        sections_array = sort_object_by_id(self._sections)
        for section in sections_array:
            s = str(section)
            if s is None:
                continue
            if out != '':
                out += '\n'
            out += s
        return out

    def parse(self, content):
        """
        Parse a JSON response containing an autodl.cfg file
        :param content: a JSON string with 'data' field containing autodl.cfg
        """
        self._sections = {}
        self._filters = []
        section = None

        def error(msg):
            print('autodl.cfg: line {}: {}'.format(i + 1, msg))
            # log('autodl.cfg: line {}: {}'.format(i + 1, msg))

        first_prog = re.compile(ur'^\[\s*([\w\-]+)\s*(?:([^\]]+))?\s*]$')
        second_prog = re.compile(ur'^([\w\-]+)\s*=(.*)$')
        lines = content['data'].split('\n')
        for line in lines:
            i = 0
            line = line.strip()
            if line == '':
                continue

            first_array = first_prog.match(line)
            second_array = second_prog.match(line)
            if line[0] == '#':
                if section:
                    section.add_comment(line)
            elif first_array:
                _type = first_array.group(1).strip().lower()
                try:
                    _name = first_array.group(2).strip().lower()
                except AttributeError:
                    _name = None
                section = self.get_section(_type, _name)
            elif second_array:
                if section is None:
                    error('Missing a [section]')
                else:
                    _option = second_array.group(1).strip().lower()
                    _value = second_array.group(2).strip().lower()
                    section.add_option(_option, _value)
            else:
                error('Ignoring line')
            i += 1

    @staticmethod
    def _filter_hash(filter_section):
        return '{} {}'.format(filter_section.type.strip(), filter_section.id)

    @staticmethod
    def _server_hash(server_name):
        return ' server {}'.format(canonicalize_server_name(server_name))

    def _channel_hash(self, channel_name):
        data = ' channel {} {}'.format(self._id, channel_name.lower())
        self._id += 1
        return data

    def get_section(self, _type, _name):
        """
        returns a section
        :param _type: section type. can be filter, options, tracker, server, channel
        :param _name: section name
        :return: the wanted section
        """
        if _type == 'filter':
            section = ConfigSection(self._id, _type, _name)
            self._id += 1
            self._filters.append(section)
            _hash = self._filter_hash(section)
            self._sections[_hash] = section
            return section
        elif _type == 'options' or _type == 'webui' or _type == 'ftp' or _type == 'irc':
            return self._get_or_create_section(_type, _name, _type.strip())
        elif _type == 'tracker':
            return self._get_or_create_section(_type, _name, _type.strip() + " " + _name.strip())
        elif _type == 'server':
            return self._get_or_create_section(_type, _name, self._server_hash(_name.strip()))
        elif _type == 'channel':
            return self._get_or_create_section(_type, _name, self._channel_hash(_name.strip()))
        else:
            data = self._get_or_create_section(_type, _name, ' unknown {} {} {}'.format(self._id, _type.strip(),
                                                                                        _name.strip()))
            self._id += 1
            return data

    def _get_or_create_section(self, _type, _name, _hash):
        try:
            section = self._sections[_hash]
        except KeyError:
            section = None
        if section is None:
            self._sections[_hash] = section = ConfigSection(self._id, _type, _name)
            self._id += 1
        return section

    def get_filters(self):
        """
        return all filters
        :return: list of filters
        """
        return self._filters

    def _remove_filters(self):
        for _filter in self._filters:
            _hash = self._filter_hash(_filter)
            del self._sections[_hash]
        self._filters = []

    def _init_section_id(self, section):
        if section.id is None:
            section.id = self._id
            self._id += 1

    def set_filters(self, sections):
        """
        reinitialize all filters
        :param sections: list of filters to init
        """
        self._remove_filters()
        for section in sections:
            self._init_section_id(section)
            _hash = self._filter_hash(section)
            self._sections[_hash] = section
        self._filters = sections

    def get_irc_servers(self):
        """
        get all irc servers
        :return: list of servers and their channels
        """
        servers = {}

        def get_server_info(server_name):
            server_name = canonicalize_server_name(server_name)

            try:
                server_info = servers[server_name]
            except KeyError:
                servers[server_name] = server_info = {
                    'channels': []
                }

            return server_info

        for key, value in self._sections.iteritems():
            section = self._sections[key]
            if re.match(ur'^ server ', key):
                server_info = get_server_info(section.name)
                server_info['server'] = section
            elif re.match(ur'^ channel ', key):
                server_info = get_server_info(section.name)
                server_info['channels'].append(section)

        rv = []
        for key, value in servers.iteritems():
            server_info = servers[key]
            if 'server' in server_info:
                rv.append(server_info)
        return rv

    def remove_servers_channels(self):
        """
        remove all servers and channels from config
        """
        for _hash in self._sections.keys():
            if not re.match(ur'^ server ', _hash) and not re.match(ur'^ channel ', _hash):
                continue
            del self._sections[_hash]

    def set_servers(self, server_infos):
        """
        reinitialize all servers and their channels
        :param server_infos: list of servers and their channels
        """
        self.remove_servers_channels()
        for server_info in server_infos:
            server_section = server_info['server']
            server_name = server_section.name
            self._init_section_id(server_section)
            self._sections[self._server_hash(server_name)] = server_section

            for channel_section in server_info['channels']:
                if channel_section is None:
                    continue
                channel_section.name = server_name
                self._init_section_id(channel_section)
                self._sections[self._channel_hash(server_name)] = channel_section
