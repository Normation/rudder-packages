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

JETTY_RELEASE = 7.6.14
DATE_RELEASE = 20131031
TMP_DIR := $(shell mktemp -dq)
WGET := $(if $(PROXY), http_proxy=$(PROXY) ftp_proxy=$(PROXY)) /usr/bin/wget -q

localdepends: ./jetty7
	rm -rf $(TMP_DIR)

./jetty7: /usr/bin/wget
	# Download and uncompress the Jetty distribution
	# Original URL: http://dist.codehaus.org/jetty/jetty-hightide-$(JETTY_RELEASE)/jetty-hightide-$(JETTY_RELEASE).v$(DATE_RELEASE).tar.gz
	$(WGET) -O $(TMP_DIR)/jetty.tgz http://www.normation.com/tarball/jetty-hightide-$(JETTY_RELEASE).v$(DATE_RELEASE).tar.gz
	tar xzf $(TMP_DIR)/jetty.tgz -C $(TMP_DIR)
	mv $(TMP_DIR)/jetty-hightide-$(JETTY_RELEASE).v$(DATE_RELEASE) ./jetty7
	rm -rf $(TMP_DIR)

	# Remove useless / demo elements from Jetty
	rm -rf ./jetty7/javadoc

	rm -rf ./jetty7/webapps/*
	rm -rf ./jetty7/contexts/*

	touch ./jetty7/webapps/.donotdelete

	# Change default log directory for jetty
	sed -i 's/default=\".\/logs\"/default=\"\/var\/log\/rudder\/webapp\"/g' ./jetty7/etc/jetty-logging.xml

	# Change jetty's default settings to listen on localhost only
	sed -i 's/\(<Set\ name=\"host\"><Property\ name=\"jetty.host\"\ \)\(\/>\)/\1default="127.0.0.1"\2/g' ./jetty7/etc/jetty.xml

	# Set jetty requestHeaderSize if not yet modified
	grep 'Set name="requestHeaderSize"' ./jetty7/etc/jetty.xml >/dev/null || sed -i -e '/<New class="org.eclipse.jetty.server.nio.SelectChannelConnector">/s/$$/\n            <Set name="requestHeaderSize">8192<\/Set>/' ./jetty7/etc/jetty.xml

	# Change jetty.sh before distincts files
	patch -p0 -s < patches/jetty/jetty-init-umask.patch
	patch -p0 -s < patches/jetty/jetty-init-stop-fix.patch
	patch -p0 -s < patches/jetty/jetty-init-sizecheck.patch
	patch -p0 -s < patches/jetty/jetty-init-use-rudder-jetty-defaults.patch
	patch -p0 -s < patches/jetty/jetty-init-check-java-version.patch
	patch -p0 -s < patches/jetty/jetty-init-prevent-false-failed-starts.patch

	cp ./jetty7/bin/jetty.sh ./jetty7/bin/jetty-debian.sh
	cp ./jetty7/bin/jetty.sh ./jetty7/bin/jetty-rpm.sh

	patch -p0 -s < patches/jetty/jetty-init-lsb-fix-debian.patch
	patch -p0 -s < patches/jetty/jetty-init-lsb-fix-rpm.patch

	cp ./jetty7/bin/jetty-rpm.sh ./jetty7/bin/jetty-sles.sh
	patch -p0 -s < patches/jetty/jetty-init-sles.patch
	
	# Provide jetty's init script to the debian package's standard location
	cp ./jetty7/bin/jetty-debian.sh ../debian/rudder-jetty.init
	cp ./rudder-jetty.default ../debian/rudder-jetty.default
	chmod +x ../debian/rudder-jetty.init

/usr/bin/wget:
	sudo aptitude --assume-yes install wget

localclean:
	rm -rf ./jetty7
	rm -f ../debian/rudder-jetty.init
	rm -f ../debian/rudder-jetty.default
	rm -rf $(TMP_DIR)

veryclean:
	rm -f ./rudder-sources.tar.bz2
	rm -rf $(TMP_DIR)

.PHONY: localclean localdepends veryclean
