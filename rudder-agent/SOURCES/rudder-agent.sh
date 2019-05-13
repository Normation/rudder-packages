# Rudder profile entries, to add the agent to the
# PATH and its manpages to the MANPATH

# Build a MANPATH with our manpages in it

## If $MANPATH is already defined, use it, or build
## a new one from scratch if it does not
if type manpath >/dev/null 2>&1
then
    MANPATH=$(manpath 2> /dev/null):/opt/rudder/share/man
elif [ ! -z "${MANPATH}" ]
then
    MANPATH=${MANPATH}:/opt/rudder/share/man
else
    MANPATH=/opt/rudder/share/man
fi

export MANPATH
