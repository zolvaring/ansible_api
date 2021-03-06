#!/usr/bin/env python3


# TODO: import read_yaml from elsewhere



from flask import jsonify, request
from flask_restful import Resource
from .blueprint import app
import os
import yaml
import re


class AnsibleTrigger(Resource):

  @app.security_handler.authorization_required
  def post(self):

    #if 'json' not in request:
    #  request.json = {}

    if 'ip_address' in request.json:
      ip_address = request.json['ip_address']
    elif 'ip_address' in request.args:
      ip_address = request.args.get('ip_address')
    else:
      return jsonify({'status':'missing required parameter: ip_address'})

    if 'hostnames' in request.json:
      hostnames = request.json['hostnames']
    elif 'hostnames' in request.args:
      hostnames = request.args.get('hostnames')
    else:
      return jsonify({'status':'missing required parameter: hostnames'})

    if 'extra_vars' in request.json:
      extra_vars = request.json['extra_vars']
    elif 'extra_vars' in request.args:
      extra_vars = request.args.get('extra_vars')
    else:
      extra_vars = ''

    if 'ansible_playbook_path' in request.json:
      ansible_playbook_path = request.json['ansible_playbook_path']
    elif 'ansible_playbook_path' in request.args:
      ansible_playbook_path = request.args.get('ansible_playbook_path')
    else:
      ansible_playbook_path = '/etc/ansible/playbooks/apple_standup.yaml'

    if 'ansible_inventory_path' in request.json:
      ansible_inventory_path = request.json['ansible_inventory_path']
    elif 'ansible_inventory_path' in request.args:
      ansible_inventory_path = request.args.get('ansible_inventory_path')
    else:
      ansible_inventory_path = '/etc/ansible/inventory/apple/dynamic'

    if not isinstance(hostnames, list):
      hostnames = [ hostnames ]
    for hostname in hostnames:
      #print(f'Adding <{hostname}> to inventory')
      print('Adding <{}> to inventory'.format(hostname))
      AnsibleTrigger.add_host_to_groups(ip_address, hostname, ansible_inventory_path)
    
    formatted_hostnames = ''
    for hostname in hostnames:
      #formatted_hostnames = formatted_hostnames + f'{hostname},'
      formatted_hostnames = formatted_hostnames + '{},'.format(hostname)
    #os.system(f"ansible-playbook {ansible_playbook_path} -i {ansible_inventory_path} -l {formatted_hostnames}")
    os.system("ansible-playbook {} -i {} -l {} -v".format(ansible_playbook_path, ansible_inventory_path, formatted_hostnames))

    return jsonify({'status':'success'})

  @staticmethod
  def add_host_to_groups(ip_address, hostname, ansible_inventory_path):

    # Adds ip address to /etc/hosts
    with open('/etc/hosts', 'r') as f:
      lines = f.readlines()
    with open('/etc/hosts', 'w') as f:
      for line in lines:
        if not line.startswith(ip_address):
          f.write(line)
      f.write('{}  {}'.format(ip_address, hostname))

    group_definitions = AnsibleTrigger.read_yaml('/etc/ansible/ansible_api/local/group_definitions.yaml')
    for group_definition in group_definitions:
      host_already_in_group = False
      if re.compile(group_definition['regex']).match(hostname):
        #hostfile = f"{app.configuration['ansible_inventory_path']}/{group_definition['name']}.ini"
        hostfile = "{}/{}.ini".format(app.configuration['ansible_inventory_path'], group_definition['name'])
        if not os.path.exists(hostfile):
          with open(hostfile, 'a+') as f:
            #f.write(f"[{group_definition['name']}]\n")
            f.write("[{}]\n".format(group_definition['name']))
        else:
          with open(hostfile, 'r') as f:
            lines = f.readlines()
          for line in lines:
            if line.rstrip() == hostname:
              host_already_in_group = True

        if not host_already_in_group:
          with open(hostfile, 'a+') as f:
            #f.write(f'{hostname}\n')
            f.write('{}\n'.format(hostname))

  # TODO: this should be moved and imported from elsewhere
  @staticmethod
  def read_yaml(filepath):
    if not os.path.exists(filepath):
      return {}
    else:
      with open(filepath, 'r') as f:
        yaml_contents = yaml.safe_load(f)
      return yaml_contents
    
    
app.api.add_resource(AnsibleTrigger, '/ansible')
