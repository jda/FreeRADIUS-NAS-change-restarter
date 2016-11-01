#!/usr/bin/python
# Safely reload FreeRADIUS after NAS table changes
# 10-2011 Jon Auer
#


try:
  import json
except ImportError:
  import simplejson as json

import pyrad.packet
import MySQLdb
import sys
import subprocess
import time
import random

markerpath = "/var/lib/reloader/marker"

def get_db_version(config):
  conn = MySQLdb.connect(
    config['host'],
    config['username'],
    config['password'],
    config['database'])

  curs = conn.cursor()
  curs.execute("SELECT `id` from `nas_changes` order by `id` desc limit 1")
  data = curs.fetchone()[0]
  
  curs.close()
  conn.close()
  
  return int(data)

def get_local_version(markerpath):
  try:
    marker = open(markerpath)
  except IOError:
    marker = open(markerpath, 'w')
    marker.write('0')
    marker.close()
    marker = open(markerpath)

  local_ver = marker.read()
  marker.close()
  return int(local_ver)

def set_local_version(markerpath, ver):
  marker = open(markerpath, 'w')
  marker.write(str(ver))
  marker.close()

def peers_alive(config):
  from pyrad.client import Client
  from pyrad.dictionary import Dictionary
  
  radconfig = config['radius']
  localconfig = config['local']

  auth_OK = True

  dictionary = Dictionary(localconfig['raddict'])
  
  for server in radconfig['servers']:
    srv = Client(server=server, secret=str(radconfig['secret']), dict=dictionary)
    req = srv.CreateAuthPacket(code=pyrad.packet.AccessRequest,
      User_Name=radconfig['username'],
      NAS_Identifier="localhost")
    req["User-Password"] = req.PwCrypt(radconfig['password'])

    try:
      reply = srv.SendPacket(req)
    except pyrad.client.Timeout:
      print "Could not contact:", server
      auth_OK = False

    if reply.code != 2:
      print "Auth failed to", server
      auth_OK = False
  return auth_OK 

def restart_radius(radpath):
  status = subprocess.call([radpath, "restart"])
  return status

# Get/make sure we have a config

if len(sys.argv) == 2:
  # read json from file param
  configFile = open(sys.argv[1], 'r')
else:
  # try to read from /etc
  try:
    configFile = open('/etc/reloader.json', 'r')
  except IOError:
    print "No config provided as param and could not open /etc/reloader.json"
    sys.exit(1)

config = json.loads(configFile.read())
configFile.close()

db_ver = get_db_version(config['database'])
local_ver = get_local_version(markerpath)

if db_ver > local_ver:
  print "Reload needed"
  
  if peers_alive(config):
    print "Peers alive. Time for random sleep to reduce change of collision with other restart"
    time.sleep(random.randrange(5,30,1))
    if peers_alive(config):
      print "Peers alive both times, restarting"
      status = restart_radius(config['local']['radpath'])

      if status==0:
        set_local_version(markerpath, db_ver)     
      else:
        print "Peers dead. Try later"

else:
  print "No changes detected in mysql database - no reload needed"
  
