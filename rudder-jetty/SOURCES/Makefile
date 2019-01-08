#####################################################################################
# Copyright 2011 Normation SAS
#####################################################################################
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, Version 3.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#####################################################################################

.DEFAULT_GOAL := localdepends

JETTY_RELEASE = 9.4.11
DATE_RELEASE = 20180605
JETTY_SHA256 = c286e87f36d56ef40821c5acb99acf3f90873d39bdbc1851f482c556c2dca5ae
TMP_DIR := $(shell mktemp -dq)

# GENERIC_GET: do not remove this line
# This is a generic get code that is common to many of our Makefiles.
# The tag is here to find them. Rudder agent has an even more generic one.
# If you change this code, change all the places where you can find this tag too.
# It is duplicated because it is the code that is used to manage dependency
# to other repositories, hence allowing deduplication of other code.
# Autodetect wget, curl or fetch usage and proxy configuration
# Usage: $(GET) <destination_file> <url> <hash>
PROXY_ENV = $(if $(PROXY), http_proxy=$(PROXY) ftp_proxy=$(PROXY))
# No accept encoding to prevent the webserver form altering the distributed file
WGET = wget -q --header="accept-encoding:" -O
CURL = curl -s --http1.1 -L -o
ifneq (,$(wildcard /usr/bin/curl))
_GET = $(PROXY_ENV) $(CURL)
else
_GET = $(PROXY_ENV) $(WGET)
endif
# Pass an empty string to skip hash check
GET=get() { $(_GET) "$$1.part" "$$2" && { openssl dgst -sha256 "$$1.part" | grep -q "$$3" || { echo "Wrong checksum, aborting"; exit 1; }; } && mv "$$1.part" "$$1"; }; get

FIND := /usr/bin/find
# this is the orginal URL for Jetty distribution
JETTY_URL := "http://repo1.maven.org/maven2/org/eclipse/jetty/jetty-distribution/$(JETTY_RELEASE).v$(DATE_RELEASE)/jetty-distribution-$(JETTY_RELEASE).v$(DATE_RELEASE).tar.gz"
# this is our "local" copy, used to make reproducible build whatever happen to original URL
JETTY_NRM_URL := "https://repository.rudder.io/build-dependencies/jetty/jetty-distribution-$(JETTY_RELEASE).v$(DATE_RELEASE).tar.gz"

localdepends: ./jetty
	rm -rf $(TMP_DIR)

./jetty:
	# Download and uncompress the Jetty distribution
	$(GET) $(TMP_DIR)/jetty.tgz $(JETTY_NRM_URL) $(JETTY_SHA256)
	tar xzf $(TMP_DIR)/jetty.tgz -C $(TMP_DIR)
	mv $(TMP_DIR)/jetty-distribution-$(JETTY_RELEASE).v$(DATE_RELEASE) ./jetty
	rm -rf $(TMP_DIR)

	# Remove useless / demo elements from Jetty
	# jetty9 is clean now - only demo-base
	rm -rf ./jetty/demo-base

	# Change jetty.sh before distincts files
	patch -p0 -s < patches/jetty/jetty-init-umask.patch
	patch -p0 -s < patches/jetty/jetty-init-stop-fix.patch
	patch -p0 -s < patches/jetty/jetty-init-sizecheck.patch
	patch -p0 -s < patches/jetty/jetty-init-use-rudder-jetty-defaults.patch
	patch -p0 -s < patches/jetty/jetty-init-prevent-false-failed-starts.patch
	patch -p0 -s < patches/jetty/jetty-init-redirect-stderrout.patch
	patch -p0 -s < patches/jetty/jetty-init-stop-forcestop.patch

	cp ./jetty/bin/jetty.sh ./jetty/bin/jetty-debian.sh
	cp ./jetty/bin/jetty.sh ./jetty/bin/jetty-rpm.sh

	patch -p0 -s < patches/jetty/jetty-init-lsb-fix-debian.patch
	patch -p0 -s < patches/jetty/jetty-init-lsb-fix-rpm.patch
	patch -p0 -s < patches/jetty/jetty-init-softokn-version-check.patch

	cp ./jetty/bin/jetty-rpm.sh ./jetty/bin/jetty-sles.sh
	patch -p0 -s < patches/jetty/jetty-init-sles.patch
	patch -p0 -s < patches/jetty/jetty-init-ulimit.patch
	
	# Provide jetty's init script to the debian package's standard location
	cp ./jetty/bin/jetty-debian.sh ../debian/rudder-jetty.init
	cp ./rudder-jetty.default ../debian/rudder-jetty.default
	chmod +x ../debian/rudder-jetty.init

	# Restore the name for log file from version of Rudder before 4.3 (see https://www.rudder-project.org/redmine/issues/12607)
	patch -p0 -s < patches/jetty/jetty-console-capture-restore-log-filename.patch

	# Make sure there were no rejects
	test `$(FIND) . -name \*.rej | wc -l` = 0

/usr/bin/wget:
	sudo aptitude --assume-yes install wget

localclean:
	rm -rf ./jetty
	rm -f ../debian/rudder-jetty.init
	rm -f ../debian/rudder-jetty.default
	rm -rf $(TMP_DIR)

veryclean:
	rm -f ./rudder-sources.tar.bz2
	rm -rf $(TMP_DIR)

.PHONY: localclean localdepends veryclean
