#Automatic updates for minimia

if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

#check for updates
update=$(git fetch --dry-run)

if [ -z $update ]; then
	echo "No update found. Exiting..."
	#update is not required
	exit
fi

echo "Update found!"
echo "Stopping mia-tunnel service"
systemctl stop mia.service

git pull

echo "Rebooting!"
reboot now
