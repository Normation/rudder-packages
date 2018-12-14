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

MAVEN_RELEASE = 3.5.4
MAVEN_SHA256 = ce50b1c91364cb77efe3776f756a6d92b76d9038b0a0782f7d53acf1e997a14d
JETTY_RELEASE = 9.4.11
DATE_RELEASE = 20180605
JETTY_SHA256 = c286e87f36d56ef40821c5acb99acf3f90873d39bdbc1851f482c556c2dca5ae
TMP_DIR := $(shell mktemp -dq)

MAVEN_PROXY := $(if $(PROXY), $(shell echo "$(PROXY)" |  perl -ne ' \
    if (m|(https?)://(?:([^:@]+)(?::([^@]+))?\@)?([^:/]+)(?::([0-9]+))?|) { \
        chomp; \
        my $$proto = "<protocol>$$1</protocol>"; \
        my $$user = defined($$2) ? "<username>$$2</username>" : ""; \
        my $$pass = defined($$3) ? "<password><![CDATA[$$3]]></password>" : ""; \
        my $$host = "<host>$$4</host>";  \
        my $$id   = "<id>$$4</id>"; \
        my $$port = defined($5) ? "<port>$$5</port>" : ""; \
        print "<proxies> <proxy> <active>true</active> $$id $$proto $$user $$pass $$host $$port </proxy> </proxies>"; \
    }'))

.DEFAULT_GOAL := localdepends

RUDDER_VERSION_TO_PACKAGE = <put Rudder version or version-snapshot here>
RUDDER_MAJOR_VERSION := $(shell echo ${RUDDER_VERSION_TO_PACKAGE} | cut -d'.' -f 1-2)
VIRTUALENV_RELEASE = 16.0.0
VIRTUALENV_SHA256 = ca07b4c0b54e14a91af9f34d0919790b016923d157afda5efdde55c96718f752


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
CURL = curl -s -L -o
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

localdepends: ./rudder-sources ./maven/bin/mvn ./rudder-users.xml ./rudder-doc ./.gitignore ./rudder.war ./endpoint.war ./inventory-web.properties ./jetty
	rm -rf $(TMP_DIR)

/usr/bin/wget:
	sudo aptitude --assume-yes install wget

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


./maven.tgz: /usr/bin/wget
	# Original URL: http://apache.multidist.com/maven/binaries/apache-maven-$(MAVEN_RELEASE)-bin.tar.gz
	$(GET) ./maven.tgz.dl https://repository.rudder.io/build-dependencies/maven/apache-maven-$(MAVEN_RELEASE)-bin.tar.gz $(MAVEN_SHA256)
	mv ./maven.tgz.dl ./maven.tgz

./maven/bin/mvn: ./maven.tgz
	tar -xzf ./maven.tgz -C .
	rm -rf ./maven
	mv ./apache-maven-$(MAVEN_RELEASE) ./maven
	sed 's|<!--PROXY-->|$(MAVEN_PROXY)|g' ./settings-external.xml.tpl > ./settings-external.xml

./rudder.war: ./maven/bin/mvn ./rudder-sources
	./maven/bin/mvn -s settings-external.xml --batch-mode org.apache.maven.plugins:maven-dependency-plugin:3.0.0:copy -Dmaven.repo.local=./.m2/repository -Dartifact=com.normation.rudder:rudder-web:$$(sed -n '/<parent>/,/<.parent>/s/.*<version>\(.*\)<.version>.*/\1/p' ./rudder-sources/rudder/pom.xml):war -DoutputDirectory=. && mv rudder-web*.war rudder.war || true

./endpoint.war: ./maven/bin/mvn ./rudder-sources
	./maven/bin/mvn -s settings-external.xml --batch-mode org.apache.maven.plugins:maven-dependency-plugin:3.0.0:copy -Dmaven.repo.local=./.m2/repository  -Dartifact=com.normation.inventory:inventory-provisioning-web:$$(sed -n '/<parent>/,/<.parent>/s/.*<version>\(.*\)<.version>.*/\1/p' ./rudder-sources/ldap-inventory/pom.xml):war -DoutputDirectory=. && mv inventory-provisioning-web*.war endpoint.war || true

./rudder-sources.tar.bz2:
	$(GET) rudder-sources.tar.bz2.dl https://www.rudder-project.org/archives/rudder-sources-${RUDDER_VERSION_TO_PACKAGE}.tar.bz2 ""
	mv ./rudder-sources.tar.bz2.dl ./rudder-sources.tar.bz2

./rudder-sources: ./rudder-sources.tar.bz2
	tar -xjf rudder-sources.tar.bz2
	mv rudder-sources-*/ rudder-sources/
	# Remove tests folders we don't want to package
	find rudder-sources/rudder-techniques -name "tests" -type d | xargs -r rm -r

./inventory-web.properties: ./rudder-sources
	cp ./rudder-sources/ldap-inventory/inventory-provisioning-web/src/main/resources/configuration.properties.sample ./inventory-web.properties

./rudder-doc: /usr/bin/wget
	# Get user manual from rudder-project.org and rename directory containing it to rudder-doc
	$(GET) doc-${RUDDER_MAJOR_VERSION}.tar.gz https://docs.rudder.io/archives/doc-${RUDDER_MAJOR_VERSION}.tar.gz ""
	tar -xzf doc-${RUDDER_MAJOR_VERSION}.tar.gz
	mkdir -p rudder-doc
	mv doc-${RUDDER_MAJOR_VERSION} rudder-doc/html

./rudder-users.xml: ./rudder-sources
	cp ./rudder-sources/rudder/rudder-web/src/main/resources/demo-rudder-users.xml ./rudder-users.xml

./virtualenv.tgz: /usr/bin/wget
	# Original URL: https://pypi.python.org/packages/source/v/virtualenv/virtualenv-12.0.7.tar.gz
	$(GET) virtualenv.tgz https://repository.rudder.io/build-dependencies/virtualenv/virtualenv-$(VIRTUALENV_RELEASE).tar.gz $(VIRTUALENV_SHA256)

./virtualenv/virtualenv.py: ./virtualenv.tgz
	tar -xzf ./virtualenv.tgz
	mv ./virtualenv-$(VIRTUALENV_RELEASE)/ virtualenv/


./.gitignore: ./configuration-repository-gitignore
	cp ./configuration-repository-gitignore ./.gitignore

localclean:
	rm -rf ./rudder-users.xml
	rm -rf ./maven/
	rm -rf ./.m2/
	rm -rf ./rudder-sources
	rm -rf ./rudder-doc
	rm -rf ./.gitignore
	rm -rf ./settings-external.xml
	rm -rf virtualenv/
	rm -rf ncf-api-virtualenv
	rm -rf ./inventory-web.properties
	rm -rf ./jetty
	rm -f ../debian/rudder-jetty.init
	rm -f ../debian/rudder-jetty.default
	rm -rf $(TMP_DIR)


veryclean:
	rm -f ./rudder-sources.tar.bz2
	rm -rf ./maven.tgz
	rm -f virtualenv.tgz
	rm -rf $(TMP_DIR)

.PHONY: localclean localdepends veryclean
