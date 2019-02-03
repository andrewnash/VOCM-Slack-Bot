import time
import re
from slackclient import SlackClient
from vocm_bot_tools import x_days_ago_qotd, date_qotd, format_qotd


slack_client = SlackClient('xoxb-531175547972-540583112211-NEnUDBiYdchY3eK2k6OUowVi')

# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None

# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
EXAMPLE_COMMAND = "What's todays the question of the day?"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

def parse_bot_commands(slack_events):
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == starterbot_id:
                return message, event["channel"]
    return None, None

def parse_direct_mention(message_text):
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def handle_command(command, channel):
    # Default response is help text for the user
    default_response = "Not sure what you mean. Try *{}*.".format(EXAMPLE_COMMAND)

    # Finds and executes the given command, filling in response
    response = None
    
    # This is where you start to implement more commands!
    if "today" in command.lower():
        response = format_qotd(x_days_ago_qotd(0))
    
    if "yesterday" in command.lower():
        response = format_qotd(x_days_ago_qotd(1))
    
    # TODO: add handling for more date formats
    if "What was the question of the day on " in command:
        response = format_qotd(date_qotd(command.split("What was the question of the day on ")[1]))

    # Sends the response back to the channel
    slack_client.api_call("chat.postMessage",
                          channel=channel,
                          text=response or default_response )

if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Starter Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(command, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")