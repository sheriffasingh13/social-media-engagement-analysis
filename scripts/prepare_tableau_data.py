"""
Makes the file my Tableau dashboard reads.
It starts from the cleaned data and adds a few label columns so the charts
are easier to read.

Run from the main project folder:
    python3 scripts/prepare_tableau_data.py
"""

import pandas as pd

df = pd.read_csv("data/cleaned/facebook_metrics_cleaned.csv")

# Engagement rate as a fraction (0.0245 = 2.45%) so Tableau can show it as a percent
df["engagement"] = df["engagement_rate"] / 100

# Photo vs. non-photo (status, link, and video posts together)
df["format_group"] = df["format"].where(df["format"] == "Photo", "Non-photo")

# Format names with the number of posts, so small groups are easy to spot
counts = df["format"].value_counts()
df["format_label"] = df["format"].map(lambda f: f"{f} ({counts[f]} posts)")

# Order for the time blocks (otherwise Tableau sorts them alphabetically)
order = {"Overnight (12-5 AM)": 1, "Morning (6-11 AM)": 2,
         "Afternoon (12-5 PM)": 3, "Evening (6-11 PM)": 4}
df["time_block_order"] = df["time_block"].map(order)

# Month names
df["month_name"] = pd.to_datetime(df["month"], format="%m").dt.strftime("%b")

df["flagged"] = df["flag_any"].map({True: "Yes", False: "No"})
df["paid"] = df["paid"].fillna("Unknown")

cols = ["format", "format_label", "format_group", "category", "time_block",
        "time_block_order", "month", "month_name", "page_size_quartile",
        "paid", "reach", "likes", "comments", "shares", "engagement", "flagged"]
df[cols].to_csv("data/cleaned/facebook_posts_tableau.csv", index=False)
print("Saved data/cleaned/facebook_posts_tableau.csv", df[cols].shape)
