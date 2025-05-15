# chatbot_engine_final.py

import openai
from semantic_search import search_similar_articles
from config import (
    OPENAI_API_KEY, OPENAI_ENDPOINT, OPENAI_API_VERSION,
    EMBEDDING_DEPLOYMENT_NAME, OPENAI_TYPE, CHAT_DEPLOYMENT_NAME
)

# Initialize OpenAI client
openai.api_key = OPENAI_API_KEY
openai.api_base = OPENAI_ENDPOINT
openai.api_version = OPENAI_API_VERSION
openai.api_type = OPENAI_TYPE

REGIONS = ["Africa", "Asia", "Europe", "Middle East", "North America", "South America"]
TOPICS = ["Politics", "Economy", "Sports", "Science", "Technology", "Climate"]


def generate_response(prompt, language="en"):
    """
    Search for relevant articles and generate a response only using the database content.
    """
    try:
        articles = search_similar_articles(prompt, k=3)
        if articles.empty:
            return "❌ لا توجد مقالات ذات صلة." if language == "ar" else "❌ No related articles found."

        response_parts = []
        for _, row in articles.iterrows():
            entry = f"**{row['Headline']}**\n\n{row['Summary']}\n\n[Read More]({row['URL']})"
            if language == "ar":
                entry = translate_to_arabic(entry)
            response_parts.append(entry)

        return "\n\n".join(response_parts)

    except Exception as e:
        return f"❌ Error fetching news: {str(e)}"


def translate_to_arabic(text):
    """
    Safely translate English text to Arabic using OpenAI with filtering protection.
    """
    try:
        response = openai.ChatCompletion.create(
            deployment_id=CHAT_DEPLOYMENT_NAME,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a professional translator. Only translate the given text from English to Modern Standard Arabic (MSA) "
                        "in a clear and neutral tone, preserving factual accuracy. Do not generate, summarize, or modify the content."
                    )
                },
                {"role": "user", "content": text}
            ],
            max_tokens=500,
            temperature=0.5
        )
        return response.choices[0].message["content"]

    except openai.error.InvalidRequestError as e:
        if "content management policy" in str(e):
            return "⚠️ لا يمكن ترجمة هذا المحتوى تلقائيًا بسبب السياسات. يرجى مراجعة المحتوى يدويًا."
        return f"⚠️ خطأ في الترجمة: {e}"

    except Exception as e:
        return f"⚠️ تعذر الترجمة: {e}"



def get_predefined_articles(region, topic, language="en"):
    """
    Returns summaries from the database only (no generation), with a read-more link.
    """
    query = f"{topic} in {region}"
    results = search_similar_articles(query, k=3)

    if results.empty:
        return [{"role": "bot", "content": "❌ لا توجد مقالات" if language == "ar" else "❌ No articles found for this topic."}]

    response = []
    for _, row in results.iterrows():
        summary = f"**{row['Headline']}**\n\n{row['Summary']}\n\n[Read More]({row['URL']})"
        if language == "ar":
            summary = translate_to_arabic(summary)
        response.append({"role": "bot", "content": summary})

    return response
