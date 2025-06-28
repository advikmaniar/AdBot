from plaidClient import client
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
import requests

print("🔍 transaction_fetcher.py is running...")
load_dotenv()

def fetchTransactions(access_token):
    # Define the base URL and date range
    base_url = "https://sandbox.plaid.com"
    end_date = datetime.today().date()
    start_date = end_date - timedelta(days=30)

    payload = {
        "client_id": os.getenv("PLAID_CLIENT_ID"),
        "secret": os.getenv("PLAID_SECRET"),
        "access_token": access_token,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat()
    }

    # Call Plaid directly
    response = requests.post(f"{base_url}/transactions/get", json=payload)
    data = response.json()
    transactions = data.get("transactions", [])
    
    print(f"📊 Retrieved {len(transactions)} transactions:\n")

    for txn in transactions:
        category = txn.get("personal_finance_category", {}).get("primary", "Unknown")
        name = txn.get("name", "Unknown")[:30]
        amount = txn.get("amount", 0)
        date = txn.get("date", "N/A")
        print(f"{date} | {name:30} | ${amount:7.2f} | {category}")

    return transactions