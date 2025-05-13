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

# Predefined options
REGIONS = ["Africa", "Asia", "Europe", "Latin America", "Middle East" , "US & Canada"]
TOPICS = ["Politics", "Economy", "Climate", "Sports", "Uncategorized"]

# User state
user_route = None
selected_region = None
selected_topic = None


def welcome_message():
    return (
        "\n👋 Welcome to Al Jazeera News Assistant!\n"
        "Would you like *predefined topics* or *ask a custom question*?\n"
        "Type '1' for Predefined Topics or '2' for Custom Question."
    )


def handle_predefined_route():
    global selected_region, selected_topic
    if not selected_region:
        print("\n🌍 What region are you interested in?")
        for idx, region in enumerate(REGIONS, start=1):
            print(f"{idx}. {region}")
        try:
            choice = int(input("Enter number: "))
            selected_region = REGIONS[choice - 1]
        except (IndexError, ValueError):
            print("Invalid selection. Please try again.")
            return
    if not selected_topic:
        print("\n📰 What type of news are you interested in?")
        for idx, topic in enumerate(TOPICS, start=1):
            print(f"{idx}. {topic}")
        try:
            choice = int(input("Enter number: "))
            selected_topic = TOPICS[choice - 1]
        except (IndexError, ValueError):
            print("Invalid selection. Please try again.")
            return

    # Query formulation for search
    query = f"{selected_topic} in {selected_region}"
    articles = search_similar_articles(query, k=3)
    if articles.empty:
        print("Sorry, no relevant news found.")
    else:
        print("\n🗞️ Here are some articles you might find interesting:")
        for _, row in articles.iterrows():
            print(f"\n- {row['Headline']}\n  {row['Summary']}\n  🔗 {row['URL']}")

    ask_to_switch()


def generate_response(prompt):
    try:
        relevant_passages = search_similar_articles(prompt, k=3)
        if relevant_passages.empty:
            return "I'm sorry, I couldn't find any related news in the database."

        context = "\n\n".join([
            f"{row['Headline']} - {row['Summary']} (URL: {row['URL']})"
            for _, row in relevant_passages.iterrows()
        ])

        full_prompt = (
            f"Use the following articles as context:\n\n{context}\n\n"
            f"Now answer this question based only on the provided context:\n{prompt}"
        )

        response = openai.ChatCompletion.create(
            deployment_id=CHAT_DEPLOYMENT_NAME,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful Al Jazeera news assistant. Only provide answers based "
                        "on Al Jazeera articles provided as context. Cite the article URL in your response."
                    )
                },
                {"role": "user", "content": full_prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )

        return response.choices[0].message["content"]

    except Exception as e:
        return f"Error generating response: {str(e)}"


def ask_to_switch():
    global user_route, selected_region, selected_topic
    print("\nWould you like to switch modes? Type '1' for Predefined Topics, '2' for Custom Question, or 'exit' to quit.")
    choice = input("Selection: ").strip()
    if choice == '1':
        user_route = 'predefined'
        selected_region = None
        selected_topic = None
    elif choice == '2':
        user_route = 'custom'
    elif choice.lower() in ['exit', 'quit']:
        print("👋 Goodbye! Thanks for using Al Jazeera News Assistant.")
        exit()


if __name__ == "__main__":
    print(welcome_message())
    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in ['exit', 'quit']:
            print("👋 Goodbye! Thanks for using Al Jazeera News Assistant.")
            break

        if user_input == '1':
            user_route = 'predefined'
        elif user_input == '2':
            user_route = 'custom'

        if user_route == 'predefined':
            handle_predefined_route()

        elif user_route == 'custom':
            answer = generate_response(user_input)
            print(f"AI: {answer}")
            ask_to_switch()

        else:
            print("Please select a valid route: Type '1' for Predefined Topics or '2' for Custom Question.")
