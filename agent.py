import logging
from dotenv import load_dotenv
import pandas as pd
import os
from langchain_community.chat_models import ChatOpenAI
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain.agents import AgentExecutor
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain_core.messages import AIMessage, HumanMessage
from classifier import classify_finance_subintent
from prompts import get_prompt
from contextBuilder import get_context
from constants import LLM_MODEL_4_MINI, NO_DATA_FOUND


# Setup logging
logging.basicConfig(level=logging.INFO)

# Load the environment variables
load_dotenv()

# Define which LLM to use
llm = ChatOpenAI(model=LLM_MODEL_4_MINI, temperature=0)

# Short term memory
chat_history = []
# Capabilities
tools = []

def process_user_task(user_task, chat_history, user_id):
    path = f"data/transactions_{user_id}.csv"
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        return NO_DATA_FOUND
    
    df = pd.read_csv(path)
    df = df[["date", "amount", "name", "personal_finance_category.primary"]].dropna()

    # Extract subintent, context, prompt
    subintent = classify_finance_subintent(user_task)
    logging.info(f"Classified subintent: {subintent} for user_id: {user_id}")
    context = get_context(user_id, subintent)
    prompt = get_prompt(user_id, subintent)
    
    full_input = f"{context}\n\nUser question: {user_task}"
    agent = (
        {
            "input": lambda x: x["input"],
            "agent_scratchpad": lambda x: format_to_openai_function_messages(x["intermediate_steps"]),
            "chat_history": lambda x: x["chat_history"],
        }
        | prompt
        | llm
        | OpenAIFunctionsAgentOutputParser()
    )
    executor = AgentExecutor(agent=agent, tools=[], verbose=True)
    result = executor.invoke({"input": full_input, "chat_history": chat_history})
    chat_history.extend([HumanMessage(content=user_task), AIMessage(content=result["output"])])
    
    return result["output"]

    

