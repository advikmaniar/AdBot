import pandas as pd
import matplotlib.pyplot as plt
import uuid
import logging
import os

def summarize_data_for_prompt(df):
    if df.empty:
        return "No transactions available."

    summary = []
    # Most frequent merchant
    top_merchant = df["name"].value_counts().idxmax()
    summary.append(f"Most frequent merchant: {top_merchant}")

    # Top categories
    if "personal_finance_category.primary" in df.columns:
        top_category = df["personal_finance_category.primary"].value_counts().head(3)
        summary.append("Top spending categories:")
        for cat, count in top_category.items():
            summary.append(f"  - {cat}: {count} transactions")

    # Recent big expenses
    big_txns = df[df["amount"] > 100].sort_values("amount", ascending=False).head(3)
    if not big_txns.empty:
        summary.append("Top 3 biggest recent expenses:")
        for _, row in big_txns.iterrows():
            summary.append(f"  - {row['name']} (${row['amount']:.2f}) on {row['date']}")

    # Transport habit check
    if df["name"].str.contains("Uber", case=False).sum() > 3:
        summary.append("You've taken Uber quite often this month. Consider using public transport or walking when possible.")
        
    return "\n".join(summary)

def generate_statistics_response(df):
    try:
        total = df["amount"].sum()
        biggest = df.loc[df["amount"].idxmax()]
        top_category = df["personal_finance_category.primary"].value_counts().idxmax()
        top_spent = df.groupby("personal_finance_category.primary")["amount"].sum().idxmax()

        return (
            f"📊 *Statistics Summary:*\n"
            f"- Total Spent: ${total:.2f}\n"
            f"- Largest Transaction: {biggest['name']} (${biggest['amount']})\n"
            f"- Most Frequent Category: {top_category}\n"
            f"- Most Expensive Category: {top_spent}"
        )
    except Exception as e:
        logging.error(f"Statistics generation failed: {e}")
        return "❌ Couldn't compute statistics due to data issue."


def generate_visualization_response(df, user_id):
    try:
        import matplotlib.pyplot as plt
        import uuid

        plt.clf()
        df_plot = df.groupby("personal_finance_category.primary")["amount"].sum().sort_values()
        df_plot.plot(kind='barh', figsize=(8, 4))
        plt.title("Spending by Category")
        plt.xlabel("Amount Spent")

        filename = f"data/plot_{user_id}_{uuid.uuid4().hex}.png"
        plt.tight_layout()
        plt.savefig(filename)

        return f"🖼️ Here's your spending visualization:\n(file://{filename})\n\n_Note: You’ll need to render the image if using Slack SDK._"

    except Exception as e:
        logging.error(f"Visualization generation failed: {e}")
        return "❌ Couldn't generate visualization."
