import logging
from dotenv import load_dotenv
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain.agents import AgentExecutor
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain_core.messages import AIMessage, HumanMessage

# Setup logging
logging.basicConfig(level=logging.INFO)

# Load the environment variables
load_dotenv()

# Define which LLM to use
llm = ChatOpenAI(model="gpt-4-1106-preview", temperature=0)

# Short term memory
chat_history = []
# Capabilities
tools = []

# Define the chat prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful personal AI assistant named TARS. You have a geeky, clever, sarcastic, and edgy sense of humor."),
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# Define the agent
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
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# user_task = "What would be the AI equivalent of Hello World?"
# output = agent_executor.invoke({"input": user_task, "chat_history": chat_history})
# print(output['output'])

def process_user_task(user_task, chat_history):
    """
    Process the user task using the agent and update the chat history.
    
    :param user_task: The task input by the user.
    :param chat_history: The current chat history.
    :return: The output from the agent.
    """
    try:
        result = agent_executor.invoke({"input": user_task, "chat_history": chat_history})
        chat_history.extend([
            HumanMessage(content=user_task),
            AIMessage(content=result["output"]),
        ])
        return result["output"]
    except Exception as e:
        logging.error(f"Error in process_user_task: {e}")
        return "An error occurred while processing the task."