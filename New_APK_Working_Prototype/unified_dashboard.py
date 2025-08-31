import streamlit as st
import sys
import os


# Set page config
st.set_page_config(
    page_title="Fake APK Detector - Unified Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .feature-card {
        padding: 20px;
        border-radius: 10px;
        background-color: #f8f9fa;
        border-left: 5px solid #1f77b4;
        margin-bottom: 20px;
    }
    .app-container {
        max-width: 1200px;
        margin: 0 auto;
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown('<h1 class="main-header">🛡️ Fake APK Detector for Banking Apps</h1>', unsafe_allow_html=True)

# Introduction
st.success("""
**Welcome to the complete Fake APK Detection Platform!** This unified dashboard brings together:
- **Web Application** (Streamlit)
- **Mobile App Interface** (Simulated)
- **Backend API Console** (Simulated)
""")

# Create tabs for different components
tab1, tab2, tab3, tab4 = st.tabs(["Web App", "Mobile Preview", "API Console", "Crime Network"])
# Add role selection at the top (before tabs)
st.sidebar.header("Select Dashboard View")
user_role = st.sidebar.radio("Choose your role:", ["User", "Police Officer"])

# Create different tabs based on role
if user_role == "User":
    # User dashboard tabs
    tab1, tab2 = st.tabs(["Web App", "Mobile Preview"])
else:
    # Police dashboard tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Web App", "Mobile Preview", "API Console", "Crime Network"])

with tab1:
    st.header("🌐 Web Application Interface")
    st.info("This is the  web application for APK analysis")
    
    # Import and run your existing Streamlit app
    try:
        from Festival_linguistic import main as streamlit_main
        streamlit_main()
    except Exception as e:
        st.warning("Could not load full Streamlit app. Showing simplified interface.")
        st.write("**APK Analysis would appear here**")
        st.write("**User authentication would be here**")
        st.write("**Results visualization would be here**")

with tab2:
    st.header("📱 Mobile App Preview")
    st.info("Simulated mobile app interface for APK detection")
    
    # Create a mobile device frame simulation
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Mobile device frame
        st.markdown("""
        <div style="border: 3px solid #333; border-radius: 30px; padding: 20px; background-color: #000; 
                    width: 300px; height: 600px; margin: 0 auto; position: relative;">
            <div style="background-color: #fff; border-radius: 25px; height: 100%; padding: 10px; 
                        overflow-y: auto;">
                <h4 style="text-align: center; margin-top: 10px;">Fake APK Detector Mobile</h4>
                <div style="text-align: center; margin: 20px 0;">
                    <button style="background-color: #4285f4; color: white; border: none; 
                                 padding: 10px 20px; border-radius: 5px; margin: 5px;">
                        Scan APK File
                    </button>
                    <button style="background-color: #34a853; color: white; border: none; 
                                 padding: 10px 20px; border-radius: 5px; margin: 5px;">
                        Verify Bank Account
                    </button>
                    <button style="background-color: #ea4335; color: white; border: none; 
                                 padding: 10px 20px; border-radius: 5px; margin: 5px;">
                        Check URL Safety
                    </button>
                </div>
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 10px; margin: 10px 0;">
                    <h5>Recent Scans</h5>
                    <p>• HDFC Bank App - ✅ Safe</p>
                    <p>• UPI Payment App - ⚠️ Suspicious</p>
                    <p>• Diwali Cashback - ❌ Dangerous</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

with tab3:
    st.header("🔧 Backend API Console")
    st.info("Simulated backend API interface")
    
    # API console simulation
    st.subheader("API Endpoints")
    
    endpoints = [
        {"method": "POST", "path": "/api/v1/analyze-apk", "description": "Analyze APK file"},
        {"method": "POST", "path": "/api/v1/analyze-url", "description": "Check URL safety"},
        {"method": "POST", "path": "/api/v1/verify-bank", "description": "Verify bank account"},
        {"method": "GET", "path": "/api/v1/crime-network", "description": "Get crime network data"}
    ]
    
    for endpoint in endpoints:
        st.code(f"{endpoint['method']} {endpoint['path']} - {endpoint['description']}")
    
    # Simulated API request/response
    st.subheader("Simulate API Request")
    
    api_choice = st.selectbox("Select endpoint to test:", 
                             ["Analyze APK", "Check URL", "Verify Bank", "Crime Network"])
    
    if st.button("Send Test Request"):
        st.success("✅ API Request Successful!")
        st.json({
            "status": "success",
            "data": {
                "verdict": "⚠️ Suspicious",
                "risk_score": 65,
                "details": "This is a simulated API response"
            }
        })
# Remove the tab4 from the user view and only show it in police view
if user_role == "Police Officer":
    with tab4:
        st.header("🌍 Crime Network Visualization")
        st.info("Geographical analysis of fake APK sources across India")
        
        # Import and use your crime network functions
        try:
            from Festival_linguistic import show_crime_network_dashboard
            show_crime_network_dashboard()
        except Exception as e:
            st.warning("Could not load crime network visualization. Showing sample map.")
            
            # Show sample map
            import folium
            from streamlit_folium import folium_static
            
            # Create a simple India map
            india_map = folium.Map(location=[20.5937, 78.9629], zoom_start=5)
            
            # Add some sample markers
            cities = [
                {"name": "Mumbai", "lat": 19.0760, "lon": 72.8777, "cases": 45},
                {"name": "Delhi", "lat": 28.6139, "lon": 77.2090, "cases": 38},
                {"name": "Bangalore", "lat": 12.9716, "lon": 77.5946, "cases": 28}
            ]
            
            for city in cities:
                folium.CircleMarker(
                    location=[city['lat'], city['lon']],
                    radius=city['cases'] / 2,
                    popup=f"{city['name']}: {city['cases']} cases",
                    color='red',
                    fill=True,
                    fillColor='red'
                ).add_to(india_map)
            
            folium_static(india_map)
        # Fraud prediction section
        st.subheader("📊 Fraud Prediction Analysis")
        
        # Sample prediction data (replace with your actual prediction logic)
        predicted_areas = [
            {"area": "Mumbai Suburbs", "risk_score": 85, "reason": "Recent spike in fake loan apps"},
            {"area": "Hyderabad Tech Corridor", "risk_score": 72, "reason": "New phishing campaign detected"},
            {"area": "Delhi NCR", "risk_score": 68, "reason": "Increased reports of banking fraud"}
        ]
        
        st.write("**Next predicted areas for fraud:**")
        for area in predicted_areas:
            risk_color = "red" if area["risk_score"] > 75 else "orange" if area["risk_score"] > 60 else "blue"
            st.markdown(f"""
            <div style="border-left: 4px solid {risk_color}; padding-left: 10px; margin: 10px 0;">
                <b>{area['area']}</b> - Risk: {area['risk_score']}%<br>
                <small>{area['reason']}</small>
            </div>
            """, unsafe_allow_html=True)
            
            
# Footer
st.markdown("---")
st.markdown("### 🚀 Integrated Platform Status")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.success("**Web App**: ✅ Operational")

with col2:
    st.info("**Mobile App**: 📱 Simulated")

with col3:
    st.info("**Backend API**: 🔧 Simulated")

with col4:
    st.success("**Crime Network**: 🌍 Operational")

if __name__ == "__main__":
    # This will run the unified dashboard
    pass
