# chatbot_engine_final.py

from openai import AzureOpenAI, OpenAIError, InvalidRequestError
from semantic_search import search_similar_articles
import os
from dotenv import load_dotenv

load_dotenv()

AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
AZURE_CHAT_DEPLOYMENT_NAME = os.getenv("AZURE_CHAT_DEPLOYMENT_NAME")

client = AzureOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_version=AZURE_OPENAI_API_VERSION,
)

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
    Safely translate English text to Arabic using Azure OpenAI.
    """
    try:
        response = client.chat.completions.create(
            model=AZURE_CHAT_DEPLOYMENT_NAME,  # This is your deployment name, not base model
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
        return response.choices[0].message.content  # ✅ correct for SDK v1+

    except InvalidRequestError as e:
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
