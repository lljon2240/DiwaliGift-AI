
import os
import re
import json
from urllib.parse import quote_plus

import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# -----------------------------------------
# CONFIGURATION
# -----------------------------------------

load_dotenv()

st.set_page_config(
    page_title="DiwaliGift AI",
    page_icon="🎁",
    layout="wide"
)

# -----------------------------------------
# CUSTOM CSS
# -----------------------------------------

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #fffaf0, #fff1dc);
}

.main-title {
    text-align: center;
    font-size: 43px;
    font-weight: 800;
    color: #a64b08;
    margin-bottom: 5px;
}

.subtitle {
    text-align: center;
    color: #79512d;
    font-size: 16px;
    margin-bottom: 30px;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(255,255,255,0.85);
    border-radius: 15px;
}

.gift-heading {
    color: #a64b08;
    font-size: 21px;
    font-weight: 700;
}

.price {
    color: #14804a;
    font-weight: 700;
    font-size: 18px;
}

.footer {
    text-align: center;
    color: #886b4b;
    padding: 25px;
    font-size: 13px;
}

.stButton > button {
    border-radius: 10px;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)


# -----------------------------------------
# GOOGLE SHOPPING LINKS
# -----------------------------------------

def shopping_links(product_name):

    query = quote_plus(product_name)

    return {
        "Google Shopping":
            f"https://www.google.com/search?tbm=shop&q={query}",

        "Google Search":
            f"https://www.google.com/search?q={query}",

        "Amazon":
            f"https://www.amazon.in/s?k={query}",

        "Flipkart":
            f"https://www.flipkart.com/search?q={query}",

        "Myntra":
            f"https://www.myntra.com/{query}",

        "Meesho":
            f"https://www.meesho.com/search?q={query}"
    }


# -----------------------------------------
# GEMINI AI
# -----------------------------------------

def generate_gift_recommendations(
    api_key,
    recipient,
    relationship,
    budget,
    interests,
    gift_style,
    additional_info
):

    llm = ChatGoogleGenerativeAI(
        model="gemini-3.1-flash-lite",
        google_api_key=api_key,
        temperature=0.7
    )

    prompt = f"""
You are an expert Indian Diwali gift recommendation assistant.

Generate 6 personalized Diwali gift recommendations.

USER REQUIREMENTS:

Recipient: {recipient}
Relationship: {relationship}
Budget: {budget} INR
Interests: {interests}
Gift Style: {gift_style}
Additional Preferences: {additional_info}

IMPORTANT RULES:

1. Recommend practical gifts available in India.
2. Keep every individual gift within the user's budget.
3. Do not invent actual product listings, store URLs,
   seller names, ratings or stock availability.
4. Provide realistic approximate price ranges in INR.
5. Use specific product search terms suitable for
   Google Shopping.
6. Include a personalized reason for every recommendation.
7. Generate one personalized Diwali greeting.

RETURN ONLY VALID JSON in this format:

{{
  "gifts": [
    {{
      "name": "Gift name",
      "category": "Gift category",
      "estimated_price": "₹1,000 - ₹1,500",
      "description": "Gift description",
      "why_recommended": "Reason for recommendation",
      "personalization": "Personalization idea",
      "search_query": "Specific product search query",
      "icon": "🎁"
    }}
  ],
  "greeting": "Personalized Diwali greeting"
}}
"""

    response = llm.invoke(prompt)
    content = response.content

    if isinstance(content, list):
        content = "".join(
            item.get("text", "") if isinstance(item, dict)
            else str(item)
            for item in content
        )

    content = str(content).strip()

    # Remove Markdown JSON code fences if present
    content = re.sub(r"^```(?:json)?\s*", "", content)
    content = re.sub(r"\s*```$", "", content)

    # Extract JSON if additional text is returned
    start = content.find("{")
    end = content.rfind("}")

    if start == -1 or end == -1:
        raise ValueError("Gemini did not return valid JSON.")

    return json.loads(content[start:end + 1])


# -----------------------------------------
# HEADER
# -----------------------------------------

st.markdown(
    '<div class="main-title">🎁 DiwaliGift AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Your Intelligent AI-Powered Diwali Gift Shopping Assistant | Developed by <b>Mandar Kurundwade</b>'
    '</div>',
    unsafe_allow_html=True
)

st.divider()

# -----------------------------------------
# SIDEBAR
# -----------------------------------------

with st.sidebar:

    st.header("🎯 Gift Preferences")

    recipient = st.selectbox(
        "Who are you buying a gift for?",
        [
            "Mother",
            "Father",
            "Brother",
            "Sister",
            "Husband",
            "Wife",
            "Friend",
            "Colleague",
            "Children",
            "Teacher",
            "Other"
        ]
    )

    relationship = st.selectbox(
        "Relationship",
        [
            "Family",
            "Friends",
            "Professional",
            "Personal",
            "Other"
        ]
    )

    budget = st.select_slider(
        "Your Budget (INR)",
        options=[
            500, 1000, 1500, 2000,
            3000, 5000, 10000
        ],
        value=2000,
        format_func=lambda x: f"₹{x:,}"
    )

    interests = st.multiselect(
        "Interests",
        [
            "Sweets & Chocolates",
            "Home Decoration",
            "Traditional Gifts",
            "Fashion & Accessories",
            "Technology",
            "Books",
            "Wellness",
            "Personalized Gifts",
            "Dry Fruits",
            "Handmade Gifts"
        ],
        default=[
            "Traditional Gifts",
            "Home Decoration"
        ]
    )

    gift_style = st.selectbox(
        "Preferred Gift Style",
        [
            "Traditional",
            "Modern",
            "Luxury",
            "Budget Friendly",
            "Personalized",
            "Creative & Unique"
        ]
    )

    additional_info = st.text_area(
        "Additional Preferences",
        placeholder="Example: Loves traditional decorations..."
    )

    generate = st.button(
        "✨ Generate AI Gift Ideas",
        type="primary",
        use_container_width=True
    )


