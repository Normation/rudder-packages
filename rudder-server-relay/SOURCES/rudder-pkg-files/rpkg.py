import os, logging, re, json, textwrap
from pkg_resources import parse_version

import rudderPkgUtils as utils

"""
    Versions can contains the words "-SNAPSHOT" at the end, this should not be a problem at the moment since it is only present in nightly.
    Moreover, we should not have to compare a nightly version to a release one.
"""
class Version:
    def __init__(self, pluginLongVersion):
        match = re.search(r'(?P<rudderVersion>[0-9]+\.[0-9]+)-(?P<pluginShortVersion>[0-9]+\.[0-9]+(-(?P<mode>[a-zA-Z]+)){0,1})', pluginLongVersion)
        if match.group('mode') is None:
            self.mode = 'release'
        elif match.group('mode') == 'SNAPSHOT':
            self.mode = 'nightly'
        else:
            utils.fail("The version %s does not respect the version syntax"%(pluginLongVersion))

        if match.group('rudderVersion') is None or match.group('pluginShortVersion') is None:
            utils.fail("The version %s does not respect the version syntax [0-9]+.[0-9]+-[0-9]+.[0-9]+(-SNAPSHOT){0,1}"%(pluginLongVersion))
        else:
            self.rudderVersion = match.group('rudderVersion')
            self.pluginShortVersion = match.group('pluginShortVersion')
            self.pluginLongVersion = pluginLongVersion


    def __str__(self):
        return self.mode + " => " + self.rudderVersion + "-" + self.pluginShortVersion + " | " + self.pluginLongVersion

    def __repr__(self):
        return self.mode + " => " + self.rudderVersion + "-" + self.pluginShortVersion + " | " + self.pluginLongVersion + "\n"

    def __hash__(self):
        return hash((self.mode, self.rudderVersion, self.pluginShortVersion, self.pluginLongVersion))

    def __eq__(self, other):
        if isinstance(other, Version):
            return self.mode == other.mode and self.rudderVersion == other.rudderVersion and self.pluginShortVersion == other.pluginShortVersion and self.pluginLongVersion == other.pluginLongVersion
        return False

    def __lt__(self, other):
        return parse_version(self.pluginLongVersion) < parse_version(other.pluginLongVersion)
        
    def __le__(self, other):
        return parse_version(self.pluginLongVersion) <= parse_version(other.pluginLongVersion)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __gt__(self, other):
        return parse_version(self.pluginLongVersion) > parse_version(other.pluginLongVersion)

    def __ge__(self, other):
        return parse_version(self.pluginLongVersion) >= parse_version(other.pluginLongVersion)

"""
    Define an object based on a .rpkg file.
"""
class Rpkg:
    def __init__(self, longName, shortName, path, version, metadata): 
        self.longName = longName
        self.shortName = shortName
        self.path = path
        self.version = version
        self.metadata = metadata

    def getMode(self):
        return self.version.mode

    def isCompatible(self):
        return utils.check_plugin_compatibility(self.metadata)

    def show_metadata(self):
        # Mandatory
        print("Name: " + self.metadata['name'])
        print("Short name: " + self.metadata['name'].replace("rudder-plugin-", ""))
        print("Version: " + self.metadata['version'])

        # Description
        description = ""
        if 'description' in self.metadata:
            description = self.metadata['description']
        print("Description:")
        for line in textwrap.wrap(description, 80):
            print("  " + line)

        # Build info
        print("Build-date: " + self.metadata['build-date'])
        print("Build-commit: " + self.metadata['build-commit'])

        # Dependencies info
        if 'depends' in self.metadata:
          for dependType in self.metadata['depends'].keys():
              prefix = "Depends %s: "%(dependType)
              suffix = ', '.join(str(x) for x in self.metadata['depends'][dependType])
              print(prefix + suffix)

        # Jar info
        jar = ""
        if 'jar-file' in self.metadata:
            jar = ', '.join(str(x) for x in self.metadata['jar-files'])
        print("Jar files: " + jar)

        # Content info
        print("Content:")
        for iContent in self.metadata['content'].keys():
            print("  %s: %s"%(iContent, self.metadata['content'][iContent]))

    def __eq__(self, other):
        if isinstance(other, Rpkg):
            return self.longName == other.longName and self.version == other.version
        return False

    def __lt__(self, other):
        return parse_version(self.version.pluginLongVersion) < parse_version(other.version.pluginLongVersion)
        
    def __le__(self, other):
        return parse_version(self.version.pluginLongVersion) <= parse_version(other.version.pluginLongVersion)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __gt__(self, other):
        return parse_version(self.version.pluginLongVersion) > parse_version(other.version.pluginLongVersion)

    def __ge__(self, other):
        return parse_version(self.version.pluginLongVersion) >= parse_version(other.version.pluginLongVersion)

    def __hash__(self):
        return hash((self.longName, self.version))

    def __str__(self):
        return self.path

    def __repr__(self):
        return self.path

    def show(self):
        print(self.path + ":")
        print(json.dumps(self.metadata, indent=4, sort_keys=True))

    def toTabulate(self):
        return [self.longName, self.version.mode, self.version.pluginLongVersion, self.isCompatible()]


