# Add CFEngine binaries to the PATH
PATH=${PATH}:/var/rudder/cfengine-community/bin
export PATH

# Add CFEngine manpages to the MANPATH
if [ -z "${MANPATH}" ]
then
    MANPATH=/opt/rudder/share/man
else
    MANPATH=/opt/rudder/share/man:${MANPATH}
fi

export MANPATH
