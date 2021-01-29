from bunch import Bunch
from bunch import bunchify
from zato.server.service import Service
from _00_.usuarios.service import *
import requests
import json
import sys


class Service(Service):
    def handle(self):
        self.payload = redis["Usuarios"].toJSON()