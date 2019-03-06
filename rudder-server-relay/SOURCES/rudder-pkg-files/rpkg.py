import os, logging, re, json
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

    def verifyAuth(self):
        # Get rudder plugins gpg key
        utils.getRudderKey()
        # Download hash and sign files
        (folder, leaf) = os.path.split(self.path)

        shaSumUrl = folder + "/" + "SHA512SUMS"
        shaSumDst   = utils.FOLDER_PATH + "/" + shaSumUrl
        logging.info("downloading shasum file  %s"%(utils.URL + "/" + shaSumUrl))
        utils.download(utils.URL + "/" + shaSumUrl)

        signUrl   = folder + "/" + "SHA512SUMS.asc"
        signDst   = utils.FOLDER_PATH + "/" + signUrl
        logging.info("downloading shasum sign file  %s"%(utils.URL + "/" + signUrl))
        utils.download(utils.URL + "/" + signUrl)

        # Verify that signature is correct
        gpgCommand = "/usr/bin/gpg --homedir " + utils.GPG_HOME + " --verify " + signDst + " " + shaSumDst
        logging.debug("Executing %s"%(gpgCommand))
        logging.info("verifying shasum file signature %s"%(gpgCommand))
        utils.shell(gpgCommand, keep_output=False, fail_exit=True, keep_error=False)
        logging.info("=> OK!\n")
        return True

    def verifyHash(self):
        fileHash = []
        (folder, leaf) = os.path.split(self.path)
        shaSumPath = utils.FOLDER_PATH + "/" + folder + "/" + "SHA512SUMS"
        lines = [line.rstrip('\n') for line in open(shaSumPath)]
        pattern = re.compile(r'(?P<hash>[a-zA-Z0-9]+)[\s]+%s'%(leaf))
        logging.info("verifying rpkg hash")
        for line in lines:
            match = pattern.search(line)
            if match:
                fileHash.append(match.group('hash'))
        if len(fileHash) != 1:
            logging.warning('Multiple hash found matching the package, this should not happend')
        if utils.sha512(utils.FOLDER_PATH + "/" + self.path) in fileHash:
            logging.info("=> OK!\n")
            return True
        utils.fail("hash could not be verified")

    def getMode(self):
        return self.version.mode

    def isCompatible(self):
        return utils.check_plugin_compatibility(self.metadata)

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


