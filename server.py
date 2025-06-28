from flask import Flask, request, jsonify, send_from_directory
from plaidClient import client
import os
from transactionFetcher import fetchTransactions 
from plaid2.model.link_token_create_request_user import LinkTokenCreateRequestUser


app = Flask(__name__)

@app.route("/")
def index():
    return send_from_directory('.', "index.html")

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
    response = client.item_public_token_exchange(public_token)
    access_token = response.access_token

    print("🔁 Running transaction fetch after token exchange...")
    fetchTransactions(access_token)  

    # Update the .env file with the new access token
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

    return jsonify({"access_token": response.access_token}) 

if __name__ == "__main__":
    app.run(debug=True)
