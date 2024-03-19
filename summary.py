from google.cloud import datastore

client = datastore.Client.from_service_account_json("key.json")

def query_company_quarter(company, quarter):
    sentiment_query = client.query(kind="Sentiment_Details")
    company_query = sentiment_query.add_filter("YahooTicker", "=", company)
    company_quarter_query = company_query.add_filter("Period", "=", quarter)
    return company_quarter_query


categories = ["Macro", "Sector trend", "Financial metric - All", "Financial metric - Bank", "Regulation"]

def get_category_scores(company, quarter):
    category_scores = {}
    for category in categories:
        company_quarter_q = query_company_quarter(company, quarter)
        company_quarter_q.add_filter("Category", "=", category)
        aggregation_query = client.aggregation_query(company_quarter_q)
        aggregation_query.add_aggregations(
            [
                datastore.aggregation.CountAggregation(alias=f"{category} Count"),
                datastore.aggregation.AvgAggregation(property_ref="Score", alias=f"{category} Average"),
                datastore.aggregation.SumAggregation(property_ref="Weighted Sentiment", alias=f"{category} Weighted Average")
            ]
        )
        query_result = aggregation_query.fetch()
        for aggregation_results in query_result:
            for aggregation in aggregation_results:
                category_scores[aggregation.alias] = aggregation.value
    return category_scores

def get_total_scores(category_scores):
    total, weighted, count = 0, 0, 0
    for category in categories:
        total += category_scores[f"{category} Average"] * category_scores[f"{category} Count"]
        weighted += category_scores[f"{category} Weighted Average"] * category_scores[f"{category} Count"]
        count += category_scores[f"{category} Count"]
    return total / count, weighted / count


def summarize_company_quarter(company, quarter):
    summary = get_category_scores(company, quarter)
    total, weighted = get_total_scores(summary)
    summary["Total Average"] = total
    summary["Weighted Average"] = weighted
    summary["Yahoo Ticker"] = company
    summary["Period"] = quarter
    return summary


