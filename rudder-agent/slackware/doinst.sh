if [ -L /etc/rc.d/rc.rudder-agent ]; then
    # upgrade
    /opt/rudder/share/package-scripts/rudder-agent-postinst false slack false
else
    # new install
    ln -s /etc/init.d/rudder-agent /etc/rc.d/rc.rudder-agent
    /opt/rudder/share/package-scripts/rudder-agent-postinst true slack false
fi

