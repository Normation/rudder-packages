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

RUDDER_VERSION_TO_PACKAGE =
RUDDER_MAJOR_VERSION := $(shell echo ${RUDDER_VERSION_TO_PACKAGE} | cut -d'.' -f 1-2)

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

localdepends: ./rudder-sources ./maven/bin/mvn ./rudder-users.xml ./rudder-doc ./.gitignore ./rudder.war

/usr/bin/wget:
	sudo aptitude --assume-yes install wget

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

./rudder-sources.tar.bz2:
	$(GET) rudder-sources.tar.bz2.dl https://www.rudder-project.org/archives/rudder-sources-${RUDDER_VERSION_TO_PACKAGE}.tar.bz2 ""
	mv ./rudder-sources.tar.bz2.dl ./rudder-sources.tar.bz2

./rudder-sources: ./rudder-sources.tar.bz2
	tar -xjf rudder-sources.tar.bz2
	mv rudder-sources-*/ rudder-sources/

./rudder-doc: /usr/bin/wget
	# Get user manual from rudder-project.org and rename directory containing it to rudder-doc
	$(GET) doc-${RUDDER_MAJOR_VERSION}.tar.gz https://docs.rudder.io/archives/doc-${RUDDER_MAJOR_VERSION}.tar.gz ""
	tar -xzf doc-${RUDDER_MAJOR_VERSION}.tar.gz
	mkdir -p rudder-doc
	mv doc-${RUDDER_MAJOR_VERSION} rudder-doc/html

./rudder-users.xml: ./rudder-sources
	cp ./rudder-sources/rudder/rudder-web/src/main/resources/demo-rudder-users.xml ./rudder-users.xml

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

veryclean:
	rm -f ./rudder-sources.tar.bz2
	rm -rf ./maven.tgz

.PHONY: localclean localdepends veryclean
