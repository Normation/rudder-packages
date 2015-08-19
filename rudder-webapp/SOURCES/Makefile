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
RUDDER_MAJOR_VERSION := $(shell echo ${RUDDER_VERSION_TO_PACKAGE} | cut -d'.' -f 1-2)

localdepends: ./rudder-sources ./maven/bin/mvn ./rudder-users.xml ./rudder-doc ./rudder-doc/html/rudder-doc.pdf

/usr/bin/wget:
	sudo aptitude --assume-yes install wget

./maven.tgz: /usr/bin/wget
	# Original URL: http://apache.multidist.com/maven/binaries/apache-maven-$(MAVEN_RELEASE)-bin.tar.gz
	$(WGET) -O ./maven.tgz http://www.normation.com/tarball/apache-maven-$(MAVEN_RELEASE)-bin.tar.gz

./maven/bin/mvn: ./maven.tgz
	tar -xzf ./maven.tgz -C .
	rm -rf ./maven
	mv ./apache-maven-$(MAVEN_RELEASE) ./maven

./rudder-sources.tar.bz2:
	$(WGET) -O rudder-sources.tar.bz2 http://www.rudder-project.org/archives/rudder-sources-${RUDDER_VERSION_TO_PACKAGE}.tar.bz2

./rudder-sources: ./rudder-sources.tar.bz2
	tar -xjf rudder-sources.tar.bz2
	mv rudder-sources-*/ rudder-sources/

./rudder-doc: /usr/bin/wget
	# Get user manual from rudder-project.org and rename directory containing it to rudder-doc
	$(WGET) -P ./rudder-doc/html -r -np -nH --cut-dirs=1 http://www.rudder-project.org/doc-${RUDDER_MAJOR_VERSION}/
	# Download the pdf version of the manual
	$(WGET) -P ./rudder-doc/pdf http://www.rudder-project.org/rudder-doc-${RUDDER_MAJOR_VERSION}/rudder-doc.pdf

./rudder-doc/html/rudder-doc.pdf: ./rudder-doc
	ln -fs ../pdf/rudder-doc.pdf ./rudder-doc/html/rudder-doc.pdf

./rudder-users.xml: ./rudder-sources
	cp ./rudder-sources/rudder/rudder-web/src/main/resources/demo-rudder-users.xml ./rudder-users.xml

localclean:
	rm -rf ./rudder-users.xml
	rm -rf ./maven/
	rm -rf ./rudder-sources
	rm -rf ./rudder-doc

veryclean:
	rm -f ./rudder-sources.tar.bz2
	rm -rf ./maven.tgz

.PHONY: localclean localdepends veryclean
