# -*- coding: utf-8 -*-

'''
Support for Zabbix
'''

# Import python libs
import json
import urllib2
import logging

# Import salt libs
import salt.utils

logger = logging.getLogger(__name__)

authtoken = None

def _login(url, username, password):
  '''
  Logs in via zabbix api
  '''

  global authtoken

  res = _sendRequest( 'user.login', {
    "user": username,
    "password": password
  }, url, username, password, False)

  if res:
    logger.warning("The zabbix api login suceeded.")
    authtoken = res
    return True
  else:
    logger.warning("The zabbix api login failed.")
    return False

def _checkAuth(url, username, password):
  if not authtoken:
    _login(url, username, password)

def _checkResult(res):
  '''
  Checks wether the result succeded or not
  '''

  if res.has_key('error'):
    logger.info("The zabbix api call succeeded.")
    return None
  else:
    logger.info("The zabbix api call returned an error.")
    return res['result']

def test():
  '''
  Tests a login to zabbix server
  '''
  return _login()

def _sendRequest(method, params, url = None, username = None, password = None, checkauth = True):
  '''
  Sends a request with given method and parameters to zabbix server
  '''

  if checkauth:
    _checkAuth(url, username, password)

  req = {
    "jsonrpc": "2.0",
    "method": method,
    "params": params,
    "id": 1,
    "auth": authtoken
  }

  logger.warning(req)

  request = urllib2.Request(url, json.dumps(req), {'Content-Type': 'application/json'})
  response = urllib2.urlopen(request)
  res = json.loads(response.read())

  logger.warning(res)

  return _checkResult(res)

def version(url, username, password):
  '''
  Returns zabbix API version
  '''
  return _sendRequest( 'apiinfo.version', {
  }, url, username, password)

def listHostgroups(url, username, password):
  '''
  Returns list of hostgroups
  '''
  return _sendRequest('hostgroup.get', {
      "output": "extend"
    }, url, username, password)

def getHostgroup(name, url, username, password):
  '''
  Returns hostgroup with specified name
  '''
  return _sendRequest('hostgroup.get', {
      "filter": {
        "name": name
      },
    }, url, username, password)

def existsHostgroup(name, url, username, password):
  '''
  Checks if given hostgroup exists
  '''
  return _sendRequest('hostgroup.exists', {
      "name": name
    }, url, username, password)

def createHostgroup(name, url, username, password):
  '''
  Creates given hostgroup
  '''
  return _sendRequest('hostgroup.create', {
      "name": name
    }, url, username, password)

def getHost(name, url, username, password):
  '''
  Returns host with specified name
  '''
  return _sendRequest('host.get', {
      "output": "extend",
      "filter": {
        "host": [ name ]
      },
    }, url, username, password)

def existsHost(name, url, username, password):
  '''
  Checks if given host exists
  '''
  return _sendRequest('host.exists', {
      "host": name
    }, url, username, password)

def createHost(name, data, url, username, password):
  '''
  Creates given host
  '''
  groups = []

  for groupname in data['groups']:
    res = getHostgroup(groupname, url, username, password)
    if res:
      groups.append({'groupid': int(res[0]['groupid'])})

  data['groups'] = groups

  templates = []

  for templatename in data['templates']:
    res = getTemplate(templatename, url, username, password)
    if res:
      templates.append({'templateid': int(res[0]['templateid'])})

  data['templates'] = templates

  return _sendRequest('host.create', data, url, username, password)

def getTemplate(name, url, username, password):
  '''
  Returns template with specified name
  '''
  return _sendRequest('template.get', {
      "filter": {
        "host": name
      },
    }, url, username, password)

def getTemplate(name, url, username, password):
  '''
  Returns template with specified name
  '''
  return _sendRequest('template.get', {
      "filter": {
        "name": name
      },
    }, url, username, password)

def existsTemplate(name, url, username, password):
  '''
  Checks if given template exists
  '''
  return _sendRequest('template.exists', {
      "name": name
    }, url, username, password)

def createTemplate(name, data, url, username, password):
  '''
  Creates given template
  '''
  groups = []

  for groupname in data['groups']:
    res = getHostgroup(groupname, url, username, password)
    if res:
      groups.append({'groupid': int(res[0]['groupid'])})

  data['groups'] = groups

  data['host'] = name

  return _sendRequest('template.create', data, url, username, password)

def getItem(name, url, username, password):
  '''
  Returns item with specified name
  '''
  return _sendRequest('item.get', {
      "filter": {
        "key_": name
      },
    }, url, username, password)

def existsItem(name, url, username, password):
  '''
  Checks if given item exists
  '''
  return _sendRequest('item.exists', {
      "key_": name
    }, url, username, password)

def createItem(name, data, url, username, password):
  '''
  Creates given item
  '''
  res = getTemplate(data['template'], url, username, password)
  if res:
    data['hostid'] = int(res[0]['templateid'])
  
  del(data['template'])

  data['name'] = name

  return _sendRequest('item.create', data, url, username, password)

