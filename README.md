# Social Media Engagement Analysis

**Status: in progress.** This is my capstone project for the NYU SPS Data Analytics program. The final version is due December 1, 2026. The findings below are drafts and may change.

## Project question
**How are social media post format and posting hour associated with reach-based engagement rates?**

Engagement rate = (likes + comments + shares) ÷ reach × 100

I measure engagement against reach instead of follower count because a post that reaches more people usually gets more likes anyway. I use medians instead of averages so a few posts that did really well don't skew the results.

**Intended audience:** a Director of Social Media Strategy at a digital marketing agency, who decides what content gets made and when it is posted.

## Data
**Facebook Metrics dataset** from the [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/368/facebook+metrics) (CC BY 4.0). It has 500 posts from one cosmetics brand's Facebook page in 2014, with the post format, posting hour, reach, and interactions for each post.

> Moro, S., Rita, P., & Vala, B. (2016). Predicting social media performance metrics and evaluation of the impact on brand building: A data mining approach. *Journal of Business Research, 69*(9), 3341–3351. https://doi.org/10.1016/j.jbusres.2016.02.010

I started with an Instagram dataset of about 30,000 posts from Hugging Face (see the proposal). When I explored it, the posts were spread almost evenly across all 24 hours, including 3 and 4 AM, and the source didn't say where the data came from. I decided it was most likely simulated and switched to this real dataset, which comes from a published study.

## Progress

| Step | Status | File |
|---|---|---|
| Project proposal | Done | [reports/01_Project_Proposal.pdf](reports/01_Project_Proposal.pdf) |
| Dataset and analysis plan | Done | [reports/02_Dataset_and_Analysis_Plan.pdf](reports/02_Dataset_and_Analysis_Plan.pdf) |
| Data cleaning and exploration | Done | [reports/03_Data_Cleaning_and_Exploration.pdf](reports/03_Data_Cleaning_and_Exploration.pdf) |
| Analysis outputs (SQL) | Done | [reports/04_Analysis_Outputs.pdf](reports/04_Analysis_Outputs.pdf) |
| Tableau dashboard | Next | |
| Final paper, slides, and video | Due Dec 1 | |

## Draft findings
1. **Photos had the highest engagement rate.** The median was 2.45% for photos (426 posts), compared with 1.53% for status updates, 0.68% for links, and 0.55% for videos. Photos were still higher inside each content category (product, inspiration, and action).
2. **Overnight and morning posts did better than afternoon posts.** For photos, the median was 2.77% overnight, 2.61% in the morning, and 1.93% in the afternoon. The dataset doesn't say what time zone the hours are in, so I can't name a best time to post.
3. **Page-size quartiles are also time-of-year groups.** The page grew all year, so each quartile covers a different part of 2014. The quartiles with lower engagement also had more action posts (offers and contests) and fewer photos.

## How I cleaned the data
- Filled 5 blank like and share values using Total Interactions (in every complete row, Total Interactions = likes + comments + shares)
- Checked for duplicates (there were none) and fixed the data types
- Flagged 5 very low-reach posts and 4 posts where reach was higher than impressions, so I can run results with and without them
- Created engagement rate, time block, and page-size quartile columns

## Folder guide
```
data/raw/          original UCI file and its description
data/cleaned/      cleaned file used for the analysis
scripts/           Python (pandas) cleaning script
sql/               SQLite scripts: load the data, then run the analysis queries
outputs/           cleaning log, query results, and summary tables
reports/           the write-up for each stage of the project
```

## How to run it
From the main project folder:
```bash
python3 scripts/clean_facebook_metrics.py
sqlite3 outputs/facebook_metrics.db < sql/load_data.sql
sqlite3 outputs/facebook_metrics.db < sql/analysis_queries.sql
```

## Limitations
- One brand, one platform, one year. The results describe this page, not social media in general.
- Only 7 videos and 22 links, so those formats can't support strong conclusions.
- The time zone for posting hour is not given.
- Page size and time of year move together, so their effects can't be separated.

**Tools:** Python (pandas), SQL (SQLite), Tableau (in progress)
