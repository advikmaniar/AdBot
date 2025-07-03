# LLM Models
LLM_MODEL_3_5 = "gpt-3.5-turbo"
LLM_MODEL_4_MINI = "gpt-4o-mini"

# Intents
INTENT_GREETING = "greeting"
INTENT_FINANCE = "finance"
INTENT_OTHER = "other"

# Finance - Subintents
SUBINTENT_INSIGHTS = "insights"
SUBINTENT_STATISTICS = "statistics"
SUBINTENT_VISUALIZATIONS = "visualizations"

# Paths
DATA_FOLDER = "data"
NO_DATA_FOUND = "No transactions available."

# General Prompts
SYSTEM_GENERAL_MODEL_PROMPT = (
    "You are FinBot, a smart and powerful financial assistant."
    "You always analyze the user's transaction data and respond with clear, data-backed, helpful, and real-world responses. "
    "Focus on quality, not quantity. Be concise and insightful. "
    "You can never make up data or provide inaccurate information."
    "Use emojis to keep the conversation engaging and fun, but only when appropriate. "
)

# Classifier Prompts
SYSTEM_INTENT_CLASSIFIER_PROMPT = (
    "You are an intent classifier. You only respond with one of the following: "
    "'greeting', 'finance', or 'other'."
)
SYSTEM_SUBINTENT_CLASSIFIER_PROMPT = (
    "You are a subintent classifier. Map the user’s question to one of: "
    "'insights' (recommendations, advice), "
    "'statistics' (facts, totals, breakdowns), "
    "or 'visualizations' (charts/graphs)."
    "Respond with exactly one word."
)

# Subintent Prompts
SYSTEM_SUBINTENT_INSIGHTS_PROMPT = (
    "Analyze the user's transaction data and generate personalized, actionable recommendations based on the user's question. "
    "From the user's transaction data, use amount, sum, count, averages and patterns to provide as many relevant numbers in the response as possible. "
    "Only provide specific insights, no general advice — no fluff, keep it concise, max 4–5 bullet points."
    
)

# Subintent Training Examples
FINANCE_SUBINTENT_EXAMPLES = {
    "insights": [
        "How can I save more money?",
        "Give me 3 ways to reduce my monthly expenses.",
        "Any tips for cutting down my food spending?",
        "How do I stop overspending?",
        "What changes can I make to grow my savings?",
    ],
    "statistics": [
        "How much did I spend this month?",
        "What’s my biggest expense?",
        "Break down my expenses by category.",
        "Show me my spending summary.",
        "How many transactions did I make last week?",
    ],
    "visualizations": [
        "Show my expenses in a pie chart.",
        "Give me a bar graph of my spending.",
        "Plot my monthly spending by category.",
        "Create a visual summary of my expenses.",
        "Can you visualize my transaction trends?",
    ]
}

# Slack Suggestion Texts
SUGGESTIONS = [
    "How much did I spend on food?",
    "Break down my expenses",
    "Any money-saving tips?"
]

