Getting Started:
    (Optional) create a python virtual environment:
        python -m venv <path/to/environment>
        Follow instructions online for activation and general use.

    Install required packages:
        pip install -r requirements.txt

    Unzip example_scores.zip
    
    Run main.py to ensure everything is working (may take a few minutes).
    Let me (David K) know if you encounter errors.

    Check in-line documentation for function behavior.


Overview:
    Basic idea is to perform sentiment analysis on company earnings calls transcripts and plot data.

    Given:
        A workbook with transcripts of company earnings calls. One company per worksheet, one transcript per column.
        An Excel file with keywords, keyword categories, and possibly keyword weights (for calculate_weighted_sentiment).
    
    process_workbook() runs sentiment analysis on each transcript, using keywords to select relevant paragraphs.
    Paragraphs, keywords, sentiment scores, and other data are stored in an Excel file. One file per transcript.
    
    calculate_weighted_sentiment() adds a 'Weighted Sentiment Score' column to each Excel file using keyword weights.

    plot_{type}_weighted_sentiment() functions plot the weighted sentiment data in each Excel file.

Next steps:
    Migrate from excel to google datastore
    Build google connectivity and functionality
    Make plotting more dynamic

main.py:
    Just a quick example of basic use. Run to ensure everything is working.

sentiment.py:
    Used to analyze sentiment of transcripts.
    Primary functions: 'process_workbook' and 'calculate_weighted_sentiment'

plot.py
    Used to plot sentiment values.
    Primary functions: 'plot_individual_weighted_sentiment' and 'plot_overall_weighted_sentiment'

Other files/directories:
    weighted_keywords.xlsx:
        Excel file containing keywords, categories, sectors, and proposed keyword weights.
        May only contain a subset of total keywords (hence keywords.xlsx).

    keywords.xlsx:
        Excel file containing keywords and categories without weights or sectors.

    example_companies.xlsx:
        Workbook of company transcripts. One company per sheet, one transcript per column.
    
    example_scores.zip:
        Contains the output of process_workbook("example_companies.xlsx", "keywords.xlsx", (2021, 3)).
        Useful for testing weighted sentiment and plotting functions.
        Would take several hours to reproduce.
