"""
    Contains functions called by the parser and nothing else.
"""
import sys
import os
import re
import bs4
import shutil
import requests as requests
import logging
from tabulate import tabulate
import plugin
import rudderPkgUtils as utils


"""
    Expect a list of path as parameter.
    Try to install the given rpkgs.
"""
def install_file(package_files):
    for package_file in package_files:
        logging.info("Installing " + package_file)
        # First, check if file exists
        if not os.path.isfile(package_file):
            utils.fail("Error: Package file " + package_file + " does not exist")
        metadata = utils.rpkg_metadata(package_file)
        exist = utils.package_check(metadata)
        # As dependencies are only displayed messages for now,
        # wait until the end to make them visible.
        # This should be moved before actual installation once implemented.
        if not utils.install_dependencies(metadata):
            exit(1)
        if exist:
            logging.info("The package is already installed, I will upgrade it.")
        script_dir = utils.extract_scripts(metadata, package_file)
        utils.run_script("preinst", script_dir, exist)
        utils.install(metadata, package_file, exist)
        utils.run_script("postinst", script_dir, exist)
        if metadata['type'] == 'plugin' and 'jar-files' in metadata:
            for j in metadata['jar-files']:
                utils.jar_status(j, True)

"""
    List installed plugins.
"""
def package_list():
    toPrint = []
    for p in utils.DB["plugins"].keys():
        toPrint.append([p, utils.DB["plugins"][p]["version"]])
    print(tabulate(toPrint, headers=['Plugin Name', 'Version'], tablefmt='orgtbl'))

"""
    Given a short name, lookf for a the given packages availables for this plugin.
"""
def package_search(name):
    utils.readConf()
    pkgs = plugin.Plugin(name[0])
    pkgs.getAvailablePackages()
    toPrint = []
    for iRpkg in sorted(pkgs.packagesInfo):
        toPrint.append(iRpkg.toTabulate())
    print(tabulate(toPrint, headers=['Name', 'release mode', 'Version', 'Compatible'], tablefmt='orgtbl'))

"""
    Install the package for a given plugin in a specific version.
    It will not check for compatibility and will let it to the installer since
    the user explicitly asked for this version.
"""
def package_install_specific_version(name, longVersion, mode="release"):
    utils.readConf()
    pkgs = plugin.Plugin(name[0])
    pkgs.getAvailablePackages()
    if mode == "release":
        rpkg = pkgs.getRpkgByLongVersion(longVersion, mode)
    else:
        rpkg = pkgs.getRpkgByLongVersion(longVersion, mode)
    rpkgPath = utils.downloadByRpkg(rpkg)
    install_file([rpkgPath])

"""
    Install the latest available and compatible package for a given plugin.
    If no release mode is given, it will only look in the released rpkg.
"""
def package_install_latest(name, mode="release"):
    utils.readConf()
    pkgs = plugin.Plugin(name[0])
    pkgs.getAvailablePackages()
    if mode == "release":
        rpkg = pkgs.getLatestCompatibleRelease()
    else:
        rpkg = pkgs.getLatestCompatibleNightly()
    rpkgPath = utils.downloadByRpkg(rpkg)
    install_file([rpkgPath])

"""Remove a given plugin. Expect a list of name as parameter."""
def remove(package_names):
    for package_name in package_names:
        logging.info("Removing " + package_name)
        if package_name not in utils.DB["plugins"]:
            utils.fail("This package is not installed. Aborting!", 2)
        script_dir = utils.DB_DIRECTORY + "/" + package_name
        metadata = utils.DB["plugins"][package_name]
        if metadata['type'] == 'plugin' and 'jar-files' in metadata:
            for j in metadata['jar-files']:
                utils.jar_status(j, False)
        utils.run_script("prerm", script_dir, None)
        utils.remove_files(metadata)
        utils.run_script("postrm", script_dir, None)
        shutil.rmtree(script_dir)
        del utils.DB["plugins"][package_name]
        utils.db_save()

def rudder_postupgrade():
    for plugin in utils.DB["plugins"]:
        script_dir = utils.DB_DIRECTORY + "/" + plugin
        utils.run_script("postinst", script_dir, True)

