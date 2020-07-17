#!/bin/bash

set -xe

VERSION="$1"
BUILD_DIR="BUILD"

BASE=$(readlink -f $(dirname $0)/..)
cd "${BASE}/SOURCES"

# sample code, builder shouls already have the source code
#wget -q --header="accept-encoding:" -O rudder-sources.tar.bz2 "http://repository.rudder.io/sources/6.0-nightly/rudder-sources-${VERSION}~rc1-latest.tar.bz2"

# 1- install build-dependencies

pkg install gcc gnu-binutils || true

# 2- configure, make and install into tmpdir

# use gnu tools to build
export PATH=/usr/gnu/bin:/usr/gnu/x86_64-pc-solaris2.11/bin/:/usr/gnu/sparc-sun-solaris2.11/bin:$PATH

# gcc needs an option translator to work with cpan builds
cp -p "${BASE}/solaris/cc" /usr/gnu/bin/

env="RUDDER_VERSION_TO_PACKAGE=${VERSION}"

./configure --with-openssl --with-libcurl --with-zlib --with-lmdb --with-pcre --with-jq --with-libyaml --with-libxml2

# build
# solaris 11.3 doesn't detect properly 64 bitness
gmake build ${env} BUILD_CFLAGS=-m64

# install in a temporary directory
mkdir -p "${BASE}/${BUILD_DIR}"
gmake install ${env} DESTDIR="${BASE}/${BUILD_DIR}"

# 3- generate package (doc, https://docs.oracle.com/cd/E26502_01/html/E21383/pkgcreate.html)

cd "${BASE}"

# file list
pkgsend generate "${BUILD_DIR}" | pkgfmt > rudder-agent.p5m.1

# metadata
pkgmogrify -DARCH=`uname -p` -DVERSION=${VERSION} -DTAG=0 rudder-agent.p5m.1 solaris/rudder-agent.metadata.mog | pkgfmt > rudder-agent.p5m.2

# dependencies
# TODO add pkg install pkg:/text/gnu-grep as a dependency
pkgdepend generate -md "${BUILD_DIR}" rudder-agent.p5m.2 | pkgfmt > rudder-agent.p5m.3
pkgdepend resolve -m rudder-agent.p5m.3

# actuators
pkgmogrify rudder-agent.p5m.3.res solaris/rudder-agent.postinst.mog | pkgfmt > rudder-agent.p5m.4.res

# lint
pkglint -c ~/solaris-reference -r http://pkg.oracle.com/solaris/release rudder-agent.p5m.4.res

# generate repo
pkgrepo create rudder-nightly
pkgrepo -s rudder-nightly set publisher/prefix=normation
pkgsend -s rudder-nightly publish -d BUILD rudder-agent.p5m.4.res

# tar for easy transportation
tar czf rudder-nightly.tgz rudder-nightly

# create repo archive for easy transpotration to another solaris
#pkgrecv -s rudder-nightly -a -d rudder-nightly.p5p rudder-agent

# merge solaris + i386 into a single package : https://docs.oracle.com/cd/E26502_01/html/E29030/pkgmerge-1.html#REFMAN1pkgmerge-1
# pkgmerge -s arch=sparc,http://src1.example.com -s arch=i386,http://src2.example.com -d /path/to/target/repository

# post install
#/opt/rudder/share/package-scripts/rudder-agent-postinst "true" "solaris" "false" "orchestrateur"

