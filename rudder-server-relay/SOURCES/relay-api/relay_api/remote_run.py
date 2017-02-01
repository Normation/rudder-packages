from relay_api.common import *

import base64
import re
import os
import datetime
import requests
from subprocess import Popen, PIPE, STDOUT
from flask import Flask, Response

# disable ssl warning on rudder connection in all the possible ways
try:
  import urllib3
  urllib3.disable_warnings()
except:
  pass

try:
  requests.packages.urllib3.disable_warnings()
except:
  pass

from pprint import pprint

NEXTHOP = None
REMOTE_RUN_COMMAND = "sudo /opt/rudder/bin/rudder remote run"

def get_next_hop(nodes, my_uuid):
  """ Build a dict of node_id => nexthop_id """
  global NEXTHOP
  ## uncomment to enable nexthop caching caching (depends on nodeslist caching)
  #if NEXTHOP is not None:
  #  return NEXTHOP
  #else:
  NEXTHOP = {}
  for node in nodes:
    NEXTHOP[node] = node_route(nodes, my_uuid, node)[0]
  return NEXTHOP

def get_all_my_nodes(nexthop):
  """ Get all my directly connected nodes """
  result = []
  for node in nexthop:
    if nexthop[node] == node:
      result.append(node)
  return result

def get_my_nodes(nexthop, nodes):
  """ Get all nodes directly connected in the given list """
  result = []
  for node in nodes:
    if node not in nexthop:
      raise ValueError("ERROR unknown node: " + str(node))
    if nexthop[node] == node:
      result.append(node)
    return result

def get_relay_nodes(nexthop, relay, nodes):
  """ Get all nodes behind the given relay from the given list """
  result = []
  for node in nodes:
    if node not in nexthop:
      raise ValueError("ERROR unknown node: " + str(node))
    if nexthop[node] == relay and nexthop[node] != node:
      result.append(node)
  return result

def get_next_relays(nexthop):
  """ Get a list of all relays directly connected to me """
  result = set([])
  for node in nexthop:
    next_hop = nexthop[node]
    if next_hop != node:
      result.add(next_hop)
  return result

def resolve_hostname(local_nodes, node):
  """ Get the hostname of a node from its uuid """
  if node not in local_nodes:
    raise ValueError("ERROR unknown node: " + str(node))
  if "hostname" not in local_nodes[node]:
    raise ValueError("ERROR invalid nodes file on the server for " + node)
  return local_nodes[node]["hostname"]

def call_remote_run(host, uuid, classes, keep_output, asynchronous):
  """ Call the remote run command locally """
  if classes:
    classes_parameter = " -D " + classes
  else:
    classes_parameter = ""

  return run_command(REMOTE_RUN_COMMAND + classes_parameter + " " + host, uuid, keep_output, asynchronous)

def run_command(command, prefix, keep_output, asynchronous):
  """ Run the given command, prefixing all output lines with prefix """

  if keep_output:
    process = Popen(command, shell=True, stdout=PIPE, stderr=STDOUT)
    output = "".join([prefix + ":" + line for line in process.stdout.readlines()])
    retval = process.wait()
  else:
    output = ""
    if asynchronous:
      command = command + " &"
      process = Popen(command)
    else:
      process = Popen(command, shell=True)
      retval = process.wait()

  return output

def make_api_call(host, nodes, all_nodes, classes, keep_output, asynchronous):
  if all_nodes:
    method = "all"
  else:
    method = "nodes"

  url = "https://" + host + "/rudder/relay-api/remote-run/" + method

  data = {}

  if classes:
    data["classes"] = classes

  data["keep_output"] = keep_output
  data["asynchronous"] = asynchronous

  if nodes:
    data["nodes"] = ",".join(nodes)

  req = requests.post(url, data=data, verify=False)
  if req.status_code == 200:
    return req.text
  else:
    raise ValueError("Upstream Error: " + req.text)

def remote_run_generic(local_nodes, my_uuid, nodes, all_nodes, form):
  # Set default option values
  classes = None
  keep_output = False
  asynchronous = False

  if "classes" in form:
    classes = form['classes']

  if "keep_output" in form:
    keep_output = form['keep_output'].lower() == "true"

  if "asynchronous" in form:
    asynchronous = form['asynchronous'].lower() == "true"

  NEXTHOP = get_next_hop(local_nodes, my_uuid)

  def generate_output():
    # Pass the call to sub relays
    for relay in get_next_relays(NEXTHOP):
      host = resolve_hostname(local_nodes, relay)
      if all_nodes:
        yield make_api_call(host, None, all_nodes, classes, keep_output, asynchronous)
      else:
        relay_nodes = get_relay_nodes(NEXTHOP, relay, nodes)
        if relay_nodes:
          yield make_api_call(host, get_relay_nodes(NEXTHOP, relay, nodes), all_nodes, classes, keep_output, asynchronous)
    # Call directly managed nodes when needed
    if all_nodes:
      local_nodes_to_call = get_all_my_nodes(NEXTHOP)
    else:
      local_nodes_to_call = get_my_nodes(NEXTHOP, nodes)
    for node in local_nodes_to_call:
      host = resolve_hostname(local_nodes, node)
      yield call_remote_run(host, node, classes, keep_output, asynchronous)

  return Response(generate_output())
