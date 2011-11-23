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

JETTY_RELEASE = 7.2.2
DATE_RELEASE = 20101205
TMP_DIR := $(shell mktemp -dq)
WGET := $(if $(PROXY), http_proxy=$(PROXY) ftp_proxy=$(PROXY)) /usr/bin/wget

localdepends: ./jetty7

./jetty7: /usr/bin/wget
	# Download and uncompress the Jetty distribution
	$(WGET) -O $(TMP_DIR)/jetty.tgz http://www.normation.com/tarball/jetty-hightide-$(JETTY_RELEASE).v$(DATE_RELEASE).tar.gz
	tar xvzf $(TMP_DIR)/jetty.tgz -C $(TMP_DIR)
	mv $(TMP_DIR)/jetty-hightide-$(JETTY_RELEASE).v$(DATE_RELEASE) ./jetty7
	rm -rf $(TMP_DIR)

	# Change default log directory for jetty
	sed -i 's/default=\".\/logs\"/default=\"\/var\/log\/rudder\/webapp\"/g' ./jetty7/etc/jetty-logging.xml

	# Change jetty's default settings to listen on localhost only
	sed -i 's/\(<Set\ name=\"host\"><Property\ name=\"jetty.host\"\ \)\(\/>\)/\1default="127.0.0.1"\2/g' ./jetty7/etc/jetty.xml

	# Change jetty.sh before distincts files
	patch -p0 -s < jetty-init-rudder.patch

	cp ./jetty7/bin/jetty.sh ./jetty7/bin/jetty-debian.sh
	cp ./jetty7/bin/jetty.sh ./jetty7/bin/jetty-sles.sh

	patch -p0 -s < jetty-init-lsb-fix-debian.patch
	patch -p0 -s < jetty-init-lsb-fix-sles.patch


	# Provide jetty's init script to the debian package's standard location
	cp ./jetty7/bin/jetty-debian.sh ../debian/jetty.init
	cp ./rudder-jetty.default ../debian/jetty.default

/usr/bin/wget:
	sudo aptitude --assume-yes install wget

localclean:

veryclean:
	rm -rf ./jetty7
	rm -f ../debian/jetty.init
	rm -f ../debian/jetty.default

.PHONY: localclean localdepends veryclean
