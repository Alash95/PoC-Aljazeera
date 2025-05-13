import requests
from bs4 import BeautifulSoup
import pandas as pd

# Define region URLs
regions = {
    "Africa": "https://www.aljazeera.com/africa/",
    "Asia": "https://www.aljazeera.com/asia/",
    "US & Canada": "https://www.aljazeera.com/us-canada/",
    "Latin America": "https://www.aljazeera.com/latin-america/",
    "Europe": "https://www.aljazeera.com/europe/",
    "Middle East": "https://www.aljazeera.com/middle-east/"
}

# Define keywords to infer categories
category_keywords = {
    "Politics": [
        "election", "president", "minister", "parliament", "government", "vote", "senate", "law", "campaign",
        "democracy", "autocracy", "dictator", "Trump", "Biden", "Zelenskyy", "Putin", "Xi Jinping", "diplomacy",
        "ambassador", "white house", "politics", "policy", "constitution", "republic", "democrat", "republican",
        "congress", "prime minister", "foreign affairs", "national security", "legislation", "executive order",
        "cabinet", "coalition", "regime", "corruption", "scandal", "voting", "ballot", "referendum", "senator",
        "governor", "public office", "dissent", "state department", "sanctions", "asylum", "treaty", "diplomat"
    ],
    "Economy": [
        "economy", "inflation", "deflation", "stock market", "dow jones", "nasdaq", "trade", "tariff", "exports",
        "imports", "finance", "financial", "bank", "banking", "interest rates", "currency", "foreign exchange",
        "investment", "bonds", "recession", "depression", "stimulus", "unemployment", "economic growth", "fiscal",
        "monetary", "budget", "debt", "credit", "loan", "mortgage", "wage", "income", "poverty", "wealth",
        "rich", "gdp", "venture capital", "startup", "commodity", "oil prices", "cryptocurrency", "bitcoin",
        "ethereum", "forex", "treasury", "central bank", "nasdaq"
    ],
    "Sports": [
        "match", "tournament", "goal", "football", "soccer", "nba", "mlb", "olympics", "athlete", "sports",
        "coach", "team", "score", "win", "loss", "draw", "championship", "medal", "referee", "fans", "stadium",
        "injury", "player", "world cup", "uefa", "fifa", "champions league", "grand slam", "tennis", "cricket",
        "baseball", "basketball", "rugby", "boxing", "mma", "wrestling", "golf", "race", "formula 1", "nascar",
        "athletics", "marathon", "record", "qualifier", "league", "fixtures", "transfer", "scoreboard"
    ],
    "Science and Technology": [
        "technology", "science", "AI", "artificial intelligence", "machine learning", "deep learning", "robotics",
        "innovation", "data", "quantum", "research", "experiment", "tech", "startups", "software", "hardware",
        "cybersecurity", "hackers", "space", "nasa", "satellite", "mars", "tesla", "elon musk", "big data",
        "bioinformatics", "biotech", "genetics", "biotechnology", "quantum computing", "internet", "apps",
        "smartphone", "5G", "IoT", "blockchain", "VR", "AR", "augmented reality", "virtual reality", "nanotech",
        "cloud computing", "server", "GPU", "semiconductor", "chip", "encryption", "database"
    ],
    "Climate": [
        "climate", "global warming", "carbon", "emissions", "environment", "weather", "greenhouse", "pollution",
        "co2", "carbon footprint", "renewable", "solar", "wind", "deforestation", "biodiversity", "ice caps",
        "melting", "sea level", "natural disaster", "earthquake", "flood", "hurricane", "storm", "heatwave",
        "drought", "wildfire", "temperature rise", "fossil fuels", "climate crisis", "ecosystem", "sustainability",
        "environmental policy", "green energy", "electric vehicle", "recycling", "carbon trading", "net zero",
        "paris agreement", "environmentalist", "UN climate summit", "greta thunberg", "weather pattern", "ozone",
        "air quality", "climate justice", "climate denial", "methane", "energy transition"
    ]
}

# Limit per region
ARTICLE_LIMIT = 100

# Helper: infer category from text
def infer_category(text):
    text = text.lower()
    for category, keywords in category_keywords.items():
        if any(keyword in text for keyword in keywords):
            return category
    return "Uncategorized"

# Scrape function
def extract_articles(region_name, url):
    articles_list = []
    try:
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.content, "html.parser")
        articles = soup.find_all("article")[:ARTICLE_LIMIT]

        for article in articles:
            headline = article.find("h3").text.strip() if article.find("h3") else ""
            summary = article.find("p").text.strip() if article.find("p") else ""
            link_tag = article.find("a", href=True)
            article_url = "https://www.aljazeera.com" + link_tag["href"] if link_tag else ""
               
            category = infer_category(headline + " " + summary)

            articles_list.append({
                "Region": region_name,
                "Category": category,
                "Headline": headline,
                "Summary": summary,
                "URL": article_url
            })
    except Exception as e:
        print(f"Error scraping {region_name}: {e}")
    return articles_list

# Collect all data
all_articles = []
for region, url in regions.items():
    all_articles.extend(extract_articles(region, url))

# Save
df = pd.DataFrame(all_articles)
df.to_csv("aljazeera_news.csv", index=False)
print("✅ Saved as aljazeera_news.csv")