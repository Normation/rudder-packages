#####################################################################################
# Copyright 2014 Normation SAS
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

RUDDER_VERSION_TO_PACKAGE = <put Rudder version or version-snapshot here>
CFENGINE_RELEASE = 3.6.0rc2-build1
LMDB_RELEASE = 0.9.11
TMP_DIR := $(shell mktemp -dq /tmp/rudder.XXXXXX)
WGET := $(if $(PROXY), http_proxy=$(PROXY) ftp_proxy=$(PROXY)) /usr/bin/wget -q
PATCH := /usr/bin/patch

localdepends: ./initial-promises ./lmdb-source ./cfengine-source ../debian/rudder-agent.init ../debian/rudder-agent.default ./rudder-agent.cron ../debian/rudder-agent.cron.d
	rm -rf $(TMP_DIR)

./cfengine-source: /usr/bin/wget
	# Original URL: https://github.com/cfengine/core/archive/$(CFENGINE_RELEASE).tar.gz
	$(WGET) -O $(TMP_DIR)/cfengine.tgz http://www.normation.com/tarball/core-$(CFENGINE_RELEASE).tar.gz
	tar xzf $(TMP_DIR)/cfengine.tgz -C $(TMP_DIR)
	mv $(TMP_DIR)/core-$(CFENGINE_RELEASE) ./cfengine-source
	# No patches to apply

./lmdb-source: /usr/bin/wget
	# Original URL: http://ftp.fr.debian.org/debian/pool/main/l/lmdb/lmdb_$(LMDB_RELEASE).orig.tar.xz
	$(WGET) -O $(TMP_DIR)/lmdb.tgz http://www.normation.com/tarball/lmdb-$(LMDB_RELEASE).tar.gz
	tar xzf $(TMP_DIR)/lmdb.tgz -C $(TMP_DIR)
	mv $(TMP_DIR)/lmdb-$(LMDB_RELEASE) ./lmdb-source

./rudder-sources.tar.bz2:
	$(WGET) -O rudder-sources.tar.bz2 http://www.rudder-project.org/archives/rudder-sources-$(RUDDER_VERSION_TO_PACKAGE).tar.bz2

./rudder-sources: ./rudder-sources.tar.bz2
	tar -xjf rudder-sources.tar.bz2
	mv rudder-sources-*/ rudder-sources/

./initial-promises: ./rudder-sources
	rm -rf ./initial-promises/
	cp -a ./rudder-sources/rudder-techniques/initial-promises/node-server/ ./initial-promises

../debian/rudder-agent.init:
	cp ./rudder-agent.init ../debian/

../debian/rudder-agent.default:
	cp ./rudder-agent.default ../debian/

./rudder-agent.cron: ./rudder-sources
	cp ./rudder-sources/rudder-techniques/techniques/system/common/1.0/rudder_agent_community_cron.st ./rudder-agent.cron
	# Set unexpanded variables of the cron file
	sed 's@\$${sys.workdir}@/var/rudder/cfengine-community@g' -i rudder-agent.cron
	sed 's@\$${g.rudder_base}@/opt/rudder@g' -i rudder-agent.cron
	sed  's@\\&\\&@\&\&@g' -i rudder-agent.cron
	sed  's@\\&1@\&1@g' -i rudder-agent.cron

../debian/rudder-agent.cron.d: ./rudder-agent.cron
	cp ./rudder-agent.cron ../debian/rudder-agent.cron.d

/usr/bin/wget:
	sudo apt-get --assume-yes install wget

localclean:
	rm -rf ./cfengine-source
	rm -rf ./lmdb-source
	rm -rf ./initial-promises
	rm -f ../debian/rudder-agent.init
	rm -f ../debian/rudder-agent.default
	rm -rf ./rudder-sources
	rm -f ./rudder-agent.cron ../debian/rudder-agent.cron.d

veryclean:
	rm -f ./rudder-sources.tar.bz2

.PHONY: localclean localdepends veryclean
