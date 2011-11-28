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

MAVEN_RELEASE = 2.2.1
WGET := $(if $(PROXY), http_proxy=$(PROXY) ftp_proxy=$(PROXY)) /usr/bin/wget

.DEFAULT_GOAL := localdepends

GIT_BRANCH_RUDDER = <put branch or tag name here>

localdepends: ./source ./maven2/bin/mvn ./rudder-users.xml

/usr/bin/wget:
	sudo aptitude --assume-yes install wget

./maven2/bin/mvn: /usr/bin/wget
	$(WGET) -O ./maven.tgz http://www.normation.com/tarball/apache-maven-$(MAVEN_RELEASE)-bin.tar.gz
	tar -xvzf ./maven.tgz -C .
	rm -rf ./maven2
	mv ./apache-maven-$(MAVEN_RELEASE) ./maven2
	rm -rf ./maven.tgz

./source:
	mkdir -p ./source
	cd ./source && git clone --depth 1 git://github.com/Normation/rudder-parent-pom.git
	cd ./source/rudder-parent-pom && git checkout $(GIT_BRANCH_RUDDER) || rm -rf ./source/rudder-parent-pom
	cd ./source && git clone --depth 1 git://github.com/Normation/rudder-commons.git
	cd ./source/rudder-commons && git checkout $(GIT_BRANCH_RUDDER) || rm -rf ./source/rudder-commons
	cd ./source && git clone --depth 1 git://github.com/Normation/scala-ldap.git
	cd ./source/scala-ldap && git checkout $(GIT_BRANCH_RUDDER) || rm -rf ./source/scala-ldap
	cd ./source && git clone --depth 1 git://github.com/Normation/ldap-inventory.git
	cd ./source/ldap-inventory && git checkout $(GIT_BRANCH_RUDDER) || rm -rf ./source/ldap-inventory
	cd ./source && git clone --depth 1 git://github.com/Normation/cf-clerk.git
	cd ./source/cf-clerk && git checkout $(GIT_BRANCH_RUDDER) || rm -rf ./source/cf-clerk
	cd ./source && git clone --depth 1 git://github.com/Normation/rudder.git
	cd ./source/rudder && git checkout $(GIT_BRANCH_RUDDER) || rm -rf ./source/rudder

./rudder-users.xml: ./source
	cp ./source/rudder/rudder-web/src/main/resources/demo-rudder-users.xml ./rudder-users.xml

/usr/bin/git:
	sudo apt-get --assume-yes install git-core

localclean:
	rm -rf ./source
	rm -rf ./rudder-users.xml
	rm -rf ./maven2/

veryclean:

.PHONY: localclean localdepends veryclean
