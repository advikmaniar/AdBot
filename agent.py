from dotenv import load_dotenv
from langchain_community.chat_models import ChatOpenAI

# Load the environment variables
load_dotenv()

# Define which LLM to use
llm = ChatOpenAI(model="gpt-4-1106-preview", temperature=0)

output = llm.invoke("What would be the AI equivalent of Hello World?")
print(output)