#!/bin/bash

set -xe

VERSION="$1"
BUILD_DIR="BUILD"

BASE=$(readlink -f $(dirname $0)/..)
cd "${BASE}/SOURCES"

version() {
  ver="$1"
  # solaris only allow numbers in its version, so here is the mapping example for rudder 6.2
  # 6.2 alpha (nightly)-> 6.2.0.0.ddd (ddd = la date comme dans git202011191134)
  # 6.2 betaX (nighty) -> 6.2.0.1.x.0.ddd
  # 6.2 betaX -> 6.2.0.1.x.1
  # 6.2 rcX (nigtly) -> 6.2.0.2.x.0.ddd
  # 6.2 rcX -> 6.2.0.2.x.1
  # 6.2.0 -> 6.2.0.3
  # 6.2.1 nightly -> 6.2.1.2.ddd
  maj_min=$(echo "${ver}" | cut -d. -f 1-3)
  extra=$(echo "${ver}" | cut -d. -f 4-)
  ddd=$(echo "${ver}" | grep git | sed 's/.*git//')
  betax=$(echo "${ver}" | grep beta | sed 's/.*beta\([0-9]\+\).*/\1/')
  rcx=$(echo "${ver}" | grep rc | sed 's/.*rc\([0-9]\+\).*/\1/')
  if echo "${extra}" | grep -q alpha; then
    echo "${maj_min}.0.${ddd}"
  elif [ "${betax}" != "" ]; then
    if [ "${ddd}" != "" ]; then
      echo "${maj_min}.1.${betax}.0.${ddd}"
    else
      echo "${maj_min}.1.${betax}.1"
    fi
  elif [ "${rcx}" != "" ]; then
    if [ "${ddd}" != "" ]; then
      echo "${maj_min}.2.${rcx}.0.${ddd}"
    else
      echo "${maj_min}.2.${rcx}.1"
    fi
  elif [ "${ddd}" != "" ]; then # should not happen, classic nightly are called rc
    echo "${maj_min}.2.${ddd}"  # but this would match the desired behaviour anyway
  else
    echo "${maj_min}.3"
  fi
}

# sample code, builder shouls already have the source code
#wget -q --header="accept-encoding:" -O rudder-sources.tar.bz2 "http://repository.rudder.io/sources/6.0-nightly/rudder-sources-${VERSION}~rc1-latest.tar.bz2"

# 1- install build-dependencies

pkg install gcc gnu-binutils flex bison || true

# 2- configure, make and install into tmpdir

# use gnu tools to build
export PATH=/usr/gnu/bin:/usr/gnu/x86_64-pc-solaris2.11/bin/:/usr/gnu/sparc-sun-solaris2.11/bin:$PATH

env="USE_SYSTEM_OPENSSL=false USE_SYSTEM_ZLIB=false USE_SYSTEM_LMDB=false USE_SYSTEM_PCRE=false USE_SYSTEM_PERL=true USE_SYSTEM_FUSION=false USE_SYSTEM_CURL=false USE_SYSTEM_AUGEAS=false USE_SYSTEM_JQ=false USE_SYSTEM_YAML=false USE_SYSTEM_XML=false USE_ACL=false USE_PIE=false"

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
SOLARIS_VERSION=$(version "${VERSION}") # compute solaris specific version
pkgmogrify -DARCH=`uname -p` -DVERSION=${SOLARIS_VERSION} -DTAG=0 -DRELEASE=${VERSION} rudder-agent.p5m.1 solaris/rudder-agent.metadata.mog | pkgfmt > rudder-agent.p5m.2

# dependencies
pkgdepend generate -md "${BUILD_DIR}" rudder-agent.p5m.2 | pkgfmt > rudder-agent.p5m.3
pkgdepend resolve -m rudder-agent.p5m.3

# provide service
svccfg validate solaris/rudder-smf.xml
manifest_dir="${BASE}/${BUILD_DIR}/var/svc/manifest/application"
mkdir -p "${manifest_dir}"
cp solaris/rudder-smf.xml "${manifest_dir}"

# postinstall 
svccfg validate solaris/rudder-postinst.xml
cp solaris/rudder-postinst.xml "${manifest_dir}"

# actuators
pkgmogrify rudder-agent.p5m.3.res solaris/rudder-agent.postinst.mog | pkgfmt > rudder-agent.p5m.4.res

# lint
pkglint -c ~/solaris-reference -r http://pkg.oracle.com/solaris/release rudder-agent.p5m.4.res

# generate a fresh repo
rm -rf rudder-repo
pkgrepo create rudder-repo
pkgrepo -s rudder-repo set publisher/prefix=normation
pkgsend -s rudder-repo publish -d BUILD rudder-agent.p5m.4.res

# generated mostly from : /usr/lib/pkg.depot-config -F -d customconfi=/usr/src/rudder-packages/package/rudder-nightly -r /tmp/runtime
publisher="rudder-repo/publisher"
base="${publisher}/normation/"
mkdir -p "${base}/status/0"
mkdir -p "${base}/versions/0"
mkdir -p "${publisher}/1"
cp solaris/repo/versions "${base}/versions/0/index.html"
cp solaris/repo/publisher "${publisher}/1/index.html"
cp solaris/repo/status "${base}/status/0/index.html"
sed -i 's/${date}/'$(date +%Y%m%dT%H%M%S)'/' "${base}/status/0/index.html"
cd rudder-repo
ln -s publisher/normation/catalog/
ln -s publisher/normation/file/
ln -s publisher/normation/versions/
ln -s publisher/normation/status/

# tar for easy transportation to publisher
tar czf rudder-nightly-${VERSION}.tgz rudder-nightly

# create repo archive for easy transpotration to another solaris
#pkgrecv -s rudder-nightly -a -d rudder-nightly.p5p rudder-agent

# merge solaris + i386 into a single package : https://docs.oracle.com/cd/E26502_01/html/E29030/pkgmerge-1.html#REFMAN1pkgmerge-1
# pkgmerge -s arch=sparc,http://src1.example.com -s arch=i386,http://src2.example.com -d /path/to/target/repository

