from flask import Flask, request, jsonify, send_from_directory, make_response
from plaidClient import client
from transactionFetcher import fetchTransactions 
from plaid2.model.link_token_create_request_user import LinkTokenCreateRequestUser
from dotenv import load_dotenv
import os
import pandas as pd
import time
import requests

load_dotenv()

app = Flask(__name__)
user_dataframes = {}  

@app.route("/")
def index():
    return send_from_directory('static', "link.html")

@app.route("/slack/commands", methods=["POST"])
def slack_command():
    data = request.form
    user_id = data.get("user_id")
    trigger_id = data.get("trigger_id")

    # Generate the URL to Plaid Link
    link_url = f"http://localhost:5000/?user_id={user_id}" 

    slack_response = {
        "response_type": "ephemeral",
        "text": "Click below to connect your bank account securely with Plaid.",
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
    }
    return jsonify(slack_response)

@app.route("/create_link_token", methods=["GET"])
def create_link_token():
    response = client.link_token_create(
        user=LinkTokenCreateRequestUser(client_user_id="user-123"),
        client_name="Advik Finance Bot",
        products=["transactions"],
        country_codes=["US"],
        language="en"
    )
    return jsonify(response.dict())

@app.route("/exchange_public_token", methods=["POST"])
def exchange_token():
    public_token = request.json["public_token"]
    user_id = request.json.get("user_id", "user-123")
    
    # Exchange token
    response = client.item_public_token_exchange(public_token)
    access_token = response.access_token

    fire_sandbox_transactions_webhook(access_token)
    time.sleep(3) # Webhook processing

    print("🔁 Running transaction fetch after token exchange..., make_response")

    # Fetch transactions into a dataframe
    df = fetchTransactions(access_token, user_id)

    user_dataframes[user_id] = df
    print(df.head())

    # Save to CSV 
    os.makedirs("data", exist_ok=True)
    filename = f"data/transactions_{user_id}.csv"
    df.to_csv(filename, index=False)
    print(f"📁 Transactions saved to {filename}")

    update_env_access_token(access_token)

    return jsonify({"access_token": access_token})

# Only for sandbox environment
def fire_sandbox_transactions_webhook(access_token):
    webhook_payload = {
        "client_id": os.getenv("PLAID_CLIENT_ID"),
        "secret": os.getenv("PLAID_SECRET"),
        "access_token": access_token,
        "webhook_type": "TRANSACTIONS",
        "webhook_code": "DEFAULT_UPDATE"
    }
    response = requests.post("https://sandbox.plaid.com/sandbox/transactions/fire_webhook", json=webhook_payload)
    print("📨 Webhook fired:", response.status_code, response.text)


def update_env_access_token(access_token):
    lines = []
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            lines = f.readlines()

    with open(".env", "w") as f:
        updated = False
        for line in lines:
            if line.startswith("PLAID_ACCESS_TOKEN="):
                f.write(f"PLAID_ACCESS_TOKEN={access_token}\n")
                updated = True
            else:
                f.write(line)
        if not updated:
            f.write(f"PLAID_ACCESS_TOKEN={access_token}\n")

if __name__ == "__main__":
    app.run(debug=True)
