import os
import pandas as pd
import logging
from constants import SUBINTENT_STATISTICS, SUBINTENT_VISUALIZATIONS, SUBINTENT_INSIGHTS, NO_DATA_FOUND

def get_context(user_id: str, subintent: str) -> str:
    df = load_user_dataframe(user_id)
    if df.empty:
        return NO_DATA_FOUND

    if subintent == SUBINTENT_STATISTICS:
        return build_statistics_context(df)
    elif subintent == SUBINTENT_VISUALIZATIONS:
        return build_visualization_context(df)
    elif subintent == SUBINTENT_INSIGHTS:
        return build_insights_context(df)
    else:
        return build_general_context(df)

def load_user_dataframe(user_id):
    path = f"data/transactions_{user_id}.csv"
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        return pd.DataFrame()
    return pd.read_csv(path)

def build_statistics_context(df):
    try:
        total = df["amount"].sum()
        max_txn = df.loc[df["amount"].idxmax()]
        top_category = df["personal_finance_category.primary"].value_counts().idxmax()

        return (
            f"📊 Statistics Summary:\n"
            f"- Total spent: ${total:.2f}\n"
            f"- Largest transaction: {max_txn['name']} for ${max_txn['amount']:.2f}\n"
            f"- Most frequent category: {top_category}"
        )
    except Exception as e:
        logging.error(f"Statistics context error: {e}")
        return "Couldn't compute statistics context."

def build_visualization_context(df):
    top = df["personal_finance_category.primary"].value_counts().head(3).to_dict()
    context = "Top 3 categories by frequency:\n"
    for cat, count in top.items():
        context += f"- {cat}: {count} transactions\n"
    return context

def build_insights_context(df: pd.DataFrame) -> str:
    summary = []

    # Total and average spend
    total_spent = df['amount'].sum()
    avg_txn = df['amount'].mean()
    summary.append(f"Total spent in this period: ${total_spent:.2f}")
    summary.append(f"Average transaction: ${avg_txn:.2f}")

    # Most frequent merchant
    if not df['name'].empty:
        top_merchant = df["name"].value_counts().idxmax()
        count_merchant = df["name"].value_counts().max()
        summary.append(f"Most frequent merchant: {top_merchant} ({count_merchant} times)")

    # Top 3 categories by spend
    cat_spend = df.groupby("personal_finance_category.primary")["amount"].sum().sort_values(ascending=False).head(3)
    if not cat_spend.empty:
        summary.append("Top spending categories:")
        for cat, amount in cat_spend.items():
            summary.append(f"  - {cat}: ${amount:.2f}")

    # Refunds or income
    refunds = df[df['amount'] < 0]
    if not refunds.empty:
        total_refunds = refunds['amount'].sum()
        summary.append(f"Refunds/Income recorded: ${total_refunds:.2f}")

    # Optional: detect unusually high single transactions
    big_txns = df[df['amount'] > avg_txn * 2]
    if not big_txns.empty:
        max_txn = big_txns.sort_values("amount", ascending=False).iloc[0]
        summary.append(f"Largest transaction: {max_txn['name']} for ${max_txn['amount']:.2f} on {max_txn['date']}")

    return "\n".join(summary)

def build_general_context(df):
    return "User has shared transaction data. Awaiting specific instruction."
