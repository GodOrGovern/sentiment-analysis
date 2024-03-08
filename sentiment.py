import pandas as pd
import os
import datetime
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from torch.nn.functional import softmax
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import sent_tokenize
from sklearn.preprocessing import MinMaxScaler


model = AutoModelForSequenceClassification.from_pretrained('ProsusAI/finBERT')
tokenizer = AutoTokenizer.from_pretrained('ProsusAI/finBERT')
sia = SentimentIntensityAnalyzer()


def split_text(text, chunk_size):
    '''
    Args:
        text:       string of text
        chunk_size: size of chunks to split 'text' into

    Returns:
        list of 'text' split into strings of length 'chunk_size'
    '''
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]


def analyze_sentiment(text):
    '''
    Args:
        text: string of text

    Returns:
        Sentiment of 'text'
    '''
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    outputs = model(**inputs)
    probabilities = softmax(outputs.logits, dim=1)
    return probabilities[0]


def get_quarter(month):
    '''
    Args:
        month: month of the year

    Returns:
        Financial quarter of 'month'
    '''
    if month <= 3:
        return 1
    elif month <= 6:
        return 2
    elif month <= 9:
        return 3
    else:
        return 4

# parent directory for sentiment scores
scores_directory = "scores"

def process_workbook(workbook_filename, keywords_filename, last_date=None):
    ''' 
    Args:  
        workbook_filename:  Name of Excel file containing workbook of companies, one company per worksheet.
                            Each column holds a transcript for one quarter's earning call.

        keywords_filename:  Name of Excel file with keywords. Headers 'Keyword' and 'Key Word Category'

        last_date:  Given as (year, quarter)
                    If specified, the last quarter to process per company. Otherwise process all.
                    Example: 'last_date = (2021, 3)' means process each worksheet/company from
                             most recent call until Q3 of 2021

    Result:
        Creates one excel sheet for each column of each worksheet.
        Excel sheets have headers:  'Key Word Category', 'Keyword', 'Paragraph', 
                                    'Sentiment Score', 'Sentiment Magnitude' 
        Sheets are stored under ./{scores_directory}/{company_name}/{sheet_name}

    Returns:
        None
    '''
    keywords_df = pd.read_excel(keywords_filename)
    workbook = pd.ExcelFile(workbook_filename)

    for sheet_name in workbook.sheet_names:
        sheet_df = pd.read_excel(workbook, sheet_name=sheet_name)

        # Create a directory locally
        if not os.path.exists(f'./{scores_directory}/{sheet_name}'):
            os.makedirs(f'./{scores_directory}/{sheet_name}')

        for column in sheet_df.columns:
            # Hacky workaround to get date
            if isinstance(sheet_df[column][0], datetime.datetime):
                date = sheet_df[column][0]
            else:
                date = pd.to_datetime(column.removeprefix('FINAL TRANSCRIPT'))

            quarter = get_quarter(date.month)

            # stop processing sheet if earlier than 'last_date'
            if last_date and (date.year, quarter) < last_date:
                break

            # get output name and skip column if it already exists (avoid redundant processing)
            output_filename = f'CC_{sheet_name}_Q{quarter}{date.year}_{date.month}_{date.day}_{date.year}.xlsx'
            if os.path.exists(f'./{scores_directory}/{sheet_name}/{output_filename}'):
                continue

            # column and save the output to excel file
            output_df = process_transcript(sheet_df[column], keywords_df)
            output_df.to_excel(f'./{scores_directory}/{sheet_name}/{output_filename}', index=False)


def process_transcript(transcript_df, keywords_df):
    '''
    Args:
        transcript_df:  dataframe of transcript, essentially a list of paragraphs
        keywords_df:    dataframe with 'Keyword' and 'Key Word Category'

    Returns:
        output_df:  Dataframe with headers: 'Key Word Category', 'Keyword', 'Paragraph', 
                                            'Sentiment Score', 'Sentiment Magnitude'
    '''
    output_df = pd.DataFrame(columns=['Key Word Category', 'Keyword', 'Paragraph', 'Sentiment Score', 'Sentiment Magnitude'])

    for index, row in keywords_df.iterrows():
        keyword = row['Keyword']
        category = row['Key Word Category']

        paragraphs = transcript_df.apply(lambda x: str(x) if keyword.lower() in str(x).lower() else None).dropna()

        # some paragraphs contain multiple keywords and are therefore processed multiple times
        # TODO: avoid redundant processing
        for paragraph in paragraphs:
            chunks = split_text(paragraph, 1024)
            for chunk in chunks:
                sentiment_score, total_magnitude = process_chunk(chunk)
                new_row = {'Key Word Category': category, 'Keyword': keyword, 'Paragraph': chunk, 
                            'Sentiment Score': sentiment_score.item(), 'Sentiment Magnitude': total_magnitude}
                output_df = pd.concat([output_df, pd.DataFrame([new_row])], ignore_index=True)

    return output_df


def process_chunk(chunk):
    '''
    Args:
        chunk: string of text, presumably a paragraph

    Returns:
        Tuple of (sentiment_score, total_magnitude)
        sentiment_score: sentiment of 'chunk'
        total_magnitude: magnitude of 'chunk' sentiment
    '''
    probabilities = analyze_sentiment(chunk)
    sentiment_score = (probabilities[1] + (probabilities[2] * 2) + (probabilities[0] * 3)) - 2
    
    sentences = sent_tokenize(chunk)
    magnitudes = []
    for sentence in sentences:
        sentence_magnitude = abs(sia.polarity_scores(sentence)['compound'])
        magnitudes.append(sentence_magnitude)
    total_magnitude = sum(magnitudes)
    
    return sentiment_score, total_magnitude


def calculate_weighted_sentiment(sentiment_filename, keywords_filename):
    '''
    Args:
        sentiment_filename: Name of Excel file with sentiment results for a transcript.
                            Headers such as: 'Sentiment Score', 'Keyword', 'Paragraph' 

        keywords_filename:  Name of Excel file with keywords and their weights (under 'Proposed').
                            Headers such as: 'Keyword', 'Proposed'

    Result:
        Adds columns 'Proposed' and 'Weighted Sentiment Score' to 'sentiment_filename', which contains the original
        'Sentiment Score' multiplied by 'Proposed' weight for 'Keyword', scaled to between 0 and 1.

    Returns:
        None
    '''
    # Read the files
    sentiment_df = pd.read_excel(sentiment_filename)
    keywords_df = pd.read_excel(keywords_filename)

    # Map the qualitative assessments to quantitative weights
    importance_weights = {
        'Very Important': 1.5,
        'Important': 1.0,
        'Less Important': 0.5
    }
    keywords_df['Weight'] = keywords_df['Proposed'].map(importance_weights)

    # Merge the sentiment DataFrame with the keyword weights DataFrame and drop duplicate columns
    sentiment_df = pd.merge(sentiment_df, keywords_df, left_on='Keyword', right_on='Keyword', how='left', 
                            suffixes=('', '_DROP')).filter(regex='^(?!.*_DROP)')

    # Calculate the proposed sentiment score using keyword weights
    sentiment_df['Weighted Sentiment Score'] = sentiment_df['Sentiment Score'] * sentiment_df['Weight']

    # Normalize the weighted sentiment score to be between 0 and 1
    scaler = MinMaxScaler()
    sentiment_df['Weighted Sentiment Score'] = scaler.fit_transform(sentiment_df[['Weighted Sentiment Score']])

    # Save the DataFrame with the new column to the same Excel file
    sentiment_df.to_excel(sentiment_filename, index=False)
