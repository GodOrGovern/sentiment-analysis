import os
from sentiment import process_workbook, calculate_weighted_sentiment
from plot import plot_individual_weighted_sentiment, plot_overall_weighted_sentiment

# Only processes first transcript (ie Q3 2023) for each company
process_workbook("example_companies.xlsx", "weighted_keywords.xlsx", last_date=(2023, 2))

# calculates weighted scores and plots scores
scores_directory = 'example_scores'
for company in os.listdir(f'./{scores_directory}'):
    company_path = os.path.join(scores_directory, company)
    for filename in os.listdir(company_path):
        if filename.endswith('.xlsx'):
            calculate_weighted_sentiment(os.path.join(company_path, filename), "weighted_keywords.xlsx")
    plot_individual_weighted_sentiment(company_path)
    plot_overall_weighted_sentiment(company_path)

