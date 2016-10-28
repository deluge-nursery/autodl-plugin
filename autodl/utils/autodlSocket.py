# -*- coding: utf-8 -*-
import socket
import json
import errno


class AutodlSocketException(Exception):
    def __init__(self, message):
        self.message = message


class AutodlSocketConnectionRefused(AutodlSocketException):
    def __init__(self):
        self.message = 'Unable to connect to autodl-irssi'


class AutdlSocket:
    """A socket handler for all autodl-irssi communications"""
    _socket = None
    _port = 0
    _host = "127.0.0.1"
    _password = ""

    def __init__(self, port, password, host=None):
        """
        initialize a new AutodlSocket object
        :param port: the port autodl-irssi listens to
        :param password: the password of autodl-irssi
        :param host: the host to connect to. default is 127.0.0.1
        """
        if port <= 0 or port > 65535:
            raise AutodlSocketException("Invalid port {}! Initialize port in autodl.conf".format(port))
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
        """
        connects to the configured autodl
        """
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.SOL_TCP)
            self._socket.connect((self._host, self._port))
        except socket.error as exer:
            if exer.errno == errno.ECONNREFUSED:
                raise AutodlSocketConnectionRefused
            else:
                raise AutodlSocketException(exer.message)

    def disconnect(self):
        """
        closes the connection to the configured autodl
        """
        self._socket.close()

    def send(self, data):
        """
        sends command data to autodl
        :param data: a dict of the data to send
        """
        data["password"] = self._password
        self._socket.sendall(json.JSONEncoder().encode(data))

    def recv(self):
        """
        receives the response from autodl
        :return:
        """
        response = self._read_socket()
        json_response = json.JSONDecoder().decode(response)
        return json_response
