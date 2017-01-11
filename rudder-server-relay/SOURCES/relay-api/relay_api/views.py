from relay_api import app
from relay_api.shared_files import shared_files_put, shared_files_head, shared_files_put_forward, shared_files_head_forward
from relay_api.remote_run import remote_run_generic
from relay_api.common import *

from flask import Flask, jsonify, request, abort, make_response
from StringIO import StringIO
import traceback

from pprint import pprint

NODESLIST_FILE = "/opt/rudder/etc/nodeslist.json"
UUID_FILE = '/opt/rudder/etc/uuid.hive'
API_DEBUGINFO = True
POLICY_SERVER_FILE = "/var/rudder/cfengine-community/policy_server.dat"
SHARED_FILES_PATH = "/var/rudder/shared-files"

#################
# API functions #
#################

@app.route('/shared-files/<string:target_uuid>/<string:source_uuid>/<string:file_id>', methods=['PUT'])
def put_file(target_uuid, source_uuid, file_id):
  try:
    nodes = get_nodes_list(NODESLIST_FILE)
    if target_uuid not in nodes:
      # forward the file if the node is unknown
      policy_server = get_file_content(POLICY_SERVER_FILE)
      if policy_server == "root":
        return format_response("Unknown UUID: "+target_uuid, 404)
      else:
        url = "https://"+policy_server+"/rudder/relay-api/shared-files/" + target_uuid + "/" + source_uuid + "/" + file_id + "?hash=" + file_hash
        res = shared_files_put_forward(request.stream, url)
    else:
      # process the file if it is known
      my_uuid = get_file_content(UUID_FILE)
      filename = shared_files_put(target_uuid, source_uuid, file_id, request.stream, nodes, my_uuid, SHARED_FILES_PATH)
      if API_DEBUGINFO:
        res = "OK\nWritten to: " + filename + "\n"
      else:
        res = "OK\n"
    return format_response(res)
  except Exception as e:
    return format_error(e, API_DEBUGINFO)


@app.route('/shared-files/<string:target_uuid>/<string:source_uuid>/<string:file_id>', methods=['HEAD'])
def head_file(target_uuid, source_uuid, file_id):
  try:
    nodes = get_nodes_list(NODESLIST_FILE)
    file_hash = request.args.get('hash', '')
    if target_uuid not in nodes:
      # forward the request if the node is unknown
      policy_server = get_file_content(POLICY_SERVER_FILE)
      if policy_server == "root":
        return format_response("Unknown UUID: "+target_uuid, 404)
      else:
        url = "https://"+policy_server+"/rudder/relay-api/shared-files/" + target_uuid + "/" + source_uuid + "/" + file_id + "?hash=" + file_hash
        res = shared_files_head_forward(url)
    else:
      # process the request if it is known
      my_uuid = get_file_content(UUID_FILE)
      res = shared_files_head(target_uuid, source_uuid, file_id, file_hash, nodes, my_uuid, SHARED_FILES_PATH)
    if res:
      return format_response("", 200)
    else:
      return format_response("", 404)
  except Exception as e:
    print(traceback.format_exc())
    return format_error(e, API_DEBUGINFO)

@app.route('/remote-run/all', methods=['POST'])
def remote_run_all():
  try:
    nodes = get_nodes_list(NODESLIST_FILE)
    my_uuid = get_file_content(UUID_FILE)
    return remote_run_generic(nodes, my_uuid, None, True, request.form)
  except Exception as e:
    print(traceback.format_exc())
    return format_error(e, API_DEBUGINFO)

@app.route('/remote-run/nodes', methods=['POST'])
def remote_run_nodes():
  try:
    nodes = get_nodes_list(NODESLIST_FILE)
    my_uuid = get_file_content(UUID_FILE)
    return remote_run_generic(nodes, my_uuid, request.form['nodes'].split(','), False, request.form)
  except Exception as e:
    print(traceback.format_exc())
    return format_error(e, API_DEBUGINFO)

@app.route('/remote-run/nodes/<string:node_id>', methods=['POST'])
def remote_run_node(node_id):
  try:
    nodes = get_nodes_list(NODESLIST_FILE)
    my_uuid = get_file_content(UUID_FILE)
    return remote_run_generic(nodes, my_uuid, [node_id], False, request.form)
  except Exception as e:
    print(traceback.format_exc())
    return format_error(e, API_DEBUGINFO)

# main
if __name__ == '__main__':
  app.run(debug = True)

