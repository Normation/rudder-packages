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

CFENGINE_RELEASE = 3.2.0
TMP_DIR := $(shell mktemp -dq)
WGET := $(if $(PROXY), http_proxy=$(PROXY) ftp_proxy=$(PROXY)) /usr/bin/wget
PATCH := /usr/bin/patch

localdepends: ./cfengine-source ../debian/cfengine-community.default ../debian/cfengine-community.init

./cfengine-source: /usr/bin/wget
	# Original URL: http://www.cfengine.com/source-code/download?file=cfengine-$(CFENGINE_RELEASE).tar.gz
	$(WGET) -O $(TMP_DIR)/cfengine.tgz http://www.normation.com/tarball/cfengine-$(CFENGINE_RELEASE).tar.gz
	tar xvzf $(TMP_DIR)/cfengine.tgz -C $(TMP_DIR)
	mv $(TMP_DIR)/cfengine-$(CFENGINE_RELEASE) ./cfengine-source
	rm -rf $(TMP_DIR)
	$(PATCH) -d ./cfengine-source -p0 < ./cfengine-file-edit-section-r3229.patch
	$(PATCH) -d ./cfengine-source -p0 < ./patch-reset-persistent-classes.patch

../debian/cfengine-community.default:
	cp ./cfengine-community.default ../debian/

../debian/cfengine-community.init:
	cp ./cfengine-community.init ../debian/

/usr/bin/wget:
	sudo apt-get --assume-yes install wget

localclean:

veryclean:
	rm -rf ./cfengine-source
	rm -f ../debian/cfengine-community.default
	rm -f ../debian/cfengine-community.init

.PHONY: localclean localdepends veryclean
