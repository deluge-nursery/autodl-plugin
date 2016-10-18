# -*- coding: utf-8 -*-
import socket
import json


class SocketException(Exception):
    pass


class AutdlSocket:
    _socket = None
    _port = 0
    _host = "127.0.0.1"
    _password = ""

    def __init__(self, port, password):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.SOL_TCP)
        if port <= 0 or port > 65535:
            raise Exception("Invalid port {}! Initialize port in conf.php".format(port))
        self._port = port
        self._password = password

    @staticmethod
    def _read_socket(_socket):
        data = ''
        while True:
            val = bytes(_socket.recv(4096))
            if val == '':
                break
            data = bytes.join(data, val)
        return data

    def send_autodl_command(self, data):
        self._socket.connect((self._host, self._port))
        data["password"] = self._password
        self._socket.sendall(json.JSONEncoder().encode(data))
        response = self._read_socket(self._socket)
        self._socket.close()
        json_response = json.JSONDecoder().decode(response)
        return json_response

if __name__ == "__main__":
    sock = AutdlSocket(23875, 'gO4#&aXMb6mMOB')
    commands = {
        'command': 'command',
        'getfiles': 'getfiles',
        'getfile': 'getfile',
        'writeconfig': 'writeconfig',
        'getlines': 'getlines'
    }

    command_type_autodl = {
        'update': 'update',
        'whatsnew': 'whatsnew',
        'version': 'version',
        # 'reload': 'reload',
        'reloadtrackers': 'reloadtrackers'
    }

    command_type_irc = {

    }

    getfile_name = {
        'autodl.cfg': 'autodl.cfg',
        'tracker': '*.tracker'
    }

    get_files = {}

    write_config_data = {
        'data': ''
    }

    getlines = {
        'cid': 5
    }

    command = {
        'command': commands['getfile'],
        'name': 'autodl.cfg'
    }
    sock.send_autodl_command(data=command)
