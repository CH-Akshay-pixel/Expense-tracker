from google import genai
from django.conf import settings


def get_ai_client():
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    return client


def categorize_expense(title, available_categories):
    """Auto-detect category from expense title"""
    client = get_ai_client()
    categories_list = ', '.join(available_categories)

    prompt = f"""You are an expense categorizer.
Given this expense title: "{title}"
Available categories: {categories_list}

Reply with ONLY the category name that best matches.
If none match, reply with "Other".
Do not explain, just the category name."""

    response = client.models.generate_content(
        model='gemini-1.5-flash-8b',
        contents=prompt
    )
    return response.text.strip()


def get_spending_insights(expenses_data, currency, budget):
    """Generate AI spending insights"""
    client = get_ai_client()

    prompt = f"""You are a personal finance advisor.
Analyze this spending data and give 3 specific actionable insights:

Currency: {currency}
Monthly Budget: {budget}
Spending by category: {expenses_data}

Format your response as exactly 3 insights.
Each insight should start with an emoji.
Be specific with numbers.
Keep each insight to 2 sentences max.
Be friendly and encouraging."""

    response = client.models.generate_content(
        model='gemini-1.5-flash-8bflash',
        contents=prompt
    )
    return response.text.strip()


def get_budget_recommendation(expenses_data, income, currency):
    """Generate AI budget recommendations"""
    client = get_ai_client()

    prompt = f"""You are a personal finance advisor.
Based on this spending history, recommend a monthly budget:

Currency: {currency}
Monthly Income: {income}
Average spending by category: {expenses_data}

Provide:
1. Recommended monthly budget total
2. Budget breakdown by category
3. One key saving tip

Format as clean readable text with emojis.
Be specific with {currency} amounts."""

    response = client.models.generate_content(
        model='gemini-1.5-flash-8b',
        contents=prompt
    )
    return response.text.strip()


def chat_with_ai(user_message, expenses_context):
    """AI chatbot for expense queries"""
    client = get_ai_client()

    prompt = f"""You are a helpful expense tracking assistant.
You have access to the user's expense data:

{expenses_context}

User question: {user_message}

Answer helpfully and concisely.
Use the expense data to give specific answers.
If you don't have enough data, say so kindly."""

    response = client.models.generate_content(
        model='gemini-1.5-flash-8b',
        contents=prompt
    )
    return response.text.strip()