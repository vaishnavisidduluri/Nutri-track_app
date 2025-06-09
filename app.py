import streamlit as st
import requests
import plotly.express as px

# ----- Nutrient Mapping -----
NUTRIENT_KEYS = {
    "Energy": "Calories (kcal)",
    "Protein": "Protein (g)",
    "Total lipid (fat)": "Fat (g)",
    "Carbohydrate, by difference": "Carbohydrates (g)",
    "Sugars, total including NLEA": "Sugars (g)",
    "Fiber, total dietary": "Fiber (g)"
}

# ----- Get Nutrition Function -----
def get_nutrition(food_name, api_key):
    url = f"https://api.nal.usda.gov/fdc/v1/foods/search?query={food_name}&pageSize=1&api_key={api_key}"
    response = requests.get(url)
    if response.status_code != 200:
        return None
    data = response.json()
    if "foods" in data and len(data["foods"]) > 0:
        food = data["foods"][0]
        nutrients = {
            NUTRIENT_KEYS[n['nutrientName']]: n['value']
            for n in food.get('foodNutrients', [])
            if n['nutrientName'] in NUTRIENT_KEYS
        }
        return {
            "Description": food.get("description", food_name.title()),
            **nutrients
        }
    return None

# ----- Page Config -----
st.set_page_config(page_title="NutriTrack 🍎", layout="centered")

# ----- Custom CSS -----
st.markdown("""
    <style>
    body {
        background-color: #fdf6f0;
        font-family: 'Segoe UI', sans-serif;
    }
    .stApp {
        background-color: #fdf6f0;
        color: #2b2d42;
    }
    h1, h2, h3 {
        color: #6a0572;
    }
    label {
        color: black !important;
    }
    input::placeholder {
        color: black !important;
        opacity: 1;
    }
    .stTextInput>div>div>input {
        background-color: #fff;
        padding: 10px;
        border: 1px solid #ccc;
        border-radius: 10px;
        color: #2b2d42;
    }
    .stButton>button {
        background-color: #da9f93;
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.5em 1.2em;
        font-weight: bold;
        transition: background 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #b3758d;
        color: #fff;
    }
    .element-container:has(.stPlotlyChart) {
        background-color: #fff;
        border-radius: 15px;
        padding: 1.5em;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    .stDataFrame {
        background-color: white;
        border-radius: 12px;
        padding: 10px;
        font-size: 16px;
    }
    </style>
""", unsafe_allow_html=True)

# ----- App Header -----
st.title("🥗 NutriTrack: Smart Nutrition Explorer")
st.markdown("Welcome to **NutriTrack** – a tool to explore the nutritional value of your favorite foods.")

# ----- Input -----
food_input = st.text_input("🔍 Enter food items", placeholder="e.g., apple, bread, paneer")

# ----- Search Button -----
if st.button("✨ Analyze"):
    if food_input.strip():
        api_key = st.secrets["api_key"] if "api_key" in st.secrets else "HYgXx4w7LOvXAV6rQXCu7BP6FMCo5rAK2fELjfco"
        food_items = [item.strip() for item in food_input.split(",") if item.strip()]
        all_results = []
        totals = {label: 0 for label in NUTRIENT_KEYS.values()}

        with st.spinner("Fetching nutrition data..."):
            for food in food_items:
                result = get_nutrition(food, api_key)
                if result:
                    all_results.append(result)
                    for k, v in result.items():
                        if k in totals:
                            totals[k] += v

        if all_results:
            st.subheader("📋 Nutritional Summary")
            for res in all_results:
                st.markdown(f"**✅ {res['Description']}**")
                st.write({k: v for k, v in res.items() if k != "Description"})

            st.subheader("🧾 Total Combined Nutrition")
            st.dataframe(totals, use_container_width=True)

            fig = px.pie(
                names=[k for k in totals if k != "Calories (kcal)"],
                values=[v for k, v in totals.items() if k != "Calories (kcal)"],
                title="🥧 Macronutrient + Sugar/Fiber Breakdown",
                color_discrete_sequence=px.colors.sequential.RdPu
            )
            fig.update_traces(textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("❌ No data found. Please try other food items.")
    else:
        st.warning("⚠️ Please enter at least one food item.")

# ----- Footer -----
st.markdown("---")
st.caption("🍃 Built with ❤️ using Streamlit")
