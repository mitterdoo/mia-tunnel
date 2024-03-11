#Automatic updates for minimia

#check for updates
update=$(git fetch --dry-run)

if [ -z $update ]; then
	#update is not required
	exit
fi

systemctl stop mia.service

git pull

reboot now
