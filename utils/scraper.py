import feedparser

def fetch_rss_feed(url):
    feed = feedparser.parse(url)
    
    # Technical Diagnostic: Extract HTTP status (default to 0 if not available)
    status = getattr(feed, 'status', 0) 
    
    articles = []
    for entry in feed.entries:
        article_data = {
            'title': entry.get('title', 'No Title'),
            'link': entry.get('link', ''),
            'summary': entry.get('summary', 'No summary available.')
        }
        articles.append(article_data)
        
    # Return both the status and the data
    return status, articles

if __name__ == "__main__":
    test_url = ""
    results = fetch_rss_feed(test_url)
    print(f"Total articles found: {len(results)}")
    if len(results) > 0:
        print(f"First headline: {results[0]['title']}")
    #print("--- DEBUG START ---")