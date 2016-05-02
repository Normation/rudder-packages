# This is a fake makefile that acts as the original one.
# It retreive everything from rudder-agent here, patch it and run it

# indirection in case we call those one
all: Makefile
localdepends: Makefile
depends: Makefile
localclean: Makefile
clean: Makefile
veryclean: Makefile

# when a Makefile regenerates itself, make reexecute itself on the new makefile
Makefile: always
	rsync -a ../../rudder-agent/ ../
	# Convert rudder-agent to rudder-agent-thin where needed
	patch -d ../debian --forward -p1 < patches/rudder-agent-thin/0001-rudder-agent-to-rudder-agent-thin-debian.patch
	test `find . -name \*.rej | wc -l` = 0
	sed -i 's/^REAL_NAME=rudder-agent/REAL_NAME=rudder-agent-thin/' ../debian/rules
	sed -i 's/^%define real_name  *rudder-agent$$/%define real_name rudder-agent-thin/' ../SPECS/rudder-agent.spec


# Fake dependency to force Makefile regeneration
always:

