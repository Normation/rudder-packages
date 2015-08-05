#!/bin/sh

# To allow Rudder to provide its own version of openssl
PATH=/opt/rudder/bin:$PATH
export PATH

if type openssl 2>/dev/null >/dev/null
then
  :
else
  echo "ERROR: openssl binary is missing !"
  exit 1
fi

# md4 md5 sha sha1 sha224 sha256 sha384 sha512 whirlpool
# The oldest openssl we support is 0.9.8 and it supports sha512
HASH=sha512

# the file to sign
FILE="$1"
if [ ! -f "${FILE}" ]
then
  echo "ERROR: Cannot sign: The file ${FILE} doesn't exist"
  exit 2
fi

# the key to use for signature
PRIVKEY=/var/rudder/cfengine-community/ppkeys/localhost.priv

# cfengine  passphrase
PASSPHRASE="Cfengine passphrase"

# Create signature
SIGNATURE=`openssl dgst -passin "pass:${PASSPHRASE}" -${HASH} -hex -sign "${PRIVKEY}" < "${FILE}" | sed -e 's/.*= //'`

# Create a signature FILE
cat > "${FILE}.sign" <<EOF
header=rudder-signature-v1
algorithm=${HASH}
digest=${SIGNATURE}
EOF