# -----------------------------------------
# MAIN CONTENT
# -----------------------------------------

st.subheader("🪔 Find the Perfect Diwali Gift")

st.write(
    "Tell our AI assistant about your recipient "
    "and discover personalized gift recommendations "
    "with shopping options from multiple websites."
)

if generate:

    api_key = (
        os.getenv("GOOGLE_API_KEY")
        or os.getenv("GEMINI_API_KEY")
    )

    if not api_key:
        st.error(
            "Gemini API key not found. "
            "Please configure GOOGLE_API_KEY in your .env file."
        )

    elif not interests:
        st.warning("Please select at least one interest.")

    else:

        try:
            with st.spinner(
                "✨ Gemini AI is finding the perfect Diwali gifts..."
            ):

                result = generate_gift_recommendations(
                    api_key,
                    recipient,
                    relationship,
                    budget,
                    interests,
                    gift_style,
                    additional_info
                )

            gifts = result.get("gifts", [])

            if not gifts:
                st.warning("No gift recommendations were generated.")

            else:

                st.success(
                    f"Successfully generated {len(gifts)} gift ideas!"
                )

                st.divider()

                st.subheader("🎁 Personalized Gift Recommendations")

                st.caption(
                    "Prices are AI-generated estimates, not verified "
                    "live marketplace prices."
                )

                # Display gift cards
                for index, gift in enumerate(gifts, start=1):

                    name = gift.get("name", "Gift Recommendation")
                    query = gift.get("search_query") or name
                    links = shopping_links(query)

                    with st.container(border=True):

                        col1, col2 = st.columns([1, 4])

                        with col1:
                            st.markdown(
                                f"<h1 style='text-align:center;'>"
                                f"{gift.get('icon', '🎁')}</h1>",
                                unsafe_allow_html=True
                            )

                            st.caption(f"GIFT #{index}")

                        with col2:

                            st.markdown(
                                f'<div class="gift-heading">'
                                f'{name}</div>',
                                unsafe_allow_html=True
                            )

                            st.markdown(
                                f'<div class="price">'
                                f'💰 {gift.get("estimated_price", "Price unavailable")}'
                                f'</div>',
                                unsafe_allow_html=True
                            )

                            st.write(
                                gift.get("description", "")
                            )

                            st.markdown("**💡 Why this gift?**")
                            st.write(
                                gift.get("why_recommended", "")
                            )

                            st.markdown("**✨ Personalization idea**")
                            st.write(
                                gift.get("personalization", "")
                            )

                        st.markdown("#### 🛍️ Explore Products & Stores")

                        # Google shopping and search
                        c1, c2 = st.columns(2)

                        with c1:
                            st.link_button(
                                "🛒 Google Shopping",
                                links["Google Shopping"],
                                use_container_width=True
                            )

                        with c2:
                            st.link_button(
                                "🔎 Google Search",
                                links["Google Search"],
                                use_container_width=True
                            )

                        # Marketplace links
                        c1, c2, c3, c4 = st.columns(4)

                        with c1:
                            st.link_button(
                                "Amazon",
                                links["Amazon"],
                                use_container_width=True
                            )

                        with c2:
                            st.link_button(
                                "Flipkart",
                                links["Flipkart"],
                                use_container_width=True
                            )

                        with c3:
                            st.link_button(
                                "Myntra",
                                links["Myntra"],
                                use_container_width=True
                            )

                        with c4:
                            st.link_button(
                                "Meesho",
                                links["Meesho"],
                                use_container_width=True
                            )

                # ---------------------------------
                # GREETING
                # ---------------------------------

                st.divider()

                st.subheader("💌 Your Personalized Diwali Greeting")

                greeting = result.get(
                    "greeting",
                    "Wishing you a Happy and Prosperous Diwali!"
                )

                st.info(greeting)

                st.download_button(
                    "📥 Download Gift Recommendations",
                    data=json.dumps(
                        result,
                        indent=4,
                        ensure_ascii=False
                    ),
                    file_name="Diwali_Gift_Recommendations.json",
                    mime="application/json"
                )

        except json.JSONDecodeError:
            st.error(
                "Gemini returned an invalid JSON response. "
                "Please try again."
            )

        except Exception as e:
            st.error(f"AI Generation Error: {str(e)}")


# -----------------------------------------
# FOOTER
# -----------------------------------------

st.divider()

st.markdown(
    """
    <div class="footer">
        ✨ AI POWERED &nbsp; • &nbsp; Python &nbsp; • &nbsp;
        Streamlit &nbsp; • &nbsp; LangChain &nbsp; • &nbsp;
        Google Gemini
        <br><br>
        Developed by <b>Mandar Kurundwade</b>
        <br>
        DiwaliGift AI © 2026
    </div>
    """,
    unsafe_allow_html=True
)
