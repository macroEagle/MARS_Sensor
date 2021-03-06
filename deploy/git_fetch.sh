cd /mars/git/MARS_Sensor
git fetch

CHANGED=$(git diff master origin/master)
if [ ! -n "$CHANGED" ]; then
#if git diff-index --quiet HEAD --; then
	echo "Match."
else
	echo "No Match."
	git pull
	#Update deploy.sh into deploy folder
	cp /mars/git/MARS_Sensor/deploy/*.sh /mars/deploy
	cd /mars/deploy
    chmod +x *.sh	
	#Update script and restart the service
	cd /mars/scripts
	rm *.*
	cp /mars/git/MARS_Sensor/scripts/*.* /mars/scripts
	sudo systemctl restart mars-sensor@pi
fi
