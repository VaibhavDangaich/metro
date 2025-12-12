import streamlit as st
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import base64

def image_to_data_uri(image_path):
    with open(image_path, "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode("utf-8")
    return f"data:image/jpeg;base64,{encoded}"

load_dotenv()

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

model = ChatOpenAI(model_name="gpt-4o").with_structured_output(json_Schema)

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
        result = model.invoke({
            "source_station": source,
            "destination_station": destination
        })
        st.subheader("Route Suggestion:")
        st.markdown(f"**From:** {result.get('source_station')}")
        st.markdown(f"**To:** {result.get('destination_station')}")
        # Show line color as a colored line
        color_map = {
            "blue": "#0074D9",
            "green": "#2ECC40",
            "purple": "#B10DC9",
            "yellow": "#FFDC00",
            "orange": "#FF851B",
            "pink": "#F012BE"
        }
        line_color = result.get('line_color', '').lower()
        if line_color in color_map:
            st.markdown(f'<hr style="height:8px;border:none;background:{color_map[line_color]};margin:10px 0;">', unsafe_allow_html=True)
            st.markdown(f"**Line Color:** <span style='color:{color_map[line_color]};font-weight:bold'>{line_color.title()}</span>", unsafe_allow_html=True)
        elif line_color:
            st.markdown(f"**Line Color:** {line_color.title()}")
        # Show any additional info from the model
        for k, v in result.items():
            if k not in ["source_station", "destination_station", "line_preference", "allow_interchange", "response_language", "line_color"]:
                st.markdown(f"**{k.replace('_', ' ').title()}:** {v}")

