import streamlit as st
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import base64

def image_to_data_uri(image_path):
    with open(image_path, "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode("utf-8")
    return f"data:image/jpeg;base64,{encoded}"

load_dotenv()

model = ChatOpenAI(model_name="gpt-4o")

json_Schema = {
    "type": "object",
    "properties": {
        "source_station": {
            "type": "string",
            "description": "Name of the starting metro station."
        },
        "destination_station": {
            "type": "string",
            "description": "Name of the destination metro station."
        },
        "line_preference": {
            "type": "string",
            "enum": [
                "North South Line",
                "East West Line",
                "Southwestern (Joka) Line",
                "Newtown (Airport) Line",
                "Eastern (Barasat) Line",
                "Northern (Barrackpore) Line",
                "fastest",
                "least interchanges",
                "any"
            ],
            "description": "Preferred metro line or route type."
        },
        "line_color": {
            "type": "string",
            "enum": [
                "blue",
                "green",
                "purple",
                "yellow",
                "orange",
                "pink"
            ],
            "description": "Color of the metro route line as per the map legend."
        },
        "allow_interchange": {
            "type": "boolean",
            "default": True,
            "description": "Whether interchanges are allowed."
        },
        "response_language": {
            "type": "string",
            "description": "Preferred language for the response."
        }
    },
    "required": ["source_station", "destination_station"]
}

st.header('Metro Guide')
st.image("metro.jpeg", caption="Kolkata Metro Map", use_column_width=True)

stations = [
    # North South Line (Blue)
    "Dakineshwar", "Baranagar", "Dum Dum", "Belgachia", "Shyambazar", "Sovabazar Sutanuti", "Girish Park", "M.G. Road", "Central Station", "Chandni Chowk", "Esplanade", "Park Street", "Maidan", "Rabindra Sadan", "Netaji Bhawan", "Jatin Das Park", "Kalighat", "Rabindra Sarobar", "Mahanayak U.K.", "Netaji", "Masterda Surysen", "Gitanjali", "Kavi Nazrul", "Sahid Khudiram", "Kavi Subash",
    # East West Line (Green)
    "Howrah Maidan", "Howrah", "Mahakaran", "Esplanade", "Sealdah", "Phoolbagan", "Salt Lake Stadium", "Bengal Chemical", "City Center", "Central Park", "Karunamoyee", "Salt Lake Sector V",
    # Southwestern (Joka) Line (Purple)
    "Joka", "Thakurpukur", "Sakherbazar", "Behala Chowrasta", "Behala Bazar", "Taratala", "Majerhat", "Mominpur", "Kidderpore", "Victoria", "Diamond Park", "IIM",
    # Newtown (Airport) Line (Yellow)
    "Baranagar", "Dum Dum", "Jessore Road", "Biman Bandar", "Birati", "Michael Nagar", "New Barrackpore", "Madhyamgram", "Hridaypur", "Barasat",
    # Eastern (Barasat) Line (Orange)
    "Dakineshwar", "Baranagar", "Dum Dum", "V.I.P Road", "Chinar Park", "City Center 2 (CC2)", "Mangal Deep", "Eco Park", "Mother's Wax Museum", "Convention Center", "Siksha Tirtha", "Swapno Bhor", "Nabadiganta", "Nazul Tirtha", "Salt Lake Sector V", "Nalban", "Gour Kishore Ghosh", "Beleghata", "Barun Sengupta", "Ritwik Ghatak", "V.I.P. Bazar", "Hemanta M.", "Kavi Sukanta",
    # Northern (Barrackpore) Line (Pink)
    "Panihati", "Sodepur", "Agarpara", "Kamarhati", "Nopara", "Cantonment", "Jessore Road", "Biman Bandar", "Birati", "Michael Nagar", "New Barrackpore", "Madhyamgram", "Hridaypur", "Barasat", "Tala Gate", "Titagarh", "Talpukur", "Barrackpore"
]

source = st.selectbox("Select Source Station", stations)
destination = st.selectbox("Select Destination Station", stations)

if st.button("Find Route"):
    with st.spinner("Finding best route..."):
        image_data_uri = image_to_data_uri("metro.jpeg")
        result = model.invoke([
    {
        "role": "user",
        "content": [
            {"type": "text", "text": f"What is the best route from {source} to {destination}? Also mention the line color."},
            {
                "type": "image_url", 
                "image_url": {
                    "url": image_data_uri,
                    "detail": "high"
                }
            }
        ]
    }
])
    st.subheader("Route Suggestion:")
    st.write(result.content)

