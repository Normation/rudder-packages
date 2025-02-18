if [ -L /etc/rc.d/rc.rudder-agent ]; then
  # upgrade
  /opt/rudder/share/package-scripts/rudder-agent-postinst false slack false
else
  # new install
  ln -s /etc/init.d/rudder-agent /etc/rc.d/rc.rudder-agent
  /opt/rudder/share/package-scripts/rudder-agent-postinst true slack false
fi

# Start agent when boot
if [ "$(grep -qE "^rudder agent start" /etc/rc.d/rc.local ; echo $?)" != "0" ]; then
  echo -e "\n# Start rudder agent\nrudder agent start\n" >> /etc/rc.d/rc.local
fi

# Stop agent when shutdown
if [ "$(grep -qE "^/etc/rc.d/rc.rudder-agent stop" /etc/rc.d/rc.local_shutdown 2>/dev/null ; echo $?)" != "0" ]; then
  echo -e "\n# Stop rudder agent\n/etc/rc.d/rc.rudder-agent stop\n" >> /etc/rc.d/rc.local_shutdown
fi

