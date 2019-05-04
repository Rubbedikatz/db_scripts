# Deutsche Bahn Delay Scanner

This project measures train delays at Germany's biggest train stations.

<b>How to get started</b>
1. clone this repo.
2. execute <i>setup.py</i>.
3. get a free Deutsche Bahn API key: https://developer.deutschebahn.com/store/site/pages/getting-started.jag
4. add your API Key to the file called <i>API_key.txt</i>.
5. executing <i>scan.py</i> collects all delay data for stations in <i>stations.txt</i> at this moment.
6. the notebook <i>exploration.ipynb</i> shows how the data is structured within the database.

<b>Optional</b><br>
You can collect weather data to find out how delays are related to the local weather.
Add an API key for www.... to <i>API_key.txt</i> and every time you execute <i>scans.py</i> also execute <i>weather.py</i>.

If you want to run an analysis without collecting your own data, you can download a database with data from [] to [] here: LINK
The data was collected in 30 minute intervals with cronjobs running on a raspberry pi: https://www.raspberrypi.org/documentation/linux/usage/cron.md
