import os
import time
from slackclient import SlackClient
from HTMLParser import HTMLParser
from selenium import webdriver
from bs4 import BeautifulSoup
import requests
import urllib
import urllib2
from cleverbot import Cleverbot
import re


os.environ["SLACK_BOT_TOKEN"] = "xoxb-106160578288-sOXQicblQ2vDSqkqlAr7DaFT"

os.environ["BOT_ID"] = "U344QH08G"

# starterbot's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")

# constants
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = "do"

cb = Cleverbot()

# instantiate Slack & Twilio clients
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

trendingtopics = []

path_to_chromedriver = '/Users/jerryliu/Downloads/chromedriver'
os.environ["webdriver.chrome.driver"] = path_to_chromedriver
driver = webdriver.Chrome(path_to_chromedriver)
url = "https://www.google.com/trends/hottrends"
driver.get(url)
spans = driver.find_elements_by_class_name('hottrends-single-trend-title')
for span in spans:
    trendingtopics.append(span.text.lower())
driver.quit()


def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """

    # make a string with the request type in it:
    method = "POST"
    # create a handler. you can specify different handlers here (file uploads etc)
    # but we go for the default
    handler = urllib2.HTTPHandler()
    # create an openerdirector instance
    opener = urllib2.build_opener(handler)
    # build a request
   # data = urllib.urlencode(dictionary_of_POST_fields_or_None)
    data =  {
     "documents": [
         {
             "language": "en",
             "id": "1",
             "text": "First document"
         },
         {
             "language": "en",
             "id": "100",
             "text": "Final document"
         }
     ]
    }
    data = urllib.urlencode(data)

    request = urllib2.Request(url, data=data)
    # add any other information you want
    request.add_header("Content-Type",'application/json')
    request.add_header("Ocp-Apim-Subscription-Key",'4c0a791d83ef4e5daf5bcbd5813be948')
    request.add_header("Accept",'application/json')

    # overload the get method function with a small anonymous function...
  
    request.get_method = lambda: method
    # try it; don't forget to catch the result
   # try:
   #     connection = opener.open(request)
   # except urllib2.HTTPError,e:
   #     connection = e

    response = urllib2.urlopen(request)
    print response.read()

    response = ""
    if command == '':
        pass
    for topic in trendingtopics:
        if topic in command:
            url = "http://www.bing.com/news/search?q=%s&qs=n&form=QBNT&pq=hamilton&sc=8-8&sp=-1&sk=&ghc=1" % topic
            response = "You've stumbled upon a trending topic! Look here: %s" % url

    # response = "Not sure what you mean. Use the *" + EXAMPLE_COMMAND + \
    #            "* command with numbers, delimited by spaces."
    # if command.startswith(EXAMPLE_COMMAND):
    #     response = "Sure...write some more code then I can do that!"
    if 'pcbot' in command and response == "":
        response = cb.ask(re.sub('[^A-Za-z0-9]+', '', command))
    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)


def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    print(slack_rtm_output)
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and 'user' in output and output['user'] != BOT_ID:
                # return text after the @ mention, whitespace removed
                return output['text'], output['channel']
    return None, None


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")