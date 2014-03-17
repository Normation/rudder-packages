#!/bin/bash
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

#Rudder Script init

#Check if script is executed by root
if [ ! $(whoami) = 'root' ];then echo "You must be root"; exit; fi

REGEXPCHK1='^[0-9]\{1,3\}.[0-9]\{1,3\}.[0-9]\{1,3\}.[0-9]\{1,3\}\/[0-9]\{1,2\}$'
REGEXPCHK2='^[0-9]\{1,3\}.[0-9]\{1,3\}.[0-9]\{1,3\}.[0-9]\{1,3\}$'

# VARS
TMP_DIR=`mktemp -dq`
TMP_LOG=`mktemp -t rudder.XXXXXXXXXX -q`
mv $TMP_LOG ${TMP_LOG}.log
TMP_LOG=${TMP_LOG}.log
BOOTSTRAP_PATH=$TMP_DIR/bootstrap.ldif
INITPOLICY_PATH=$TMP_DIR/init-policy-server.ldif
INITDEMO_PATH=$TMP_DIR/demo-data.ldif
RUDDER_CONF_FILE=/opt/rudder/etc/rudder-web.properties
RUDDER_CONTEXT=`grep contextPath --color /opt/rudder/jetty7/contexts/rudder.xml | sed "s@^\s*<Set name=\"contextPath\">\(.*\)</Set>@\1@"`
REGEXP='s/^\([0-9]\{1,3\}\)\(.[0-9]\{1,3\}\)\(.[0-9]\{1,3\}\)\(.[0-9]\{1,3\}.[0-9]\{1,2\}\)$/\1\\\2\\\3\\\4/g'
again="yes"
cpt=0
cpt2=0
# Check if promises already exist for CFEngine community
INITREP=/var/rudder/cfengine-community/inputs
INITPRO=`ls ${INITREP} 2>/dev/null | wc -l`

Pause()
{
    key=""
    echo -n Hit any key to continue....
    stty -icanon
    key=`dd count=1 2>/dev/null`
    stty icanon
}

ErrorCheck()
{
  if [ $? -ne 0 ]
  then
    echo "ERROR: Execution failed! Aborting."
    echo "An error occured. Please check $TMP_LOG for details."
	exit
  fi
}

LDAPInit()
{
  cp /opt/rudder/share/bootstrap.ldif $BOOTSTRAP_PATH
  cp /opt/rudder/share/init-policy-server.ldif $INITPOLICY_PATH
  cp /opt/rudder/share/demo-data.ldif $INITDEMO_PATH
  sed -i "s/^\([^#].*\)%%POLICY_SERVER_HOSTNAME%%/\1$ANSWER1/g" $INITPOLICY_PATH
  sed -i "s#^\([^#].*\)%%POLICY_SERVER_ALLOWED_NETWORKS%%#\1$NET#g" $INITPOLICY_PATH
  /opt/rudder/sbin/slapadd -l $BOOTSTRAP_PATH &> $TMP_LOG
  ErrorCheck
  /opt/rudder/sbin/slapadd -l $INITPOLICY_PATH &> $TMP_LOG
  ErrorCheck
}

