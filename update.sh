#Automatic updates for minimia

install_dir="/usr/bin/mia-tunnel"
log="${install_dir}/log"
date=$(date +%D)
time=$(date +%r)

if ! test -f $log; then
	touch $log
fi

echo "miniMIA Update Script" > $log
echo "${date} ${time}" >> $log
printf "\n\n" >> $log


if [ "$EUID" -ne 0 ]; then 
	echo "Script was not ran as root! Exiting..." >> $log
	exit
fi

echo "Checking for updates..." >> $log
#check for updates
update=$(git -C $install_dir fetch --dry-run)

if [ -z $update ]; then
	echo "No update found. Exiting..." >> $log
	#update is not required
	exit
fi

echo "Update found!" >> $log
echo "Stopping mia-tunnel service" >> $log
systemctl stop mia.service

git -C $install_dir pull >> $log

echo "Update Installed. Rebooting!" >> $log
reboot now
