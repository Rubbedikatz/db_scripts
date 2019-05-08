# Deutsche Bahn Delay Scanner

This project measures train delays at Germany's biggest train stations.

## Getting started
<b>Get your own data</b>
1. Clone this repo.
2. Install dependencies, preferrably in a virtual environment. 
```
pip install -r requirements.txt
```
3. Run <i>setup.py</i> to create the database and get static information on train stations.
```
python setup.py
```
4. Get a free [Deutsche Bahn API key](https://developer.deutschebahn.com/store/site/pages/getting-started.jag).
5. Add your API Key to <i>api_keys.txt</i> at the line starting with <i>dbapi = ""</i>.
6. Run <i>update_trips.py</i> to collect data for trips at [train stations of the first category](https://de.wikipedia.org/wiki/Liste_der_deutschen_Bahnh%C3%B6fe_der_Kategorie_1) in Germany at this moment.
```
python update_trips.py
```

<b>Test with sample data instead</b><br>
If you want to run an analysis without collecting your own data, you can download a [database with sample data](ftp://u95127680-public:datasets@home756490993.1and1-data.host).
The data was collected in 30 minute intervals with [cronjobs running on a raspberry pi](https://www.raspberrypi.org/documentation/linux/usage/cron.md).

<b>Explore</b><br>
The notebook <i>exploration.ipynb</i> shows how the data is structured within the database.

<b>Optional Weather Data</b><br>
You can collect weather data to find out how delays are related to the local weather.
Add an API key for [OpenWeather.com](https://openweathermap.org/) to <i>api_keys.txt</i> and every time you execute <i>update_trips.py</i> also run
```
python update_weather.py
```

## Author

**Hannes Knobloch** - [Rubbedikatz](https://github.com/Rubbedikatz)


