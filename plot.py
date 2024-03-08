import pandas as pd
import os
import re
import pandas as pd
import matplotlib.pyplot as plt

def group_files_by_company(directory):
    '''
    Args:
        directory: path to directory with sentiment excel files for a given company
        File naming format CC_{company}_Q{quarter}{year}_{month}_{day}_{year}.xlsx"

    Returns:
        files_by_company: dictionary with company names as keys and their
        associated (files, quarter_year of files) as items.
    '''
    files_by_company = {}
    for filename in os.listdir(directory):
        match = re.search(r'CC_(.+)_Q(\d{1})(\d{4})', filename)
        if match:
            company = match.group(1)
            quarter_year = 'Q' + match.group(2) + match.group(3)
            if company not in files_by_company:
                files_by_company[company] = []
            files_by_company[company].append((filename, quarter_year))
    return files_by_company


def plot_overall_weighted_sentiment(directory):
    '''
    Args:
        directory: path to directory of sentiment excel files for a given company. 
        Each file has headers such as: 'Weighted Sentiment Score', 'Keyword', 'Keyword Category'
    
    Result:
        Line graph showing weighted sentiment scores for a given company over time.
        Saved as a .png to 'directory'

    Returns:
        None
    '''
    files_by_company = group_files_by_company(directory)

    for company, file_quarter_pairs in files_by_company.items():
        print(f'Processing files for company: {company}')  # Print the company name

        plt.clf()
        sentiment_scores = []

        # Sort file_quarter_pairs based on quarter and year
        file_quarter_pairs.sort(key=lambda x: (int(x[1][2:]), int(x[1][1:2])))
        for filename, quarter_year in file_quarter_pairs:
            df = pd.read_excel(os.path.join(directory, filename), engine='openpyxl')
            total_sentiment_score = df['Weighted Sentiment Score'].sum()  # Calculate the sum instead of the average
            sentiment_scores.append((quarter_year, total_sentiment_score))

        quarters, scores = zip(*sentiment_scores)
        plt.plot(quarters, scores)
        plt.xlabel('Quarter')
        plt.ylabel('Average Weighted Sentiment Score')
        plt.title(f'Average Weighted Sentiment Score per Quarter for {company}')
        plt.savefig(os.path.join(directory, f'{company}_Weighted_Sentiment.png'))


def plot_individual_weighted_sentiment(directory):
    '''
    Args:
        directory: path to directory of sentiment excel files for a given company. 
        Each file has headers such as: 'Weighted Sentiment Score', 'Keyword', 'Keyword Category'
    
    Result:
        Line graph showing weighted sentiment scores for a given company over time.
        Scores are broken up by category (eg Finanical Metric, Macro, Sector Trend)
        Saved as a .png to 'directory'

    Returns:
        None
    '''
    files_by_company = group_files_by_company(directory)

    for company, file_quarter_pairs in files_by_company:
        print(f'Processing files for company: {company}')

        plt.clf()
        sentiment_scores_by_category = {}

        # Sort file_quarter_pairs based on quarter and year
        file_quarter_pairs.sort(key=lambda x: (int(x[1][2:]), int(x[1][1:2])))

        for filename, quarter_year in file_quarter_pairs:
            df = pd.read_excel(os.path.join(directory, filename))

            category_scores = df.groupby('Key Word Category')['Weighted Sentiment Score'].mean()

            # Update the sentiment_scores_by_category dictionary
            for category, score in category_scores.items():
                if category in ["Financial metric - All", "Macro", "Sector trend"]:
                    if category not in sentiment_scores_by_category:
                        sentiment_scores_by_category[category] = []
                    sentiment_scores_by_category[category].append((quarter_year, score))

        # Plot sentiment scores for each category
        for category, scores in sentiment_scores_by_category.items():
            quarters, category_scores = zip(*scores)
            plt.plot(quarters, category_scores, label=category)

        plt.ylim(0, 1)
        plt.xlabel('Quarter')
        plt.ylabel('Average Weighted Sentiment Score')
        plt.title(f'Average Weighted Sentiment Score per Quarter for {company}')
        plt.legend()
        plt.savefig(os.path.join(directory, f'{company}_Weighted_Sentiment_Categories.png'))