from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
import os
import pandas as pd
from constants import SUBINTENT_STATISTICS, SUBINTENT_VISUALIZATIONS, SUBINTENT_INSIGHTS, NO_DATA_FOUND, SYSTEM_GENERAL_MODEL_PROMPT, SYSTEM_SUBINTENT_INSIGHTS_PROMPT

def get_prompt(user_id: str, subintent: str) -> str:
    df = load_user_dataframe(user_id)
    if df.empty:
        return NO_DATA_FOUND
    
    if subintent == SUBINTENT_STATISTICS:
        return statistics_prompt
    elif subintent == SUBINTENT_VISUALIZATIONS:
        return visual_prompt
    elif subintent == SUBINTENT_INSIGHTS:
        return insights_prompt
    else:
        return general_prompt
    

general_prompt = ChatPromptTemplate.from_messages([
    ("system", 
     SYSTEM_GENERAL_MODEL_PROMPT),
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

insights_prompt = ChatPromptTemplate.from_messages([
    ("system", 
     SYSTEM_GENERAL_MODEL_PROMPT + SYSTEM_SUBINTENT_INSIGHTS_PROMPT),
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

statistics_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You're a financial analyst..."),
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

visual_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "Describe the user's spending chart..."),
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

def load_user_dataframe(user_id):
    path = f"data/transactions_{user_id}.csv"
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        return pd.DataFrame()
    return pd.read_csv(path)