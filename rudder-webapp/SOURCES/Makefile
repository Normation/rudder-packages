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
PAGES_WITH_VERSION = "rudder/rudder-web/src/main/webapp/index.html" "rudder/rudder-web/src/main/webapp/templates-hidden/common-layout.html"
CURRENT_YEAR = $(date +'%Y')

localdepends: ./rudder-sources ./maven/bin/mvn ./rudder-users.xml ./rudder-doc ./rudder-doc/html/rudder-doc.pdf ./.gitignore ./rudder.war

/usr/bin/wget:
	sudo aptitude --assume-yes install wget

./maven.tgz: /usr/bin/wget
	# Original URL: http://apache.multidist.com/maven/binaries/apache-maven-$(MAVEN_RELEASE)-bin.tar.gz
	$(WGET) -O ./maven.tgz.dl http://www.normation.com/tarball/apache-maven-$(MAVEN_RELEASE)-bin.tar.gz
	mv ./maven.tgz.dl ./maven.tgz

./maven/bin/mvn: ./maven.tgz
	tar -xzf ./maven.tgz -C .
	rm -rf ./maven
	mv ./apache-maven-$(MAVEN_RELEASE) ./maven
	sed 's|<!--PROXY-->|$(MAVEN_PROXY)|g' ./settings-external.xml.tpl > ./settings-external.xml

./rudder.war: ./maven/bin/mvn ./rudder-sources
	./maven/bin/mvn -s settings-external.xml --batch-mode org.apache.maven.plugins:maven-dependency-plugin:3.0.0:copy -Dartifact=com.normation.rudder:rudder-web:$$(sed -n '/<parent>/,/<.parent>/s/.*<version>\(.*\)<.version>.*/\1/p' ./rudder-sources/rudder/pom.xml):war -DoutputDirectory=. && mv rudder-web*.war rudder.war || true

./rudder-sources.tar.bz2:
	$(WGET) -O rudder-sources.tar.bz2.dl http://www.rudder-project.org/archives/rudder-sources-${RUDDER_VERSION_TO_PACKAGE}.tar.bz2
	mv ./rudder-sources.tar.bz2.dl ./rudder-sources.tar.bz2

./rudder-sources: ./rudder-sources.tar.bz2
	tar -xjf rudder-sources.tar.bz2
	mv rudder-sources-*/ rudder-sources/

	# Change rudder version displayed in the Web UI
	for page in $(PAGES_WITH_VERSION); do \
	  sed -i "s%@PACKAGING_RUDDER_MAJOR_VERSION@%$(RUDDER_MAJOR_VERSION)%" "rudder-sources/$${page}" ; \
	  sed -i "s%@PACKAGING_RUDDER_VERSION@%$(RUDDER_VERSION_TO_PACKAGE)%" "rudder-sources/$${page}" ; \
	  sed -i "s%@PACKAGING_CURRENT_YEAR@%$(CURRENT_YEAR)%" "rudder-sources/$${page}" ; \
	done

./rudder-doc: /usr/bin/wget
	# Get user manual from rudder-project.org and rename directory containing it to rudder-doc
	$(WGET) -P ./rudder-doc/html -r -np -nH --cut-dirs=2 http://www.rudder-project.org/doc-${RUDDER_MAJOR_VERSION}/webhelp-localsearch/
	# Download the pdf version of the manual
	$(WGET) -P ./rudder-doc/pdf http://www.rudder-project.org/rudder-doc-${RUDDER_MAJOR_VERSION}/rudder-doc.pdf

./rudder-doc/html/rudder-doc.pdf: ./rudder-doc
	ln -fs ../pdf/rudder-doc.pdf ./rudder-doc/html/rudder-doc.pdf

./rudder-users.xml: ./rudder-sources
	cp ./rudder-sources/rudder/rudder-web/src/main/resources/demo-rudder-users.xml ./rudder-users.xml

./.gitignore: ./configuration-repository-gitignore
	cp ./configuration-repository-gitignore ./.gitignore

localclean:
	rm -rf ./rudder-users.xml
	rm -rf ./maven/
	rm -rf ./rudder-sources
	rm -rf ./rudder-doc
	rm -rf ./.gitignore
	rm -rf ./settings-external.xml

veryclean:
	rm -f ./rudder-sources.tar.bz2
	rm -rf ./maven.tgz

.PHONY: localclean localdepends veryclean
