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

    def __init__(self, port, password, host=None):
        if port <= 0 or port > 65535:
            raise Exception("Invalid port {}! Initialize port in conf.php".format(port))
        if host is not None:
            self._host = host
        self._port = port
        self._password = password

    def _read_socket(self):
        data = ''
        while True:
            val = bytes(self._socket.recv(8192))
            if val == '':
                break
            data = bytes.join(data, val)
        return data

    def connect(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.SOL_TCP)
        self._socket.connect((self._host, self._port))

    def disconnect(self):
        self._socket.close()

    def send(self, data):
        data["password"] = self._password
        self._socket.sendall(json.JSONEncoder().encode(data))

    def recv(self):
        response = self._read_socket()
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
    sock.send(data=command)
