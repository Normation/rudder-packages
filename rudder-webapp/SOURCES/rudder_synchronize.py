#!/usr/bin/python3

"""
Rudder synchronize

A CLI based tool to export and import Rudder component with their dependencies
It requires the rudder-api-client package to be installed to work properly.

Usage:
    rudder-synchronize export <rudder_item> <uuid> <path> [--debug]
    rudder-synchronize import <rudder_item> <path> [--debug]
    rudder-synchronize delete <rudder_item> <uuid> [--debug] [--yes]

"""

# TODO import/export GM
# TODO add resources support in 6.0

import json, logging, traceback
import re
import os, sys
import requests
# Hack to import rudder lib, remove, some day ...
sys.path.insert(0, "/usr/share/rudder-api-client/")
sys.path.insert(0, "/opt/rudder/share/python")
import docopt
from rudder import RudderEndPoint, RudderError

LOG_PATH="./run.log"
YES = None

try:
    input = raw_input
except NameError:
    pass

class colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'

with open('/var/rudder/run/api-token') as ftoken:
    TOKEN = ftoken.read()
RUDDER_URL="https://localhost/rudder"
endpoint = RudderEndPoint(RUDDER_URL, TOKEN, verify=False)

def startLogger(logLevel):
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    # stdout logger
    stdoutHandler = logging.StreamHandler(sys.stdout)
    stdoutFormatter = logging.Formatter('%(message)s')
    stdoutHandler.setFormatter(stdoutFormatter)
    if logLevel == 'INFO':
        stdoutHandler.setLevel(logging.INFO)
    elif logLevel == 'DEBUG':
        stdoutHandler.setLevel(logging.DEBUG)
    else:
        fail("unknow loglevel %s"%(logLevel))

    # log file logger
    fileHandler = logging.FileHandler(filename=LOG_PATH , mode='w')
    fileHandler.setLevel(logging.DEBUG)
    fileFormatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fileHandler.setFormatter(fileFormatter)

    root.addHandler(stdoutHandler)
    root.addHandler(fileHandler)

def fail(message, code=1, exit=False):
    logging.error(colors.RED + message + colors.ENDC)
    if exit == True:
        exit(code)

def make_jsonfile(filename, content):
  logging.debug("Writing to %s"%filename)
  if not os.path.exists(os.path.dirname(filename)):
    os.makedirs(os.path.dirname(filename))
  with open(filename, "w") as fd:
    fd.write(json.dumps(content, sort_keys=True, indent=2, separators=(',', ': ')))

def queryYesNo(question, answer=None):
    global YES
    if YES:
        return (YES, YES)
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if answer == None:
        while True:
            sys.stdout.write(question)
            choice = input()

            if choice == "Y":
                YES = True
                return (True, True)
            elif choice == "N":
                YES = False
                return (False, False)
            elif choice in valid:
                return (answer, valid[choice])
            else:
                sys.stdout.write("Please respond with 'y' or 'no' "
                                 "(or 'Y' or 'N' for all next inputs).\n")
    else:
        return (answer, answer)


def is_directive(data):
    if "techniqueName" in data and "techniqueVersion" in data:
        return True
    return False

def is_rule(data):
    if "directives" in data and "targets" in data:
        return True
    return False

def is_technique(data):
    if "type" in data and "version" in data and "data" in data:
        return True
    return False

def export_rule(uuid, path):
    logging.debug("Exporting rule %s"%uuid)
    try:
        rule = endpoint.rule_details(uuid)['rules'][0]
        make_jsonfile(path + "/rules/" + uuid + ".json", rule)

        directives = []
        for iDirective in rule['directives']:
            export_directive(iDirective, path)
    except RudderError as e:
        fail("Error while exporting technique %s:\n%s"%(uuid,e.message))

def export_directive(uuid, path):
    logging.debug("Exporting directive %s"%uuid)
    try:
        directive = endpoint.directive_details(uuid)['directives'][0]
        # This is needed because of #8687, the API does not know these parameters at creation
        if "isEnabled" in directive:
            del directive["isEnabled"]
        if "isSystem" in directive:
            del directive["isSystem"]
        if "priority" in directive:
            del directive["priority"]
        if "tags" in directive:
            del directive["tags"]
        if "policyMode" in directive:
            del directive["policyMode"]
        if "system" in directive:
            del directive["system"]
        make_jsonfile( path + "/directives/" + uuid + ".json", directive)

        export_technique(directive["techniqueName"], path)

    except RudderError as e:
        fail("Error while exporting technique %s:\n%s"%(uuid, e.message))

