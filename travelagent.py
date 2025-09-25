import streamlit as st
import json
import os
import requests
from agno.agent import Agent
from agno.tools.serpapi import SerpApiTools
from agno.models.google import Gemini
from datetime import datetime

# Set up Streamlit UI with a travel-friendly theme
st.set_page_config(page_title="🌍 AI Travel Planner", layout="wide")
st.markdown(
    """
    <style>
        .title {
            text-align: center;
            font-size: 36px;
            font-weight: bold;
            color: #ff5733;
        }
        .subtitle {
            text-align: center;
            font-size: 20px;
            color: #555;
        }
        .stSlider > div {
            background-color: #f9f9f9;
            padding: 10px;
            border-radius: 10px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Title and subtitle
st.markdown('<h1 class="title">✈️ AI-Powered Travel Planner</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Plan your dream trip with AI! Get personalized recommendations for flights, hotels, and activities.</p>', unsafe_allow_html=True)

# User Inputs Section
st.markdown("### 🌍 Where are you headed?")
source = st.text_input("🛫 Departure City (IATA Code):", "BOM")  # Example: BOM for Mumbai
destination = st.text_input("🛬 Destination (IATA Code):", "DEL")  # Example: DEL for Delhi

st.markdown("### 📅 Plan Your Adventure")
num_days = st.slider("🕒 Trip Duration (days):", 1, 14, 5)
travel_theme = st.selectbox(
    "🎭 Select Your Travel Theme:",
    ["💑 Couple Getaway", "👨‍👩‍👧‍👦 Family Vacation", "🏔️ Adventure Trip", "🧳 Solo Exploration"]
)

# Divider for aesthetics
st.markdown("---")

st.markdown(
    f"""
    <div style="
        text-align: center; 
        padding: 15px; 
        background-color: #ffecd1; 
        border-radius: 10px; 
        margin-top: 20px;
    ">
        <h3>🌟 Your {travel_theme} to {destination} is about to begin! 🌟</h3>
        <p>Let's find the best flights, stays, and experiences for your unforgettable journey.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

def format_datetime(iso_string):
    try:
        dt = datetime.strptime(iso_string, "%Y-%m-%d %H:%M")
        return dt.strftime("%b-%d, %Y | %I:%M %p")  # Example: Mar-06, 2025 | 6:20 PM
    except:
        return "N/A"

activity_preferences = st.text_area(
    "🌍 What activities do you enjoy? (e.g., relaxing on the beach, exploring historical sites, nightlife, adventure)",
    "Relaxing on the beach, exploring historical sites"
)

departure_date = st.date_input("Departure Date")
return_date = st.date_input("Return Date")

# Sidebar Setup
st.sidebar.title("🌎 Travel Assistant")
st.sidebar.subheader("Personalize Your Trip")

# Travel Preferences
budget = st.sidebar.radio("💰 Budget Preference:", ["Economy", "Standard", "Luxury"])
flight_class = st.sidebar.radio("✈️ Flight Class:", ["Economy", "Business", "First Class"])
hotel_rating = st.sidebar.selectbox("🏨 Preferred Hotel Rating:", ["Any", "3⭐", "4⭐", "5⭐"])

# Packing Checklist
st.sidebar.subheader("🎒 Packing Checklist")
packing_list = {
    "👕 Clothes": True,
    "🩴 Comfortable Footwear": True,
    "🕶️ Sunglasses & Sunscreen": False,
    "📖 Travel Guidebook": False,
    "💊 Medications & First-Aid": True
}
for item, checked in packing_list.items():
    st.sidebar.checkbox(item, value=checked)

# Travel Essentials
st.sidebar.subheader("🛂 Travel Essentials")
visa_required = st.sidebar.checkbox("🛃 Check Visa Requirements")
travel_insurance = st.sidebar.checkbox("🛡️ Get Travel Insurance")
currency_converter = st.sidebar.checkbox("💱 Currency Exchange Rates")

SERPAPI_KEY = "297ceeab91a57e9c6644536c9d6addbd86f6da82f44fba2fcba97dce8148ebb2"
GOOGLE_API_KEY = "AIzaSyA-i0mbqZRTXHpZ0Drrd0DQP3S81FPrVYg"
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

# Function to fetch flight data using SerpAPI
def fetch_flights(source, destination, departure_date, return_date):
    params = {
        "engine": "google_flights",
        "departure_id": source,
        "arrival_id": destination,
        "outbound_date": str(departure_date),
        "return_date": str(return_date),
        "currency": "INR",
        "hl": "en",
        "api_key": SERPAPI_KEY
    }
    
    try:
        # Using requests to call SerpAPI directly
        api_url = "https://serpapi.com/search"
        response = requests.get(api_url, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Error fetching flight data: {str(e)}")
        return None

# Function to extract top 3 cheapest flights
def extract_cheapest_flights(flight_data):
    if not flight_data:
        return []
    
    best_flights = flight_data.get("best_flights", [])
    # Safely extract price and sort
    sorted_flights = []
    for flight in best_flights:
        price = flight.get("price", 0)
        # Convert price to integer if it's a string
        if isinstance(price, str):
            try:
                price = int(price.replace('₹', '').replace(',', '').strip())
            except:
                price = float('inf')
        sorted_flights.append((flight, price))
    
    sorted_flights.sort(key=lambda x: x[1])
    return [flight for flight, _ in sorted_flights[:3]]

# Function to create mock flight data for demo purposes
def create_mock_flight_data():
    return {
        "best_flights": [
            {
                "airline": "Air India",
                "airline_logo": "https://via.placeholder.com/100x50.png?text=Air+India",
                "price": "₹8,500",
                "total_duration": "120",
                "flights": [
                    {
                        "departure_airport": {"time": "2025-03-06 06:20"},
                        "arrival_airport": {"time": "2025-03-06 08:20"},
                        "airline": "Air India"
                    }
                ],
                "departure_token": "mock_token_1"
            },
            {
                "airline": "IndiGo",
                "airline_logo": "https://via.placeholder.com/100x50.png?text=IndiGo",
                "price": "₹7,200",
                "total_duration": "135",
                "flights": [
                    {
                        "departure_airport": {"time": "2025-03-06 14:30"},
                        "arrival_airport": {"time": "2025-03-06 16:45"},
                        "airline": "IndiGo"
                    }
                ],
                "departure_token": "mock_token_2"
            },
            {
                "airline": "Vistara",
                "airline_logo": "https://via.placeholder.com/100x50.png?text=Vistara",
                "price": "₹9,800",
                "total_duration": "125",
                "flights": [
                    {
                        "departure_airport": {"time": "2025-03-06 09:15"},
                        "arrival_airport": {"time": "2025-03-06 11:20"},
                        "airline": "Vistara"
                    }
                ],
                "departure_token": "mock_token_3"
            }
        ]
    }

# AI Agents
researcher = Agent(
    name="Researcher",
    instructions=[
        "Identify the travel destination specified by the user.",
        "Gather detailed information on the destination, including climate, culture, and safety tips.",
        "Find popular attractions, landmarks, and must-visit places.",
        "Search for activities that match the user's interests and travel style.",
        "Prioritize information from reliable sources and official travel guides.",
        "Provide well-structured summaries with key insights and recommendations."
    ],
    model=Gemini(id="gemini-2.0-flash-exp"),
    tools=[SerpApiTools(api_key=SERPAPI_KEY)],
)

planner = Agent(
    name="Planner",
    instructions=[
        "Gather details about the user's travel preferences and budget.",
        "Create a detailed itinerary with scheduled activities and estimated costs.",
        "Ensure the itinerary includes transportation options and travel time estimates.",
        "Optimize the schedule for convenience and enjoyment.",
        "Present the itinerary in a structured format."
    ],
    model=Gemini(id="gemini-2.0-flash-exp"),
)

hotel_restaurant_finder = Agent(
    name="Hotel & Restaurant Finder",
    instructions=[
        "Identify key locations in the user's travel itinerary.",
        "Search for highly rated hotels near those locations.",
        "Search for top-rated restaurants based on cuisine preferences and proximity.",
        "Prioritize results based on user preferences, ratings, and availability.",
        "Provide direct booking links or reservation options where possible."
    ],
    model=Gemini(id="gemini-2.0-flash-exp"),
    tools=[SerpApiTools(api_key=SERPAPI_KEY)],
)

# Generate Travel Plan
if st.button("🚀 Generate Travel Plan"):
    use_mock_data = st.checkbox("Use mock data (if real API fails)", value=True)
    
    with st.spinner("✈️ Fetching best flight options..."):
        if use_mock_data:
            flight_data = create_mock_flight_data()
            st.info("📊 Using mock flight data for demonstration")
        else:
            flight_data = fetch_flights(source, destination, departure_date, return_date)
        
        if flight_data:
            cheapest_flights = extract_cheapest_flights(flight_data)
        else:
            cheapest_flights = []
            st.error("Failed to fetch flight data. Using mock data instead.")
            flight_data = create_mock_flight_data()
            cheapest_flights = extract_cheapest_flights(flight_data)

    # AI Processing
    with st.spinner("🔍 Researching best attractions & activities..."):
        research_prompt = (
            f"Research the best attractions and activities in {destination} for a {num_days}-day {travel_theme.lower()} trip. "
            f"The traveler enjoys: {activity_preferences}. Budget: {budget}. Flight Class: {flight_class}. "
            f"Hotel Rating: {hotel_rating}. Visa Requirement: {visa_required}. Travel Insurance: {travel_insurance}."
        )
        try:
            research_results = researcher.run(research_prompt, stream=False)
        except Exception as e:
            st.error(f"Research failed: {str(e)}")
            research_results = type('obj', (object,), {'content': 'Research content unavailable due to API limitations.'})

    with st.spinner("🏨 Searching for hotels & restaurants..."):
        hotel_restaurant_prompt = (
            f"Find the best hotels and restaurants near popular attractions in {destination} for a {travel_theme.lower()} trip. "
            f"Budget: {budget}. Hotel Rating: {hotel_rating}. Preferred activities: {activity_preferences}."
        )
        try:
            hotel_restaurant_results = hotel_restaurant_finder.run(hotel_restaurant_prompt, stream=False)
        except Exception as e:
            st.error(f"Hotel search failed: {str(e)}")
            hotel_restaurant_results = type('obj', (object,), {'content': 'Hotel and restaurant information unavailable due to API limitations.'})

    with st.spinner("🗺️ Creating your personalized itinerary..."):
        planning_prompt = (
            f"Based on the following data, create a {num_days}-day itinerary for a {travel_theme.lower()} trip to {destination}. "
            f"The traveler enjoys: {activity_preferences}. Budget: {budget}. Flight Class: {flight_class}. Hotel Rating: {hotel_rating}. "
            f"Visa Requirement: {visa_required}. Travel Insurance: {travel_insurance}. Research: {getattr(research_results, 'content', 'No research data')}. "
            f"Flights: {json.dumps(cheapest_flights) if cheapest_flights else 'No flight data'}. Hotels & Restaurants: {getattr(hotel_restaurant_results, 'content', 'No hotel data')}."
        )
        try:
            itinerary = planner.run(planning_prompt, stream=False)
        except Exception as e:
            st.error(f"Itinerary creation failed: {str(e)}")
            itinerary = type('obj', (object,), {'content': 'Itinerary creation failed due to API limitations. Please try again later.'})

    # Display Results
    st.subheader("✈️ Cheapest Flight Options")
    if cheapest_flights:
        cols = st.columns(len(cheapest_flights))
        for idx, flight in enumerate(cheapest_flights):
            with cols[idx]:
                airline_logo = flight.get("airline_logo", "https://via.placeholder.com/100x50.png?text=Airline")
                airline_name = flight.get("airline", "Unknown Airline")
                price = flight.get("price", "Not Available")
                total_duration = flight.get("total_duration", "N/A")
                
                flights_info = flight.get("flights", [{}])
                departure = flights_info[0].get("departure_airport", {}) if flights_info else {}
                arrival = flights_info[-1].get("arrival_airport", {}) if flights_info else {}
                
                departure_time = format_datetime(departure.get("time", "N/A"))
                arrival_time = format_datetime(arrival.get("time", "N/A"))
                
                # Simple booking link (mock)
                booking_link = "https://www.google.com/travel/flights"

                # Flight card layout
                st.markdown(
                    f"""
                    <div style="
                        border: 2px solid #ddd; 
                        border-radius: 10px; 
                        padding: 15px; 
                        text-align: center;
                        box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
                        background-color: #f9f9f9;
                        margin-bottom: 20px;
                    ">
                        <img src="{airline_logo}" width="100" alt="Flight Logo" />
                        <h3 style="margin: 10px 0;">{airline_name}</h3>
                        <p><strong>Departure:</strong> {departure_time}</p>
                        <p><strong>Arrival:</strong> {arrival_time}</p>
                        <p><strong>Duration:</strong> {total_duration} min</p>
                        <h2 style="color: #008000;">💰 {price}</h2>
                        <a href="{booking_link}" target="_blank" style="
                            display: inline-block;
                            padding: 10px 20px;
                            font-size: 16px;
                            font-weight: bold;
                            color: #fff;
                            background-color: #007bff;
                            text-decoration: none;
                            border-radius: 5px;
                            margin-top: 10px;
                        ">🔗 Book Now</a>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    else:
        st.warning("⚠️ No flight data available.")

    st.subheader("🏨 Hotels & Restaurants")
    st.write(getattr(hotel_restaurant_results, 'content', 'No hotel data available'))

    st.subheader("🗺️ Your Personalized Itinerary")
    st.write(getattr(itinerary, 'content', 'No itinerary available'))

    st.success("✅ Travel plan generated successfully!")
