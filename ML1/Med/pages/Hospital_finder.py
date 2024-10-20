import streamlit as st
import networkx as nx
import folium
import requests
from geopy.distance import geodesic
from streamlit_folium import st_folium

# Define locations as nodes with coordinates
locations = {
    "Ambulance": (12.9616, 77.5946),
    "General Hospital": (12.9716, 77.5946),
    "Heart Care Center": (12.9260, 77.6762),
    "Neurology Specialty": (12.9367, 77.5992),
}

# Create a graph and add nodes with positions
graph = nx.Graph()
for location, coords in locations.items():
    graph.add_node(location, pos=coords)

# Add weighted edges (distances between nodes) using geopy
for loc1, coord1 in locations.items():
    for loc2, coord2 in locations.items():
        if loc1 != loc2:
            distance = geodesic(coord1, coord2).kilometers
            graph.add_edge(loc1, loc2, weight=distance)

# Streamlit App Layout
st.title("Ambulance Route Finder with Dijkstra's Algorithm")

# Display location dropdowns
start_location = st.selectbox("Select Ambulance Location", list(locations.keys()))
destination_type = st.selectbox("Select Hospital Type", ["General Hospital", "Cardiology", "Neurology"])

# Hospital Mapping (for simplicity, map destination type to actual hospital names)
hospital_mapping = {
    "General Hospital": "General Hospital",
    "Cardiology": "Heart Care Center",
    "Neurology": "Neurology Specialty"
}

# Initialize the session state for the map
if "map" not in st.session_state:
    st.session_state["map"] = None

def get_route(start_coords, end_coords):
    """Query the OSRM API to get a route that follows roads."""
    url = f"http://router.project-osrm.org/route/v1/driving/{start_coords[1]},{start_coords[0]};{end_coords[1]},{end_coords[0]}?overview=full&geometries=geojson"
    try:
        response = requests.get(url)
        data = response.json()
        if response.status_code == 200 and data["routes"]:
            return data["routes"][0]["geometry"]["coordinates"]
        else:
            st.error("Could not find a route using the OSRM API.")
            return None
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

if st.button("Find Shortest Route"):
    # Define start and destination nodes
    destination_location = hospital_mapping[destination_type]
    
    # Find shortest path using Dijkstra's algorithm
    try:
        shortest_path = nx.dijkstra_path(graph, source=start_location, target=destination_location, weight='weight')
        total_distance = nx.dijkstra_path_length(graph, source=start_location, target=destination_location, weight='weight')
        
        st.success(f"Shortest path found: {' -> '.join(shortest_path)} with total distance: {total_distance:.2f} km")
        
        # Visualize the map
        # Center map on the start location
        m = folium.Map(location=locations[start_location], zoom_start=12)
        
        # Add nodes to the map
        for loc in shortest_path:
            folium.Marker(
                location=locations[loc],
                tooltip=loc,
                icon=folium.Icon(color='green' if loc == destination_location else 'blue')
            ).add_to(m)
        
        # Draw lines between the nodes using actual road routes
        for i in range(len(shortest_path) - 1):
            start_coords = locations[shortest_path[i]]
            end_coords = locations[shortest_path[i + 1]]
            
            # Get the route between start and end coordinates using the OSRM API
            route = get_route(start_coords, end_coords)
            
            if route:
                # Convert the route into the format Folium expects (lat, lon)
                folium.PolyLine(
                    [(coord[1], coord[0]) for coord in route],
                    color='blue',
                    weight=5
                ).add_to(m)
        
        # Save the map in session_state to persist between reruns
        st.session_state["map"] = m

    except nx.NetworkXNoPath:
        st.error("No path found between the selected locations.")

# Display the persisted map if it exists
if st.session_state["map"]:
    st_folium(st.session_state["map"], width=900, height=600)
