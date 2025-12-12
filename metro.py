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

json_Schema = {
    "title": "MetroRoute",
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
                "North South Line", "East West Line", "Southwestern (Joka) Line",
                "Newtown (Airport) Line", "Eastern (Barasat) Line",
                "Northern (Barrackpore) Line", "fastest", "least interchanges", "any"
            ],
            "description": "Preferred metro line or route type."
        },
        "line_color": {
            "type": "string",
            "enum": ["blue", "green", "purple", "yellow", "orange", "pink"],
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

model = ChatOpenAI(model_name="gpt-4o", temperature=0).with_structured_output(json_Schema)

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
                        "text": f"Find the best route from {source} to {destination}. Return the details in JSON format matching the schema."
                    },
                    {
                        "type": "image_url", 
                        "image_url": {"url": image_data_uri}
                    }
                ]
            )
            
            try:
                result = model.invoke([message])
                
                st.subheader("Route Suggestion:")
                st.markdown(f"**From:** {result.get('source_station')}")
                st.markdown(f"**To:** {result.get('destination_station')}")
                
                color_map = {
                    "blue": "#0074D9", "green": "#2ECC40", "purple": "#B10DC9",
                    "yellow": "#FFDC00", "orange": "#FF851B", "pink": "#F012BE"
                }
                line_color = result.get('line_color', '').lower()
                
                if line_color in color_map:
                    st.markdown(f'<hr style="height:8px;border:none;background:{color_map[line_color]};margin:10px 0;">', unsafe_allow_html=True)
                    st.markdown(f"**Line Color:** <span style='color:{color_map[line_color]};font-weight:bold'>{line_color.title()}</span>", unsafe_allow_html=True)
                elif line_color:
                    st.markdown(f"**Line Color:** {line_color.title()}")
                
                ignore_keys = ["source_station", "destination_station", "line_preference", 
                               "allow_interchange", "response_language", "line_color"]
                
                for k, v in result.items():
                    if k not in ignore_keys:
                        st.markdown(f"**{k.replace('_', ' ').title()}:** {v}")
                        
            except Exception as e:
                st.error(f"An error occurred: {e}")