def check_compatibility():
    for p in utils.DB["plugins"]:
        metadata = utils.DB["plugins"][p]
        if not utils.check_plugin_compatibility(metadata):
            logging.warning("Plugin " + p + " is not compatible with rudder anymore, disabling it.")
            if 'jar-files' in metadata:
                for j in metadata['jar-files']:
                    utils.jar_status(j, False)
            logging.warning("Please install a new version of " + p + " to enable it again.")
            logging.info("")
            utils.jetty_needs_restart = True

def plugin_save_status():
    enabled = []
    if not os.path.exists(utils.PLUGINS_CONTEXT_XML):
        return
    text = open(utils.PLUGINS_CONTEXT_XML).read()
    match = re.search(r'<Set name="extraClasspath">(.*?)</Set>', text)
    if match:
        enabled = match.group(1).split(',')
    for p in utils.DB["plugins"]:
        metadata = utils.DB["plugins"][p]
        if 'jar-files' in metadata:
            for j in metadata['jar-files']:
                if j in enabled:
                    print("enabled " + j)
                else:
                    print("disabled " + j)

def plugin_restore_status():
    lines = sys.stdin.readlines()
    for line in lines:
        line = line.strip()
        if line.startswith("enabled "):
            print("enable " + line.split(' ')[1])
            utils.jar_status(line.split(' ')[1], True)
        if line.startswith("disabled "):
            utils.jar_status(line.split(' ')[1], False)
    check_compatibility()

def plugin_status(plugins, status):
    for plugin in plugins:
        if status:
            print("Enabling " + plugin)
        else:
            print("Disabling " + plugin)
        if plugin not in utils.DB["plugins"]:
            utils.fail("Unknown plugin " + plugin)
        metadata = utils.DB["plugins"][plugin]
        if 'jar-files' in metadata:
            for j in metadata['jar-files']:
                utils.jar_status(j, status)

def plugin_disable_all():
    plugin_status(utils.DB["plugins"].keys(), False)

def plugin_enable_all():
    plugin_status(utils.DB["plugins"].keys(), True)

def update_licenses():
    utils.readConf()
    url = utils.URL + "/licenses/" + utils.REPO
    r = requests.get(url, auth=(utils.USERNAME, utils.PASSWORD))
    data = bs4.BeautifulSoup(r.text, "html.parser")
    licensePattern = re.compile('<a href="(?P<file>[a-zA-Z\-_]+.license)">(?P=file)<\/a>')
    keyPattern = re.compile('<a href="(?P<key>[a-zA-Z\-_]+.key)">(?P=key)<\/a>')
    for l in data.find_all("a"):
        licenseMatch = licensePattern.search(str(l))
        keyMatch = keyPattern.search(str(l))
        if licenseMatch is not None:
            logging.info("downloading %s"%(licenseMatch.group('file')))
            utils.download(url + "/" + licenseMatch.group('file'), "/opt/rudder/etc/plugins/licenses/" + licenseMatch.group('file'))
        elif keyMatch is not None:
            logging.info("downloading %s"%(keyMatch.group('key')))
            utils.download(url + "/" + keyMatch.group('key'), "/opt/rudder/etc/plugins/licenses/" + keyMatch.group('key'))

# TODO validate index sign if any?
""" Download the index file on the repos """
def update():
    utils.readConf()
    logging.debug('Updating the index')
    utils.getRudderKey()
    # backup the current indexFile if it exists
    logging.debug("backuping %s in %s"%(utils.INDEX_PATH, utils.INDEX_PATH + ".bkp"))
    if os.path.isfile(utils.INDEX_PATH):
        os.rename(utils.INDEX_PATH, utils.INDEX_PATH + ".bkp")
    try:
        utils.download(utils.URL + "/" + "rpkg.index")
    except Exception as e:
        if os.path.isfile(utils.INDEX_PATH + ".bkp"):
            logging.debug("restoring %s from %s"%(utils.INDEX_PATH, utils.INDEX_PATH + ".bkp"))
            os.rename(utils.INDEX_PATH + ".bkp", utils.INDEX_PATH)
        utils.fail(e)
