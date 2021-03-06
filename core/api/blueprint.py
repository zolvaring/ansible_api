#!/usr/bin/env python3


# Initialize configuration for the application
from .configuration import configuration

# Initialize the app itself, add 'is_running' endpoint
from .starter import app

# Add 'info' endpoint to app
from .info import app

# Add AnsibleTrigger endpoint as 'ansible'
from .AnsibleTrigger import app

# Add user endpoint
from .UserTest import app
