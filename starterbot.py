import os
import time
from slackclient import SlackClient
from HTMLParser import HTMLParser
import urllib
from cleverbot import Cleverbot
import re

<<<<<<< HEAD
os.environ["SLACK_BOT_TOKEN"] = "xoxb-106160578288-cxJBYlx4Xt9dYmg0vyBFHEiD"
=======
os.environ["SLACK_BOT_TOKEN"] = "xoxb-106160578288-dRlnKRijzFq5Ypnx6284kXPH"
>>>>>>> c39875517889a1460356f5e9f8853a67076477b3
os.environ["BOT_ID"] = "U344QH08G"

# starterbot's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")

# constants
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = "do"

cb = Cleverbot()

# instantiate Slack & Twilio clients
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

# class MyHTMLParser(HTMLParser):
#     trendingtopics = []
#     gettext = 0
#     def handle_starttag(self, tag, attrs):
#         if tag == 'span':
#             print("FOUND SPAN: ")
#             print(attrs)
#             for kv in attrs:
#                 if kv[0] == 'class' and kv[1] == 'hottrends-single-trend-title ellipsis-maker-inner':
#                     self.gettext = 1
#                     print("FOUND TAG")

#     def handle_endtag(self, tag):
#         if tag == 'span': 
#             self.gettext = 0

#     def handle_data(self, data):
        

# url = "https://www.google.com/trends/hottrends"
# parser = MyHTMLParser()
# f = urllib.urlopen(url)
# parser.feed(f.read())
# parser.close()
# print(parser.trendingtopics)


def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    if command == '':
        pass
    # response = "Not sure what you mean. Use the *" + EXAMPLE_COMMAND + \
    #            "* command with numbers, delimited by spaces."
    # if command.startswith(EXAMPLE_COMMAND):
    #     response = "Sure...write some more code then I can do that!"
    if 'pcbot' in command:
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