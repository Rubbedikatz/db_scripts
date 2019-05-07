# Deutsche Bahn Delay Scanner

This project measures train delays at Germany's biggest train stations.

<b>How to get started</b>
1. clone this repo.
2. execute <i>setup.py</i>.
3. get a free Deutsche Bahn API key: https://developer.deutschebahn.com/store/site/pages/getting-started.jag
4. add your API Key to the line starting with <i>dbapi = ""</i> to the file <i>api_keys.txt</i>.
5. executing <i>update_trips.py</i> collects all delay data for train stations in Germany of category 1: https://de.wikipedia.org/wiki/Liste_der_deutschen_Bahnh%C3%B6fe_der_Kategorie_1
6. the notebook <i>exploration.ipynb</i> shows how the data is structured within the database.

<b>Optional</b><br>
You can collect weather data to find out how delays are related to the local weather.
Add an API key for https://openweathermap.org/ to <i>api_keys.txt</i> and every time you execute <i>update_trips.py</i> also execute <i>update_weather.py</i>.

If you want to run an analysis without collecting your own data, you can download a database with data from 2018 here: ftp://u95127680-public:datasets@home756490993.1and1-data.host
The data was collected in 30 minute intervals with cronjobs running on a raspberry pi: https://www.raspberrypi.org/documentation/linux/usage/cron.md
