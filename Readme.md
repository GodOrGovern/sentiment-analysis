# Sentiment Analysis

Programs to perform sentiment analysis on company transcripts (eg 10-Q, 10-K) and plot sentiment data.

## Getting Started

Install required packages  
`pip install -r requirements.txt`

Unzip example_scores.zip.
\
Run main.py to ensure everything is working (may take a few minutes).
\
Check in-line documentation for function behavior.

## Files

### main.py

Quick example of basic use. Run to ensure everything is working.

### sentiment.py

Used to analyze sentiment of transcripts.  
Primary functions: 'process_workbook' and 'calculate_weighted_sentiment'

### plot.py

Used to plot sentiment values.  
Primary functions: 'plot_individual_weighted_sentiment' and 'plot_overall_weighted_sentiment'

### summary.py

Used to summarize quarterly sentiment scores.
Primary functions: summarize_company_quarter

#### weighted_keywords.xlsx

Excel file containing keywords, categories, sectors, and proposed keyword weights. May only contain a subset of total keywords (hence keywords.xlsx).

#### keywords.xlsx

Excel file containing keywords and categories without weights or sectors.

#### example_companies.xlsx

Workbook of company transcripts. One company per sheet, one transcript per column.

#### example_scores.zip

Contains the output of process_workbook("example_companies.xlsx", "keywords.xlsx", (2021, 3)). Useful for testing weighted sentiment and plotting functions.
