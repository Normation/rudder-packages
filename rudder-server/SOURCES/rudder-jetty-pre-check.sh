#!/bin/sh

# This script is started before the jetty service and ensures everything is correct.
# If it fails, the service will not start.

# Gets the memory size (Xmx+MaxPermSize) needed by Java megabytes as argument.
# Checks if there is enough available RAM + Swap to contain the JVM.
checkAvailableRam()
{
  # By default, add 10% to the given needed memory size to have a safe
  # margin (leave some memory for the OS)
  TOTAL_MEM_NEEDED=$((((${1})*100)/90))
  # $7 is "available" memory.
  TOTAL_MEM_AVAILABLE=$(($(free -m|awk '/^Mem:/{print $7}')+$(free -m|awk '/^Swap:/{print $2}')))
  if [ ${TOTAL_MEM_AVAILABLE} -le ${TOTAL_MEM_NEEDED} ]; then
    echo "WARNING: Not enough free memory to start Jetty (about ${TOTAL_MEM_NEEDED}MB are needed). Trying anyway, but the application is likely to fail."
  fi
}

# Check that the OS support C.UTF-8 so that our export in rudder-jetty.conf will be understood.
# See: https://issues.rudder.io/issues/29869
checkLocaleCharmap()
{
  CHARMAP=$(locale charmap 2>/dev/null)
  if [ "${CHARMAP}" != "UTF-8" ]; then
    echo "WARNING: locale '${LC_ALL}' resolves to charmap '${CHARMAP}' instead of UTF-8: it is either not a UTF-8 locale, or not available on this system."
  fi
}


# Get configured XMX and locale
. /etc/default/rudder-jetty

# Checking if enough RAM is available for Jetty to use
# Metaspace is auomanaged in JDK8+. Rudder needs 150Mo of it.
checkAvailableRam $((${JAVA_XMX}+150))

# Checking that file names will be encoded in UTF-8
checkLocaleCharmap
