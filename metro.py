import streamlit as st
import os
import base64
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

load_dotenv()

if "OPENAI_API_KEY" in st.secrets:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

def image_to_data_uri(image_path):
    if not os.path.exists(image_path):
        st.error(f"Image not found: {image_path}")
        return None
        
    with open(image_path, "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode("utf-8")
    return f"data:image/jpeg;base64,{encoded}"

# UPDATED SCHEMA: Supports multiple segments with different colors
json_Schema = {
    "title": "MetroRoute",
    "type": "object",
    "properties": {
        "source_station": {"type": "string"},
        "destination_station": {"type": "string"},
        "total_stations": {"type": "integer"},
        "estimated_time_minutes": {"type": "integer"},
        "route_segments": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "start_station": {"type": "string"},
                    "end_station": {"type": "string"},
                    "line_color": {
                        "type": "string",
                        "enum": ["blue", "green", "purple", "yellow", "orange", "pink"]
                    },
                    "instructions": {"type": "string", "description": "e.g., 'Take Blue Line towards Kavi Subash'"}
                },
                "required": ["start_station", "end_station", "line_color", "instructions"]
            }
        }
    },
    "required": ["source_station", "destination_station", "route_segments"]
}

model = ChatOpenAI(model_name="o3", temperature=0).with_structured_output(json_Schema)

st.header('Metro Guide')

image_path = "metro.jpeg"
if os.path.exists(image_path):
    st.image(image_path, caption="Kolkata Metro Map", use_column_width=True)
else:
    st.warning("metro.jpeg not found.")

stations = [
    "Dakineshwar", "Baranagar", "Dum Dum", "Belgachia", "Shyambazar", "Sovabazar Sutanuti", "Girish Park", "M.G. Road", "Central Station", "Chandni Chowk", "Esplanade", "Park Street", "Maidan", "Rabindra Sadan", "Netaji Bhawan", "Jatin Das Park", "Kalighat", "Rabindra Sarobar", "Mahanayak U.K.", "Netaji", "Masterda Surysen", "Gitanjali", "Kavi Nazrul", "Sahid Khudiram", "Kavi Subash",
    "Howrah Maidan", "Howrah", "Mahakaran", "Esplanade", "Sealdah", "Phoolbagan", "Salt Lake Stadium", "Bengal Chemical", "City Center", "Central Park", "Karunamoyee", "Salt Lake Sector V",
    "Joka", "Thakurpukur", "Sakherbazar", "Behala Chowrasta", "Behala Bazar", "Taratala", "Majerhat", "Mominpur", "Kidderpore", "Victoria", "Diamond Park", "IIM",
    "Baranagar", "Dum Dum", "Jessore Road", "Biman Bandar", "Birati", "Michael Nagar", "New Barrackpore", "Madhyamgram", "Hridaypur", "Barasat",
    "Dakineshwar", "Baranagar", "Dum Dum", "V.I.P Road", "Chinar Park", "City Center 2 (CC2)", "Mangal Deep", "Eco Park", "Mother's Wax Museum", "Convention Center", "Siksha Tirtha", "Swapno Bhor", "Nabadiganta", "Nazul Tirtha", "Salt Lake Sector V", "Nalban", "Gour Kishore Ghosh", "Beleghata", "Barun Sengupta", "Ritwik Ghatak", "V.I.P. Bazar", "Hemanta M.", "Kavi Sukanta",
    "Panihati", "Sodepur", "Agarpara", "Kamarhati", "Nopara", "Cantonment", "Jessore Road", "Biman Bandar", "Birati", "Michael Nagar", "New Barrackpore", "Madhyamgram", "Hridaypur", "Barasat", "Tala Gate", "Titagarh", "Talpukur", "Barrackpore"
]

source = st.selectbox("Select Source Station", stations)
destination = st.selectbox("Select Destination Station", stations)

color_map = {
    "blue": "#0074D9", "green": "#2ECC40", "purple": "#B10DC9",
    "yellow": "#FFDC00", "orange": "#FF851B", "pink": "#F012BE"
}

if st.button("Find Route"):
    if not os.path.exists(image_path):
        st.error("Cannot proceed: Map image missing.")
    else:
        with st.spinner("Finding best route..."):
            image_data_uri = image_to_data_uri(image_path)
            
            message = HumanMessage(
                content=[
                    {
                        "type": "text", 
                        "text": f"Find the best route from {source} to {destination}. If there is a line change, split the route into segments. Return JSON."
                    },
                    {
                        "type": "image_url", 
                        "image_url": {"url": image_data_uri}
                    }
                ]
            )
            
            try:
                result = model.invoke([message])
                
                st.subheader("Route Plan")
                st.markdown(f"**From:** {result.get('source_station')}  ➡️  **To:** {result.get('destination_station')}")
                
                if 'total_stations' in result:
                    st.caption(f"Total Stations: {result['total_stations']} | Est. Time: {result.get('estimated_time_minutes', '?')} mins")
                
                segments = result.get('route_segments', [])
                
                for i, segment in enumerate(segments):
                    line_color = segment.get('line_color', '').lower()
                    hex_color = color_map.get(line_color, '#808080')
                    
                    with st.container():
                        st.markdown(f"#### Step {i+1}: {segment.get('start_station')} to {segment.get('end_station')}")
                        st.markdown(f'<div style="background-color:{hex_color};padding:4px 10px;border-radius:5px;color:white;font-weight:bold;width:fit-content;margin-bottom:5px;">{line_color.upper()} LINE</div>', unsafe_allow_html=True)
                        st.write(segment.get('instructions'))
                        
                        if i < len(segments) - 1:
                            st.markdown("**⬇️ CHANGE TRAIN**")
                            
            except Exception as e:
                st.error(f"An error occurred: {e}")
