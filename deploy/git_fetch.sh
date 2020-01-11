cd /mars/git
rm -rf MARS_Sensor
git clone https://github.com/macroEagle/MARS_Sensor.git
if diff -aqr /mars/git /mars/git_bak
then
	echo "Match!"
else
	echo "No match!"
	cd /mars/git_bak
	rm -rf *.*
	cp -r /mars/git/. /mars/git_bak/.
fi