#Check if arg are used
if [ $# -gt 0 ]
then
  if [ $# -lt 5 ]
  then
    echo "usage: rudder-init.sh hostname DemoData LDAPReset InitialPromisesReset AllowedNetwork1 [AllowedNetwork2]..."
    exit
  else
    ANSWER1=$1 #Hostname
    ALLOWEDNETWORK[0]=$5 #ServerAllowed
    ANSWER4=$2 #DemoSample
    LDAPRESET=$3 #LDAPRESET
    LDAPCHK=1
    ANSWER6=$4 #InitialPromises
  fi
else
	echo
	echo "Welcome to the Rudder initialization script"
	echo
	echo "This script will configure your Rudder root server."
	echo "It can be run as many times as you want."

	# Menu
	# 1st Step: Definition HOSTNAME
	echo
	echo -n "Please enter the fully qualified domain name that will be used to access the web interface of the Rudder server (i.e rudder.example.com): "
	read ANSWER1
	# 2nd Step: Definition SERVER_ALLOWED_NETWORK
	while [ z$again = "zyes" ]
	do
	  again=''
	  while ! echo "${ALLOWEDNETWORK[$cpt]}" | grep "$REGEXPCHK1"
	  do
		echo
		echo -n "Enter network allowed to access server (i.e 192.168.0.0/24): "
		read ALLOWEDNETWORK[$cpt]
	  done
	  echo "Network(s) added:"
	  for i in ${ALLOWEDNETWORK[*]}
	  do
		echo $i
	  done
	  while ! echo "$again" | grep "^\(yes\|no\)$";do echo -n "Add more networks? (yes/no) ";read again;done
	  ((cpt++))
	done
	# 4th Step: Demo Sample
	while ! echo "$ANSWER4" | grep "^\(yes\|no\)$"
	do
	  echo
	  echo -n "Do you want to add sample data (for demos)? (yes/no) "
	  read ANSWER4
	done
	# 5th Step: LDAP Check
	LDAPDATA_PATH=/var/rudder/ldap/openldap-data/
	if [ -e ${LDAPDATA_PATH}DB_CONFIG ]
	then
	  LDAPCHK=`/opt/rudder/sbin/slapcat  | grep "^dn: " | wc -l`
	  if [ $LDAPCHK -gt 0 ]
	  then
		while ! echo "$LDAPRESET" | grep "^\(yes\|no\)$"
		do
		  echo
		  echo -ne "An LDAP database has been detected.\nDo you want to reinitialize it? (yes/no) "
		  read LDAPRESET
		done
	  fi
	fi
	#6th Step: Initial Promises
	if [ ${INITPRO} -ne 0 ]
	then
	  while ! echo "$ANSWER6" | grep "^\(yes\|no\)$"
	  do
		echo
		echo -n "Do you want to reset initial promises ? (yes/no) "
		read ANSWER6
	  done
	else
	  ANSWER6="yes"
	fi
fi
# Review
echo
echo Hostname: "$ANSWER1"
echo Allowed networks: "${ALLOWEDNETWORK[*]}"
echo Add sample data? "$ANSWER4"
if [ $LDAPCHK -gt 0 ]
then
  echo Reinitialize LDAP database? "$LDAPRESET"
fi
if [ ${INITPRO} -ne 0 ];then
	echo Reset Initial Promises? "$ANSWER6"
fi
echo
Pause
# Set Configuration
# Formatting allowed network
# NET will modify init-policy-server.ldif and NET 2 cf-served.cf
for i in ${ALLOWEDNETWORK[*]}
do
  if [ $cpt2 -eq 0 ]
  then
    NET=`echo $i | sed $REGEXP`
    NET2="'$NET'"
  else
    NET="$NET\ndirectiveVariable: ALLOWEDNETWORK[$cpt2]: `echo $i | sed $REGEXP`"
    NET2="$NET2, '`echo $i | sed $REGEXP`'"
  fi
  ((cpt2++))
done

# Configure initial promises
if [ z$ANSWER6 = "zyes" ]
then
  echo -n "Configuring and installing initial CFEngine promises..."
  cp -r /opt/rudder/share/initial-promises/ $TMP_DIR/community
  find $TMP_DIR/community -name "cf-served.cf" -type f -exec sed -i "s@'%%POLICY_SERVER_ALLOWED_NETWORKS%%'@$NET2@g" {} \;
  find $TMP_DIR/community -type f -exec sed -i "s/%%POLICY_SERVER_HOSTNAME%%/$ANSWER1/g" {} \;
  find $TMP_DIR/community -type f -exec sed -i "s#%%POLICY_SERVER_ALLOWED_NETWORKS%%#$NET#g" {} \;
  rm -rf /var/rudder/cfengine-community/inputs/*
  rm -rf /var/cfengine/inputs/*
  cp -r $TMP_DIR/community/* /var/rudder/cfengine-community/inputs/
  cp -r $TMP_DIR/community/* /var/cfengine/inputs/
  echo "127.0.0.1" > /var/cfengine/policy_server.dat
  echo "127.0.0.1"> /var/rudder/cfengine-community/policy_server.dat
  echo " done."
fi
# LDAP (re)initialization
/etc/init.d/slapd stop &> $TMP_LOG
if [ $LDAPCHK -gt 0 ]
then
  if [ z$LDAPRESET = "zyes" ]
  then
    echo -n "Initializing LDAP database..."
    rm -f /var/rudder/ldap/openldap-data/{alock,__db.*,*.bdb,log.*}
    LDAPInit
  fi
else
  echo -n "Initializing LDAP database..."
  LDAPInit
fi
# Check if Demo sample have to be added
if [ z$ANSWER4 = "zyes" ]
then
    /opt/rudder/sbin/slapadd -l $INITDEMO_PATH &> $TMP_LOG
fi
echo " done."

# Update the password file used by Rudder with random password

sed -i s/RUDDER_WEBDAV_PASSWORD.*/RUDDER_WEBDAV_PASSWORD:$(dd if=/dev/urandom count=128 bs=1 2>&1 | md5sum | cut -b-12)/ /opt/rudder/etc/rudder-passwords.conf
sed -i s/RUDDER_PSQL_PASSWORD.*/RUDDER_PSQL_PASSWORD:$(dd if=/dev/urandom count=128 bs=1 2>&1 | md5sum | cut -b-12)/ /opt/rudder/etc/rudder-passwords.conf
sed -i s/RUDDER_OPENLDAP_BIND_PASSWORD.*/RUDDER_OPENLDAP_BIND_PASSWORD:$(dd if=/dev/urandom count=128 bs=1 2>&1 | md5sum | cut -b-12)/ /opt/rudder/etc/rudder-passwords.conf

echo "The Rudder password file has been updated with random passwords."

# Delete temp files
echo -n "Cleaning up..."
rm -rf $TMP_DIR
echo " done."

# Restart services
echo -n "Restarting services..."

# Launch manually a single cf-agent instance to set passwords everywhere
/opt/rudder/bin/cf-agent &> $TMP_LOG

# Start the whole infrastructure
/etc/init.d/rudder-agent restart >> $TMP_LOG 2&>1
if [ -e $LDAPDATA_PATH ]; then /etc/init.d/slapd start >> $TMP_LOG 2&>1; fi
/etc/init.d/jetty restart >> $TMP_LOG 2&>1 || echo "WARNING: Jetty failed to start, maybe there is not enough RAM or swap on the machine. Skipping..."
echo " done."

echo
echo "Everything has been set up correctly."
echo "Rudder is ready to go on http://${ANSWER1}${RUDDER_CONTEXT}"
