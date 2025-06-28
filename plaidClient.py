from plaid2 import PlaidClient
import os
from dotenv import load_dotenv

load_dotenv()

client = PlaidClient.from_env()