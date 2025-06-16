from crawlers.news import crawl_news_articles_stream
# from crawlers.paper import crawl_scholar_papers
# from crawlers.blog import crawl_technical_blogs
# from crawlers.product import crawl_product_comparisons



async def crawler_agent(intent_result, user_data_dir=None, profile_directory=None, set_profile: bool = False, headless: bool = True, max_results: int = 10):
    if intent_result["intent"] == "NEWS":
        results = crawl_news_articles_stream(intent_result["query"], user_data_dir, profile_directory, set_profile, headless, max_results)
    # elif intent_result["intent"] == "PAPER":
    #     result = crawl_scholar_papers(intent_result["query"])
    # elif intent_result["intent"] == "BLOG":
    #     result = crawl_technical_blogs(intent_result["query"])
    # elif intent_result["intent"] == "PRODUCT":
    #     result = crawl_product_comparisons(intent_result["query"])
    else:
        results = []
    return results