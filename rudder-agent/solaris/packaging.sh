# this is not the final build script just an indication of what has to be dont

# dependencies
pkg install gcc
pkg install gnu-binutils

# use gnu tools to build
export PATH=/usr/gnu/bin:/usr/gnu/x86_64-pc-solaris2.11/bin/:$PATH

# build
gmake build RUDDER_VERSION_TO_PACKAGE=6.0.3 USE_SYSTEM_OPENSSL=false USE_SYSTEM_ZLIB=false USE_SYSTEM_LMDB=false USE_SYSTEM_PCRE=false USE_SYSTEM_PERL=false USE_SYSTEM_FUSION=false USE_SYSTEM_CURL=false USE_SYSTEM_YAML=false USE_SYSTEm_XML=false OS_FAMILY=solaris

# install in a temporary directory
gmake install DESTDIR=$(pwd)/tmp-build RUDDER_VERSION_TO_PACKAGE=6.0.3 USE_SYSTEM_OPENSSL=false USE_SYSTEM_ZLIB=false USE_SYSTEM_LMDB=false USE_SYSTEM_PCRE=false USE_SYSTEM_PERL=false USE_SYSTEM_FUSION=false USE_SYSTEM_CURL=false USE_SYSTEM_YAML=false USE_SYSTEM_XML=false OS_FAMILY=solaris

# post install
/opt/rudder/share/package-scripts/rudder-agent-postinst "true" "solaris" "false" ""

