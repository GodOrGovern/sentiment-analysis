from google.cloud import datastore

client = datastore.Client.from_service_account_json("key.json")

def query_company_quarter(company, quarter, kind):
    '''
    Input:
        company: Yahoo Ticker of company
        quarter: quarter to query, in QxYYYY format (x is one of 1,2,3,4)
        kind: The Datastore kind of the score entities

    Returns:
        company_quarter_query:  Datastore query object "storing" all score entities (under 'kind')
                                from 'company' during 'quarter'. Can be filtered by other keys (eg Category)
                                if properly indexed.
    '''
    sentiment_query = client.query(kind=kind)
    company_query = sentiment_query.add_filter("YahooTicker", "=", company)
    company_quarter_query = company_query.add_filter("Period", "=", quarter)
    return company_quarter_query

# scoring categories
categories = ["Macro", "Sector trend", "Financial metric - All", "Financial metric - Bank", "Regulation"]

def get_category_scores(company, quarter, kind):
    category_scores = {}
    for category in categories:
        company_quarter_q = query_company_quarter(company, quarter, kind)
        company_quarter_q.add_filter("Category", "=", category)
        aggregation_query = client.aggregation_query(company_quarter_q)
        aggregation_query.add_aggregations(
            [
                datastore.aggregation.CountAggregation(alias=f"{category} Count"),
                datastore.aggregation.AvgAggregation(property_ref="Score", alias=f"{category} Average"),
                datastore.aggregation.AvgAggregation(property_ref="WeightedSentiment", alias=f"{category} Weighted Average")
            ]
        )
        query_result = aggregation_query.fetch()
        for aggregation_results in query_result:
            for aggregation in aggregation_results:
                if "Weighted" in aggregation.alias:
                    # Normalize weighted scores from [0, 1] to [-1, 1] (0 if no values)
                    category_scores[aggregation.alias] = 2*aggregation.value - 1 if aggregation.value else 0
                else:
                    category_scores[aggregation.alias] = aggregation.value
    return category_scores

def get_total_scores(category_scores):
    total, weighted, count = 0, 0, 0
    for category in categories:
        total += category_scores[f"{category} Average"] * category_scores[f"{category} Count"]
        weighted += category_scores[f"{category} Weighted Average"] * category_scores[f"{category} Count"]
        count += category_scores[f"{category} Count"]
    try:
        return total / count, weighted / count
    except:
        return None, None


def summarize_company_quarter(company, quarter, kind):
    summary = get_category_scores(company, quarter, kind)
    total, weighted = get_total_scores(summary)
    summary["Total Average"] = total
    summary["Weighted Average"] = weighted
    summary["Yahoo Ticker"] = company
    summary["Period"] = quarter
    return summary

def upload_summary(summary):
    entity = datastore.Entity(client.key("Banks_Summary"))
    for key, item in summary.items():
        entity[key] = item
    client.put(entity)

def upload_companies(quarters, companies, kind):
    for company in companies:
        for quarter in quarters:
            summary = summarize_company_quarter(company, quarter, kind)
            upload_summary(summary)

upload_companies(["Q32021", "Q42021", "Q12022", "Q22022", "Q32022", "Q42022", "Q12023", "Q22023"], ["BAC US", "C US", "GS US", "JPM US", "WFC US"], "Banks")
