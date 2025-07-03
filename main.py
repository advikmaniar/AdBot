from agent import process_user_task
from dotenv import load_dotenv
import os
from openai import OpenAI
import logging
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from server import user_dataframes
import pandas as pd
from classifier import classify_intent, is_obvious_greeting, is_obvious_all_set
from utils import clean_text

# Set up basic logging
logging.basicConfig(level=logging.INFO)

# Load environment variables
load_dotenv()

# Initialize the chat_history
chat_history = []

# Slack App Initialization
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.command("/connect-bank-account")
def handle_connect_command(ack, body, respond):
    ack()
    user_id = body["user_id"]
    link_url = f"http://localhost:5000/?user_id={user_id}" 

    respond({
        "response_type": "ephemeral",
        "text": "Click the button below to securely link your bank account.",
        "attachments": [
            {
                "text": "",
                "fallback": "Connect your account",
                "actions": [
                    {
                        "type": "button",
                        "text": "🔗 Connect My Bank Account",
                        "url": link_url
                    }
                ]
            }
        ]
    })

def process_message(event, client):
    """Process the message and respond accordingly."""
    try:
        user_id, channel_id = event.get('user'), event.get('channel')

        if 'channel_type' in event and event['channel_type'] == 'im' and 'bot_id' not in event:
            response = client.chat_postMessage(channel=channel_id, text="...")
            # Get the timestamp of the response so that we can update it with the real response from the AI later
            ts = response['ts']
            # Get the text of the user message from Slack DM
            agent_input = event.get('text', '')

            if is_obvious_greeting(agent_input):
                intent = "greeting"
            elif is_obvious_all_set(agent_input):
                client.chat_update(channel=channel_id, ts=ts, text="👍 Glad to hear that! If you need anything else, just let me know.")
                return
            else:
                intent = classify_intent(agent_input)
            logging.info(f"Classified intent: {intent} for user_id: {user_id}")

            if intent == "greeting":
                client.chat_postMessage(
                    channel=channel_id,
                    text="Hey there! 👋 Ready to analyze your spending?",
                    blocks=[
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": "Try asking me things like:"
                            }
                        },
                        {
                            "type": "actions",
                            "elements": [
                                {
                                    "type": "button",
                                    "text": {"type": "plain_text", "text": "💰 How much did I spend on food?"},
                                    "value": "How much did I spend on food?",
                                    "action_id": "suggestion_1"
                                },
                                {
                                    "type": "button",
                                    "text": {"type": "plain_text", "text": "📊 Break down my expenses"},
                                    "value": "Break down my expenses",
                                    "action_id": "suggestion_2"
                                },
                                {
                                    "type": "button",
                                    "text": {"type": "plain_text", "text": "🧠 Any money-saving tips?"},
                                    "value": "Any money-saving tips?",
                                    "action_id": "suggestion_3"
                                }
                            ]
                        }
                    ]
                )

                return
            elif intent == "finance":
                agent_response_text = process_user_task(str(agent_input), chat_history, user_id)
                # cleaned_text = clean_text(agent_response_text)
                client.chat_update(channel=channel_id, ts=ts, text=agent_response_text)
                return
            else:
                client.chat_update(channel=channel_id, ts=ts, text="🤖 I'm trained to help you analyze your transactions. Try asking me something like `Show my biggest expenses this month`.")
                return

    except Exception as e:
        logging.error("Error processing message: %s", str(e))

@app.event("message")
def message_handler(event, say, ack, client):
    """Handles incoming messages."""
    ack()
    logging.info("Message received: %s", event)

    # Process the message
    process_message(event, client)

@app.action("suggestion_1")
@app.action("suggestion_2")
@app.action("suggestion_3")
def handle_suggestion_clicks(ack, body, client):
    ack()
    user_id = body["user"]["id"]
    channel_id = body["channel"]["id"]
    text = body["actions"][0]["value"]

    # Post the clicked suggestion as if user typed it
    response = client.chat_postMessage(channel=channel_id, text=text)
    ts = response["ts"]

    agent_response = process_user_task(text, chat_history, user_id)
    client.chat_update(channel=channel_id, ts=ts, text=agent_response)


if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN"))
    handler.start()