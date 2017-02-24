import os
import time
from slackclient import SlackClient
import dice

# starwarsbot's ID as an environment variable
BOT_ID = "U49GZTWPL" # os.environ.get("BOT_ID")

# constants
AT_BOT = "<@" + BOT_ID + ">"

# instantiate Slack & Twilio clients
slack_client = SlackClient("xoxb-145577948802-YyvbmKihDqcgkgcv7acMD1se") # os.environ.get('SLACK_BOT_TOKEN'))


def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    response = "Not sure what you mean. Try using 'roll', followed by a dice pool, or 'help' for more info."
    if command.startswith("help"):
        response = ("a = Ability die \n"
                    "b = Boost die \n"
                    "c = Challenge die \n"
                    "d = Difficulty die \n"
                    "p = Proficiency die \n"
                    "s = Setback die \n"
                    "f = Force die \n"
                    "D = Standard die")
    if command.startswith("roll"):
        response = dice.display_results(dice.roll_string(command[5:]))
    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)


def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
    return None, None


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("StarWarsBot connected and running!")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
