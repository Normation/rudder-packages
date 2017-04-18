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

MAVEN_RELEASE = 3.0.4
WGET := $(if $(PROXY), http_proxy=$(PROXY) ftp_proxy=$(PROXY)) /usr/bin/wget -q

.DEFAULT_GOAL := localdepends

RUDDER_VERSION_TO_PACKAGE = <put Rudder version or version-snapshot here>
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

localdepends: ./rudder-sources ./inventory-web.properties ./maven/bin/mvn ./endpoint.war

/usr/bin/wget:
	sudo aptitude --assume-yes install wget

./maven.tgz: /usr/bin/wget
	# Original URL: http://apache.multidist.com/maven/binaries/apache-maven-$(MAVEN_RELEASE)-bin.tar.gz
	$(WGET) -O ./maven.tgz http://www.normation.com/tarball/apache-maven-$(MAVEN_RELEASE)-bin.tar.gz

./maven/bin/mvn: ./maven.tgz
	tar -xzf ./maven.tgz -C .
	rm -rf ./maven
	mv ./apache-maven-$(MAVEN_RELEASE) ./maven
	sed 's|<!--PROXY-->|$(MAVEN_PROXY)|g' ./settings-external.xml.tpl > ./settings-external.xml

./endpoint.war: ./maven/bin/mvn ./rudder-sources
	./maven/bin/mvn -s settings-external.xml --batch-mode org.apache.maven.plugins:maven-dependency-plugin:3.0.0:copy -Dmaven.repo.local=./.m2/repository  -Dartifact=com.normation.inventory:inventory-provisioning-web:$$(sed -n '/<parent>/,/<.parent>/s/.*<version>\(.*\)<.version>.*/\1/p' ./rudder-sources/ldap-inventory/pom.xml):war -DoutputDirectory=. && mv inventory-provisioning-web*.war endpoint.war || true

./rudder-sources.tar.bz2:
	$(WGET) -O rudder-sources.tar.bz2 http://www.rudder-project.org/archives/rudder-sources-${RUDDER_VERSION_TO_PACKAGE}.tar.bz2

./rudder-sources: ./rudder-sources.tar.bz2
	tar -xjf rudder-sources.tar.bz2
	mv rudder-sources-*/ rudder-sources/

./inventory-web.properties: ./rudder-sources
	cp ./rudder-sources/ldap-inventory/inventory-provisioning-web/src/main/resources/configuration.properties.sample ./inventory-web.properties

localclean:
	rm -rf ./maven
	rm -rf ./.m2
	rm -rf ./inventory-web.properties
	rm -rf ./rudder-sources
	rm -rf ./settings-external.xml

veryclean:
	rm -f ./rudder-sources.tar.bz2
	rm -rf ./maven.tgz

.PHONY: localclean localdepends veryclean
