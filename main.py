from agent import process_user_task
from dotenv import load_dotenv
import os
import logging
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from server import user_dataframes
import pandas as pd

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

@app.command("/connect-bank-account")
def handle_connect_command(ack, body, respond):
    ack()
    user_id = body["user_id"]
    link_url = f"http://localhost:5000/?user_id={user_id}"  # Replace with your actual domain or ngrok

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

        # Respond only to DMs and non-bot messages
        if 'channel_type' in event and event['channel_type'] == 'im' and 'bot_id' not in event:
            # Send an initial response to let the user know the AI is processing the request
            response = client.chat_postMessage(channel=channel_id, text="...")
            # Get the timestamp of the response so that we can update it with the real response from the AI later
            ts = response['ts']
            # Get the text of the user message from Slack DM
            agent_input = event.get('text', '')

            if "show my latest transaction" in agent_input.lower():
                df = user_dataframes.get(user_id)
                if df is None or df.empty:
                    csv_path = f"data/transactions_user-123.csv"
                    if os.path.exists(csv_path):
                        df = pd.read_csv(csv_path)
                    else:
                        client.chat_update(channel=channel_id, ts=ts, text="❌ No transactions found for your account.")
                        return
                if df is None or df.empty:
                    client.chat_update(channel=channel_id, ts=ts, text="❌ No transactions found for your account.")
                else:
                    latest = df.sort_values("date", ascending=False).iloc[0]
                    category = latest.get("personal_finance_category.primary", "N/A")
                    website = latest["website"] if "website" in latest and pd.notna(latest["website"]) else "N/A"
                    response = (
                        f"*📅 Date:* {latest['date']}\n"
                        f"*🏷️ Name:* {latest['name']}\n"
                        f"*💰 Amount:* ${latest['amount']:.2f}\n"
                        f"*📂 Category:* {category}\n"
                    )
                    client.chat_update(channel=channel_id, ts=ts, text=response)
                return

            # Process the user message using the agent
            agent_response_text = process_user_task(str(agent_input), chat_history)
            # Update the initial response with the real response from the AI
            client.chat_update(channel=channel_id, ts=ts, text=agent_response_text)

    except Exception as e:
        logging.error("Error processing message: %s", str(e))

@app.event("message")
def message_handler(event, say, ack, client):
    """Handles incoming messages."""
    ack()
    logging.info("Message received: %s", event)

    # Process the message
    process_message(event, client)

if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN"))
    handler.start()