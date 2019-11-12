all: rudder-debug-info

rudder-debug-info: debug-info lib/* tests/*
	perl -pe '$$_=qx/cat $$1/ if /^#\s*Include\s*:\s*(\S+)/' debug-info > $@
	chmod +x $@

clean:
	rm -f rudder-debug-info
