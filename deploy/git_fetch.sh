cd /mars/git
rm -rf MARS_Sensor
git clone https://github.com/macroEagle/MARS_Sensor.git
if diff -aqr -x=.git /mars/git /mars/git_bak
then
	echo "Match!"
else
	echo "No match..dd!"
	cp /mars/git/MARS_Sensor/deploy/*.sh /mars/deploy
	cd /mars/deploy
    chmod +x *.sh
	cd /mars/git_bak
	rm -rf MARS_Sensor
	rsync -ax --exclude [.git] /mars/git/. /mars/git_bak/.
fi
