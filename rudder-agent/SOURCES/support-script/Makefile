all: rudder-support-info

rudder-support-info: support-info lib/* tests/*
	perl -pe '$$_=qx/cat $$1/ if /^#\s*Include\s*:\s*(\S+)/' lib/* tests/* support-info > $@
	chmod +x $@

clean:
	rm -f rudder-support-info
