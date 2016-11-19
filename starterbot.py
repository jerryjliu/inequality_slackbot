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
import json
from sets import Set


minorityGroups = set(["chinese", "black", "blacks", "black people", "african", 
    "native americans", "native american", "ape", "americans", "american", "indians", "mexicans", 
    "koreans", "japanese", "japs", "jap", "korean", "viets", "vietnamese", "arab", "persians", "whites", "white", "persia", "middle east", "middle eastern", "china", "japan", "korea", "asia", "africa", "asians", "latinos", "muslims", "muslim", "jews", "jew", "faggot", "fag", "girls", "female", "girl", "woman", "women"])
os.environ["SLACK_BOT_TOKEN"] = "xoxb-106160578288-MCCDt4mOofB8a5PGTnwdeaA6"

os.environ["BOT_ID"] = "U344QH08G"

# starterbot's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")

# constants
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = "do"

cb = Cleverbot()

# instantiate Slack & Twilio clients
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

trendingtopics = ["standing rock", "bannon", "pence", "trump", "clinton", "trumpcup"]

path_to_chromedriver = '/Users/jerryliu/Downloads/chromedriver'
os.environ["webdriver.chrome.driver"] = path_to_chromedriver
driver = webdriver.Chrome(path_to_chromedriver)
url = "https://www.google.com/trends/hottrends"
driver.get(url)
spans = driver.find_elements_by_class_name('hottrends-single-trend-title')
for span in spans:
    trendingtopics.append(span.text.lower())
driver.quit()

#get list of users on slack
userurl = "https://slack.com/api/users.list"
userparams = {"token": os.environ["SLACK_BOT_TOKEN"]}
r = requests.get(userurl, params=userparams)
print(r.text)
userdict = json.loads(r.text)
useridmap = {}
for user in userdict["members"]:
    useridmap[user["id"]] = user["name"]

racistCounter = 0
racistThreshold = 3

postPublic = True

def handle_command(command, channel, user):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """

    global racistCounter
    global racistThreshold
    global postPublic
   #  # make a string with the request type in it:
   #  method = "POST"
   #  # create a handler. you can specify different handlers here (file uploads etc)
   #  # but we go for the default
   #  handler = urllib2.HTTPHandler()
   #  # create an openerdirector instance
   #  opener = urllib2.build_opener(handler)
   #  # build a request
   # # data = urllib.urlencode(dictionary_of_POST_fields_or_Nones
    response = ""
    publicResponse = ""
    emergencyResponse = ""
    if command == '':
        pass
    print(command)
    data = {
     "documents": [
         {
             "language": "en",
             "id": "1",
             "text": command
         }
     ]
    }
    headers = {"Content-Type":'application/json', "Ocp-Apim-Subscription-Key":'4c0a791d83ef4e5daf5bcbd5813be948', "Accept":'application/json'}
    sentiment = requests.post("https://westus.api.cognitive.microsoft.com/text/analytics/v2.0/sentiment", data=json.dumps(data), headers=headers)
    keyPhrases = requests.post("https://westus.api.cognitive.microsoft.com/text/analytics/v2.0/keyPhrases", data=json.dumps(data), headers=headers)

    print sentiment.text
    print keyPhrases.text
    print "-----"
    print json.loads(keyPhrases.text)["documents"][0]["keyPhrases"]

    phrasesSet = set(json.loads(keyPhrases.text)["documents"][0]["keyPhrases"])
    phrasesSet = phrasesSet | (set(command.split()))
    if json.loads(sentiment.text)["documents"][0]["score"] < 0.5:
        detected = False
        for phrase in phrasesSet:
            tokens = phrase.split()
            for token in tokens:
                if token in minorityGroups:
                    racistCounter += 1 - json.loads(sentiment.text)["documents"][0]["score"]
                    detected = True
                    break
        if detected:
            response = "Hey %s, we've detected that your comment may have been politically incorrect. Please remember to be polite and respectful towards all parties.\n" % useridmap[user]

   # print keyPhrases.text["documents"]["keyPhrases"]

    #if sentiment.

    #detect trending topics. 
    if response != "":
        for topic in trendingtopics:
            if topic in command:
                url = "http://www.bing.com/news/search?q=%s&qs=n&form=QBNT&sc=8-8&sp=-1&sk=&ghc=1" % urllib.quote_plus(topic)
                response = response + "You've stumbled upon a trending topic! Look here: %s\n" % url

    if (racistCounter >= racistThreshold):
        emergencyResponse = "Hey! We've noticed that there's been a trend of offensive messages on this channel. We encourage everybody to make an effort to have a more polite and friendly conversation.\n"
        racistCounter = 0

    # response = "Not sure what you mean. Use the *" + EXAMPLE_COMMAND + \
    #            "* command with numbers, delimited by spaces."
    # if command.startswith(EXAMPLE_COMMAND):
    #     response = "Sure...write some more code then I can do that!"
    publicResponse = ""
    if 'pcbot' in command and response == "":
        if 'public' in command:
            postPublic = True 
            publicResponse = "pcbot will post public messages for offensive content."
        elif 'private' in command:
            postPublic = False
            publicResponse = "pcbot will post private messages for offensive content."
        if publicResponse == "":
            publicResponse = cb.ask(re.sub('[^A-Za-z0-9]+', '', command))

    if not postPublic:
        slack_client.api_call("chat.postMessage", channel="@" + useridmap[user],
                              text=response, as_user=True)
    else:
        slack_client.api_call("chat.postMessage", channel=channel,
                              text=response, as_user=True)
    slack_client.api_call("chat.postMessage", channel=channel,
                          text=publicResponse, as_user=True)
    slack_client.api_call("chat.postMessage", channel=channel,
                          text=emergencyResponse, as_user=True)


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
                return output['text'], output['channel'], output['user']
    return None, None, None


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        while True:
            command, channel, user = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel, user)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")