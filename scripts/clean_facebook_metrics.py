"""
Capstone - Data Cleaning and Exploration
Sheriffa Singh

Question: How are post format and posting hour associated with
reach-based engagement rate?

Input:  data/raw/dataset_Facebook.csv  (raw, from UCI)
Output: data/cleaned/facebook_metrics_cleaned.csv
        outputs/exploration_results.json  (the summary tables used in the write-up)

Run from the main project folder:
    python3 scripts/clean_facebook_metrics.py
"""

import json
import pandas as pd

RAW = "data/raw/dataset_Facebook.csv"
CLEAN = "data/cleaned/facebook_metrics_cleaned.csv"

# ---------------------------------------------------------------
# Step 1. Load the file. It uses semicolons, not commas.
# ---------------------------------------------------------------
df = pd.read_csv(RAW, sep=";")
raw_rows = len(df)
print("Rows, columns:", df.shape)

# Shorter column names so the code is easier to read
df = df.rename(columns={
    "Page total likes": "page_likes",
    "Type": "format",
    "Category": "category",
    "Post Month": "month",
    "Post Weekday": "weekday",
    "Post Hour": "hour",
    "Paid": "paid",
    "Lifetime Post Total Reach": "reach",
    "Lifetime Post Total Impressions": "impressions",
    "comment": "comments",
    "like": "likes",
    "share": "shares",
    "Total Interactions": "total_interactions",
})
keep = ["page_likes", "format", "category", "month", "weekday", "hour",
        "paid", "reach", "impressions", "likes", "comments", "shares",
        "total_interactions"]
df = df[keep].copy()

# ---------------------------------------------------------------
# Step 2. Missing values and duplicates
# ---------------------------------------------------------------
missing_before = df.isna().sum()
missing_before = missing_before[missing_before > 0].to_dict()
print("Blanks before cleaning:", missing_before)

# Check the rule: total_interactions = likes + comments + shares
complete = df.dropna(subset=["likes", "shares"])
rule_holds = bool((complete["likes"] + complete["comments"] + complete["shares"]
                   == complete["total_interactions"]).all())
print("Total = likes + comments + shares in every complete row:", rule_holds)

# Fill blank likes / shares from the total (the rule above makes this safe)
filled = {}
for col in ["likes", "shares"]:
    blank = df[col].isna()
    others = [c for c in ["likes", "comments", "shares"] if c != col]
    df.loc[blank, col] = df.loc[blank, "total_interactions"] - df.loc[blank, others].fillna(0).sum(axis=1)
    filled[col] = df.loc[blank, col].tolist()
print("Values filled in:", filled)

# The one blank Paid value stays blank; that post is skipped only in the paid comparison
duplicates = int(df.duplicated().sum())
print("Exact duplicate rows:", duplicates)

# ---------------------------------------------------------------
# Step 3. Correct data types
# ---------------------------------------------------------------
for col in ["likes", "shares", "comments", "total_interactions", "reach",
            "impressions", "page_likes", "month", "weekday", "hour"]:
    df[col] = df[col].astype(int)
df["paid"] = df["paid"].map({1.0: "Paid", 0.0: "Unpaid"})  # blank stays NaN
df["category"] = df["category"].map({1: "Action", 2: "Product", 3: "Inspiration"})

# ---------------------------------------------------------------
# Step 4. Flag suspicious records (flag, do not delete)
# ---------------------------------------------------------------
low_reach_cutoff = df["reach"].quantile(0.01)
df["flag_low_reach"] = df["reach"] < low_reach_cutoff
df["flag_reach_gt_impr"] = df["reach"] > df["impressions"]
df["flag_any"] = df["flag_low_reach"] | df["flag_reach_gt_impr"]
print("Reach of zero:", int((df["reach"] == 0).sum()))
print("Low-reach cutoff (1st percentile):", low_reach_cutoff)
print("Low-reach posts:", int(df["flag_low_reach"].sum()))
print("Reach > impressions:", int(df["flag_reach_gt_impr"].sum()))

# ---------------------------------------------------------------
# Step 5. Create new variables
# ---------------------------------------------------------------
df["interactions"] = df["likes"] + df["comments"] + df["shares"]
df["engagement_rate"] = (df["interactions"] / df["reach"] * 100).round(3)

def time_block(h):
    if h <= 5:
        return "Overnight (12-5 AM)"
    if h <= 11:
        return "Morning (6-11 AM)"
    if h <= 17:
        return "Afternoon (12-5 PM)"
    return "Evening (6-11 PM)"

df["time_block"] = df["hour"].apply(time_block)

df["page_size_quartile"] = pd.qcut(df["page_likes"], 4,
                                   labels=["Q1 smallest", "Q2", "Q3", "Q4 largest"])

df.to_csv(CLEAN, index=False)
print("Saved", CLEAN, df.shape)

# ---------------------------------------------------------------
# Step 6. Exploration: medians and post counts
# ---------------------------------------------------------------
def summary(data, by):
    t = (data.groupby(by, observed=True)["engagement_rate"]
             .agg(posts="count", median="median")
             .round(2).reset_index())
    return t

results = {
    "raw_rows": raw_rows,
    "clean_rows": len(df),
    "missing_before": missing_before,
    "filled": filled,
    "rule_holds": rule_holds,
    "duplicates": duplicates,
    "low_reach_cutoff": float(low_reach_cutoff),
    "n_low_reach": int(df["flag_low_reach"].sum()),
    "n_reach_gt_impr": int(df["flag_reach_gt_impr"].sum()),
    "n_flag_any": int(df["flag_any"].sum()),
    "overall_median": round(float(df["engagement_rate"].median()), 2),
    "overall_mean": round(float(df["engagement_rate"].mean()), 2),
    "reach_median": int(df["reach"].median()),
    "quartile_cutoffs": [float(x) for x in df["page_likes"].quantile([0.25, 0.5, 0.75])],
    "hour_counts": df["hour"].value_counts().reindex(range(24), fill_value=0).tolist(),
}

unflagged = df[~df["flag_any"]]
tables = {
    "format": summary(df, "format"),
    "format_unflagged": summary(unflagged, "format"),
    "time_block": summary(df, "time_block"),
    "time_block_unflagged": summary(unflagged, "time_block"),
    "photo_time_block": summary(df[df["format"] == "Photo"], "time_block"),
    "quartile": summary(df, "page_size_quartile"),
    "quartile_month": (df.groupby("page_size_quartile", observed=True)["month"]
                         .agg(["min", "max"]).reset_index()),
    "paid": summary(df.dropna(subset=["paid"]), "paid"),
    "category": summary(df, "category"),
    "month": summary(df, "month"),
}
for name, t in tables.items():
    print("\n==", name)
    print(t.to_string(index=False))
    results[name] = t.astype(str).to_dict(orient="records")

with open("outputs/exploration_results.json", "w") as f:
    json.dump(results, f, indent=2)
