import logging
import os
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import datetime as dt
import requests
import random
from time import sleep


logging.basicConfig(level=logging.INFO)
load_dotenv()

#This grabs the token from a local .env file so they aren't visible to the github repo
SLACK_BOT_TOKEN = os.environ["OAUTH_TOKEN"]
OAUTH_BOT_TOKEN = os.environ["SLACK_TOKEN"]
API_KEY = os.environ["WEATHAPI_KEY"]
BASE_URL = "http://api.openweathermap.org/data/2.5/weather?"
#Initializes the bot application
app = App(token=SLACK_BOT_TOKEN)

#Grabs the weather data of the city you would like to know about
def getCityWeatherData(city):
    try:
        url = BASE_URL + "appid=" + API_KEY + "&q=" + city
        response = requests.get(url).json()
        tempK = response['main']['temp']
        tempC, tempF = kelvin_to_celsius_fahrenheit(tempK)
        humidity = response['main']['humidity']
        description = response['weather'][0]['description']
        sunriseTime = dt.datetime.utcfromtimestamp(response['sys']['sunrise'] + response['timezone'])
        sunsetTime = dt.datetime.utcfromtimestamp(response['sys']['sunset'] + response['timezone'])
        weatherAtLoc = f"Temperature in {city}: {tempC:.2f} degrees Celcius or {tempF:.2f} degrees Fahrenheit\nHumidity in {city}: {humidity}% \nGeneral Weather in {city}: {description}\nSunrise at {sunriseTime} in your timezone\nSunset at {sunsetTime} in your timezone"
    except:
        weatherAtLoc = "Something went wrong. Try another city like Texas."
    return weatherAtLoc

#Functionthat changes kelvin to celsius and fahrenheit
def kelvin_to_celsius_fahrenheit(kelvin):
    celsius = kelvin - 273.15
    fahrenheit = celsius * (9/5) + 32
    return celsius, fahrenheit



@app.event("app_mention")
def mention_handler(body, context, payload, options, say, event):
    textContent = payload['text'][15:]
    
    try:
        botAction = textContent[:7]
        print(botAction)
        if botAction == "weather":
            try:
                cityToCheck = textContent[7:]
                print(cityToCheck)
                cityWeather = getCityWeatherData(cityToCheck)
                say(cityWeather)
            except:
                say("Please add a city")
        elif botAction[:4] == "help":
            say("Welcome to TimerReminder!\nFunctions you may use include:\n     remindS <amount of time till timer messages up to 999 seconds>\n     remindM <amount of time till timer messages up to 999 minutes\n     weather <city you want a weather report on>")
        elif botAction[:7] == "remindS":
            try:
                timetowait = int(textContent[7:11])
                tC = textContent[11:]
                print(timetowait)
                say("Waiting for " + str(timetowait) + " seconds to remind to: " + tC)
                sleep(timetowait)
                say("<@" + payload['user'] +">" + " It has been " + str(timetowait) + " seconds. Remember to: " + tC)
            except:
                say("Please enter a valid integer number 10 - 999 seconds")
        elif botAction[:7] == "remindM":
            try:
                timetowait = int(textContent[7:11]) * 60
                tC = textContent[11:]
                print(timetowait)
                say("Waiting for " + str(timetowait/60) + " minutes to remind to: " + tC)
                sleep(timetowait)
                say("<@" + payload['user'] +">" + " It has been " + str(timetowait/60) + " minutes. Remember to: " + tC)
            except:
                say("Please enter a valid integer number 10 - 999 minutes")
            
        else:
            say("No valid command given")
    except:
        say("Please mention more in your command")


    


@app.event("message")
def message_handler(body, context, payload, options, say, event):
    pass

if __name__ == "__main__":
    handler = SocketModeHandler(app, OAUTH_BOT_TOKEN)
    handler.start()