def export_technique(uuid, path):
    try:
        techniques = get_all_techniques()
        if uuid in techniques.keys():
            data = { "data" : techniques[uuid], "type": "ncf_technique", "version": "1" }
            make_jsonfile(path + "/techniques/" + uuid + ".json", data)
        else:
             fail("Could not find technique %s"%uuid)
    except RudderError as e:
        fail("Error while exporting technique %s:\n%s\n%s"%(uuid, e.response, e.message))
        logging.error("Could not download technique %s"%uuid)

def import_technique(path):
    try:
        with open(path) as f:
            data = json.load(f)["data"]

        techniqueData = data
        techniqueName = techniqueData["name"]
        techniqueId = techniqueData["id"]
        method = 'PUT'
        endpoint = '/api/latest/techniques'

        # Look for existing technique
        if techniqueId in get_all_techniques().keys():
            (answer, replace) = queryYesNo("The technique %s \"%s\" %s already exists, do you really want to replace it? [y/n/Y/N]"%(
                colors.YELLOW,
                techniqueName,
                colors.ENDC
            ), None)
            if replace:
                method = 'POST'
                endpoint = '/api/latest/techniques/' + techniqueId + '/1.0'
            else:
                logging.info(colors.GREEN + "Skipping technique %s as is already exists"%techniqueName + colors.ENDC)
                return

        # Call the ncf API
        ncfEndpoint = RudderEndPoint("https://localhost/rudder", TOKEN, verify=False)
        technique = ncfEndpoint.request(method, endpoint, None, techniqueData, return_raw=False)
        logging.info(colors.GREEN + "Successfully imported technique %s"%techniqueName + colors.ENDC)

    except RudderError as e:
        fail("Error while importing technique %s:\n%s\n%s"%(techniqueName, e.response, e.message))

def import_directive(path):
    try:
        with open(path) as f:
            data = json.load(f)
        directive = endpoint.create_directive(
                                     techniqueName   = data["techniqueName"],
                                     displayName      = data["displayName"],
                                     parameters       = data["parameters"],
                                     shortDescription = data["shortDescription"],
                                     longDescription  = data["longDescription"],
                                     id               = data["id"],
                                     techniqueVersion = data["techniqueVersion"],
                                     priority         = data.get("priority"),
                                     tags             = data.get("tags"),
                                     policyMode       = data.get("policyMode")
                                    )
        logging.info(colors.GREEN + "Successfully imported directive %s"%data["id"] + colors.ENDC)
    except RudderError as e:
        fail("Error while importing directive %s:\n%s"%(path,e.message))


def import_rule(path):
    try:
        with open(path) as f:
            data = json.load(f)
        if is_rule(data):
            rule = endpoint.create_rule(
                    displayName = data["displayName"],
                    id = data["id"],
                    shortDescription = data["shortDescription"],
                    longDescription = data["longDescription"],
                    directives = data["directives"],
                    tags = data["tags"]
                   )
            logging.info(colors.GREEN + "Successfully imported rule %s"%data["id"] + colors.ENDC)
    except RudderError as e:
        fail("Error while importing rule %s:\n%s"%(path, e.message))

def import_directives(path):
    if os.path.isdir(path):
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith('.json'):
                     import_directive(os.path.join(root, file))
    else:
        import_directive(path)

def import_rules(path):
    if os.path.isdir(path):
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith('.json'):
                     import_rule(os.path.join(root, file))
    else:
        import_rule(path)

def import_techniques(path):
    if os.path.isdir(path):
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith('.json'):
                     import_technique(os.path.join(root, file))
    else:
        import_technique(path)
    global YES
    YES = None

NCF_METHODS = {}
def get_all_generic_methods():
    global NCF_METHODS
    if not NCF_METHODS:
        ncfEndpoint = RudderEndPoint("https://localhost/rudder", TOKEN, verify=False)
        NCF_METHODS = ncfEndpoint.request("GET", "/api/internal/methods", None, None, return_raw=False)
    return NCF_METHODS["methods"]

