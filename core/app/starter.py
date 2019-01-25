#!/usr/bin/env python3


from flask import Flask, jsonify, redirect
from flask_restful import Api, Resource, request
from .configuration import configuration
from .SecurityHandler import SecurityHandler


app = Flask(__name__)
app.api = Api(app)
app.configuration = configuration


app.security_handler = SecurityHandler
app.security_handler.token = app.configuration['security_token']
if 'client_timeout_hours' in configuration:
  app.security_handler.client_timeout_hours = app.configuration['client_timeout_hours']
else:
  app.security_handler.client_timeout_hours = 24