NCF_TECHNIQUES = {}
def get_all_techniques():
    global NCF_TECHNIQUES
    if not NCF_TECHNIQUES:
        ncfEndpoint = RudderEndPoint("https://localhost/rudder", TOKEN, verify=False)
        techniques = ncfEndpoint.request("GET", "/api/latest/techniques", None, None, return_raw=False)
        NCF_TECHNIQUES = { v["id"]:v for v in techniques["techniques"] }
    return NCF_TECHNIQUES

def remove_rule(rule):
    try:
        delete = endpoint.delete_rule(rule)
        logging.info(colors.GREEN + "Successfully removed rule %s"%(colors.YELLOW + "\"" + rule + "\"" + colors.ENDC))
    except RudderError as e:
        logging.info(colors.RED + e.message + colors.ENDC)

def remove_directive(directive):
    try:
        delete = endpoint.delete_directive(directive)
        logging.info(colors.GREEN + "Successfully removed directive %s"%(colors.YELLOW + "\"" + directive + "\"" + colors.ENDC))
    except RudderError as e:
        logging.info(colors.RED + e.message + colors.ENDC)

"""
    Ask for the removal of each directive based on the target technique.
    If a removal is refused, it will keep the technique and the selected directives.
"""
def remove_technique(techniqueName, techniqueVersion="1.0", force=False):
    removeTechnique = True
    answer = None
    try:
        if techniqueName in get_all_techniques().keys():
            directives = endpoint.list_directives_version(techniqueName, techniqueVersion)['directives']
            for d in directives:
                (answer, remove) = queryYesNo("The directive %s \"%s\" %s with id %s \"%s\" %s is defined and base from the technique %s, do you really want to delete it? [y/n/Y/N]"%(colors.YELLOW, d['id'], colors.ENDC, colors.YELLOW, d['displayName'], colors.ENDC, techniqueName), answer)
                if remove:
                    remove_directive(d['id'])
                else:
                    removeTechnique = False
            if removeTechnique:
                headers = { "X-API-Token": TOKEN }
                r = requests.delete(RUDDER_URL + "/api/latest/techniques/" + techniqueName + "/" + techniqueVersion, params={'force':'false'}, verify=False, headers=headers)
                logging.info(colors.GREEN + "Successfully removed technique %s"%(colors.YELLOW + "\"" + techniqueName + "\"" + colors.ENDC))
            else:
                logging.info(colors.GREEN + "Keeping technique %s since some directives are still using it"%(colors.YELLOW + "\"" + techniqueName + "\"" + colors.ENDC))
        else:
            logging.info(colors.GREEN + "The technique %s could not be found on the server"%(colors.YELLOW + "\"" + techniqueName + "\"" + colors.GREEN) + colors.ENDC)
    except Exception as e:
        fail("Error while removing technique %s:\n%s"%(colors.YELLOW + "\"" + techniqueName + "\"" + colors.ENDC, e.message))

##########################
# Command line interface #
##########################

if __name__ == "__main__":
  args = docopt.docopt(__doc__)
  if args['--debug']:
      startLogger('DEBUG')
  else:
      startLogger('INFO')

  if args['--yes']:
      YES = True

  if args['export']:
      if args['<rudder_item>'] == "technique":
          export_technique(args['<uuid>'], args['<path>']),
      elif args['<rudder_item>'] == "directive":
          export_directive(args['<uuid>'], args['<path>']),
      elif args['<rudder_item>'] == "rule":
          export_rule(args['<uuid>'], args['<path>']),
      else:
          fail("Unknown Rudder Item %s"%args['<rudder_item>'])
  elif args['import']:
      if args['<rudder_item>'] == "technique":
          import_techniques(args['<path>']),
      elif args['<rudder_item>'] == "directive":
          import_directives(args['<path>']),
      elif args['<rudder_item>'] == "rule":
          import_rules(args['<path>']),
      else:
          fail("Unknown Rudder Item %s"%args['<rudder_item>'])

  elif args['delete'] and args['delete']:
      if args['<rudder_item>'] == "technique":
          remove_technique(args['<uuid>']),
      elif args['<rudder_item>'] == "directive":
          remove_directive(args['<uuid>']),
      elif args['<rudder_item>'] == "rule":
          remove_rule(args['<uuid>']),
      else:
          fail("Unknown Rudder Item %s"%args['<rudder_item>'])
