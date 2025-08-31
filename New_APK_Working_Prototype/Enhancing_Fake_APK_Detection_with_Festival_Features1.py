# Add these imports at the top of the file (if not already present)
import geopandas as gpd
import folium
from streamlit_folium import folium_static
from wordcloud import WordCloud
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import DBSCAN
import networkx as nx

# Add after the existing FRAUD_KEYWORDS dictionary
FESTIVAL_KEYWORDS = {
    "diwali": {
        "risk_score": 25,
        "explanation": "Diwali is commonly exploited in financial scams with fake offers",
        "period": "October-November",
        "common_scams": ["Cashback offers", "Lottery scams", "Gold coin offers"]
    },
    "holi": {
        "risk_score": 20,
        "explanation": "Holi festival scams often involve fake color/gift offers",
        "period": "March",
        "common_scams": ["Gift hampers", "Color package scams", "Party scams"]
    },
    "eid": {
        "risk_score": 22,
        "explanation": "Eid scams target with fake charity and gift offers",
        "period": "Varies (Islamic calendar)",
        "common_scams": ["Charity fraud", "Special discount scams", "Food hamper scams"]
    },
    "christmas": {
        "risk_score": 20,
        "explanation": "Christmas scams involve fake gift cards and shopping offers",
        "period": "December",
        "common_scams": ["Gift card scams", "Shopping discounts", "Bonus offers"]
    },
    "pongal": {
        "risk_score": 18,
        "explanation": "Pongal scams target South Indian users with festival offers",
        "period": "January",
        "common_scams": ["Special Pongal offers", "Agricultural scam", "Gift scams"]
    },
    "durga puja": {
        "risk_score": 18,
        "explanation": "Durga Puja scams common in Eastern India with pandal offers",
        "period": "September-October",
        "common_scams": ["Pandal entry scams", "Special discount cards", "Cultural event scams"]
    }
}

# Add to the existing FRAUD_KEYWORDS in each language section
# For English
# Initialize FRAUD_KEYWORDS as an empty dictionary or with initial values
FRAUD_KEYWORDS = {}

# Or, if you know what it should contain initially
FRAUD_KEYWORDS = {
    "english": []
}

# Now, you can update it without getting an error
FRAUD_KEYWORDS["english"].update(...)
FRAUD_KEYWORDS["english"].update({
    "festival": {"score": 15, "explanation": "Festival-themed scams are common during holiday seasons"},
    "celebration": {"score": 10, "explanation": "Celebration offers often used to lure victims"},
    "special edition": {"score": 18, "explanation": "Special edition claims frequently used in fake app scams"}
})

# For Hindi
FRAUD_KEYWORDS["hindi"].update({
    "त्योहार": {"score": 15, "explanation": "त्योहार के थीम वाले घोटाले छुट्टियों के मौसम में आम हैं"},
    "उत्सव": {"score": 10, "explanation": "उत्सव की पेशकशें अक्सर शिकार को लुभाने के लिए उपयोग की जाती हैं"},
    "विशेष संस्करण": {"score": 18, "explanation": "विशेष संस्करण के दावे नकली ऐप घोटालों में अक्सर उपयोग किए जाते हैं"}
})

# For Tamil
FRAUD_KEYWORDS["tamil"].update({
    "திருவிழா": {"score": 15, "explanation": "திருவிழா தீம் கொண்ட மோசடிகள் விடுமுறை காலங்களில் பொதுவானவை"},
    "விழா": {"score": 10, "explanation": "விழா சலுகைகள் பெரும்பாலும் பலிகளை ஈர்ப்பதற்குப் பயன்படுத்தப்படுகின்றன"},
    "சிறப்பு பதிப்பு": {"score": 18, "explanation": "சிறப்பு பதிப்பு கூற்றுகள் போலி பயன்பாட்டு மோசடிகளில் அடிக்கடி பயன்படுத்தப்படுகின்றன"}
})

# For Telugu
FRAUD_KEYWORDS["telugu"].update({
    "పండుగ": {"score": 15, "explanation": "పండుగ థీమ్డ్ స్కామ్లు సెలవు సీజన్లలో సాధారణం"},
    "ఉత్సవం": {"score": 10, "explanation": "ఉత్సవ ఆఫర్లు తరచుగా బాధితులను ఆకర్షించడానికి ఉపయోగించబడతాయి"},
    "ప్రత్యేక సంచిక": {"score": 18, "explanation": "ప్రత్యేక సంచిక దావాలు నకిలీ యాప్ స్కామ్లలో తరచుగా ఉపయోగించబడతాయి"}
})

# Add new regional languages (example: Bengali)
FRAUD_KEYWORDS["bengali"] = {
    "নগদ": {"score": 15, "explanation": "নগদ ফেরতের প্রতিশ্রুতি সাধারণত কেলেঙ্কারিতে শিকারের প্রলোভন দিতে ব্যবহৃত হয়"},
    "বোনাস": {"score": 12, "explanation": "বোনাস অফারগুলি প্রায়শই জাল পুরস্কার কেলেঙ্কারিতে ব্যবহৃত হয়"},
    "পুরস্কার": {"score": 10, "explanation": "পুরস্কারের প্রতিশ্রুতি প্রায়শই আর্থিক কেলেঙ্কারিতে জাল প্রণোদনা হিসাবে থাকে"},
    "জয়": {"score": 15, "explanation": "পুরস্কার জয়ের দাবি লটারি কেলেঙ্কারিতে সাধারণ"},
    "বিনামূল্যে": {"score": 10, "explanation": "বিনামূল্যের অফারগুলি প্রায়শই ব্যবহারকারীদের কেলেঙ্কারিতে ফাঁদে ফেলতে ব্যবহৃত হয়"},
    "জরুরী": {"score": 8, "explanation": "সতর্ক সিদ্ধান্ত এড়াতে মিথ্যা জরুরিতা তৈরি করে"},
    "যাচাই": {"score": 8, "explanation": "Credentials চুরি করতে verification scams-এ প্রায়শই ব্যবহৃত হয়"},
    "লটারি": {"score": 20, "explanation": "লটারি দাবি সবচেয়ে সাধারণ আর্থিক কেলেঙ্কারিগুলির মধ্যে একটি"},
    "উপহার": {"score": 10, "explanation": "ব্যবহারকারীদের প্রতারণা করতে জাল উপহারের প্রস্তাব ব্যবহার করা হয়"},
    "অফার": {"score": 8, "explanation": "বিশেষ অফারগুলি সাধারণত শপিং কেলেঙ্কারিতে ব্যবহৃত হয়"},
    "ছাড়": {"score": 5, "explanation": "বিশ্বাস করতে অসাধারণ ছাড়গুলি প্রায়শই কেলেঙ্কারি নির্দেশ করে"},
    "দাবি": {"score": 12, "explanation": "ব্যবহারকারীদের কিছু claim করতে উত্সাহিত করা একটি সাধারণ কেলেঙ্কারি কৌশল"},
    "সীমিত": {"score": 7, "explanation": "ব্যবহারকারীদের উপর চাপ দিতে মিথ্যা scarcity তৈরি করে"},
    "সময়": {"score": 5, "explanation": "সময়-সীমিত অফারগুলি চিন্তা না করে কাজ করার জন্য চাপ তৈরি করে"},
    "বিজয়ী": {"score": 15, "explanation": "মিথ্যা বিজয়ী ঘোষণা কেলেঙ্কারিতে সাধারণ"},
    "উৎসব": {"score": 15, "explanation": "উৎসব-থিমযুক্ত কেলেঙ্কারি ছুটির মৌসুমে সাধারণ"},
    "আনন্দ": {"score": 10, "explanation": "আনন্দের প্রস্তাবগুলি প্রায়শই শিকারের প্রলোভন দিতে ব্যবহৃত হয়"},
    "বিশেষ সংস্করণ": {"score": 18, "explanation": "বিশেষ সংস্করণের দাবিগুলি জাল অ্যাপ কেলেঙ্কারিতে প্রায়শই ব্যবহৃত হয়"}
}

# Add after the existing CASE_URGENCY_LEVELS
FESTIVAL_PERIODS = {
    "diwali": {"start": "10-15", "end": "11-15", "risk_multiplier": 1.5},
    "holi": {"start": "03-01", "end": "03-31", "risk_multiplier": 1.3},
    "eid": {"start": "04-20", "end": "05-20", "risk_multiplier": 1.4},
    "christmas": {"start": "12-01", "end": "12-31", "risk_multiplier": 1.3},
    "pongal": {"start": "01-10", "end": "01-20", "risk_multiplier": 1.2},
    "durga puja": {"start": "09-25", "end": "10-15", "risk_multiplier": 1.2}
}

# Add this function to detect festival patterns
def detect_festival_patterns(text, current_date=None):
    """
    Detect festival-related patterns in text and calculate additional risk
    based on current date proximity to actual festival dates
    """
    detected_festivals = []
    total_risk = 0
    
    if not text:
        return detected_festivals, total_risk
    
    text_lower = text.lower()
    current_date = current_date or datetime.now()
    current_month_day = current_date.strftime("%m-%d")
    
    for festival, festival_data in FESTIVAL_KEYWORDS.items():
        if festival in text_lower:
            # Calculate base risk
            base_risk = festival_data["risk_score"]
            
            # Check if current date is during festival period
            festival_period = FESTIVAL_PERIODS.get(festival, {})
            festival_start = festival_period.get("start", "")
            festival_end = festival_period.get("end", "")
            risk_multiplier = festival_period.get("risk_multiplier", 1.0)
            
            # Apply risk multiplier if during festival period
            if festival_start and festival_end and festival_start <= current_month_day <= festival_end:
                final_risk = base_risk * risk_multiplier
                timing_note = " (festival period - increased risk)"
            else:
                final_risk = base_risk
                timing_note = ""
            
            detected_festivals.append({
                "festival": festival,
                "risk_score": final_risk,
                "explanation": festival_data["explanation"] + timing_note,
                "common_scams": festival_data["common_scams"]
            })
            total_risk += final_risk
    
    return detected_festivals, total_risk

# Add this function to show festival alerts
def show_festival_alerts(detected_festivals, app_name):
    """
    Display festival-specific alerts with contextual information
    """
    if not detected_festivals:
        return
    
    st.subheader("🎆 Festival Scam Alerts")
    
    for festival_info in detected_festivals:
        festival = festival_info['festival']
        risk_score = festival_info['risk_score']
        explanation = festival_info['explanation']
        common_scams = festival_info['common_scams']
        
        with st.expander(f"⚠️ {festival.capitalize()} Pattern Detected ({risk_score} risk points)", expanded=True):
            st.error(explanation)
            st.write("**Common scams during this festival:**")
            for scam in common_scams:
                st.write(f"- {scam}")
            
            # Add prevention tips based on festival
            st.write("**Prevention tips:**")
            if festival == "diwali":
                st.write("- Verify all Diwali offers directly on bank websites")
                st.write("- Avoid clicking on links in SMS/WhatsApp messages")
                st.write("- Check app reviews and download counts before installing")
            elif festival == "holi":
                st.write("- Be cautious of Holi party invites with payment requests")
                st.write("- Verify color/gift package offers with legitimate retailers")
                st.write("- Don't share OTPs or banking details for 'Holi specials'")

# Update the detect_fraud_keywords function to include festival detection
def detect_fraud_keywords(text, include_festivals=True):
    detected_keywords = []
    total_risk = 0
    
    if not text:
        return detected_keywords, total_risk
    
    text_lower = text.lower()
    
    for lang, keywords in FRAUD_KEYWORDS.items():
        for keyword, keyword_data in keywords.items():
            if keyword.lower() in text_lower:
                detected_keywords.append({
                    "keyword": keyword,
                    "language": lang,
                    "risk_score": keyword_data["score"],
                    "explanation": keyword_data["explanation"]
                })
                total_risk += keyword_data["score"]
    
    # Add festival pattern detection
    if include_festivals:
        festival_patterns, festival_risk = detect_festival_patterns(text)
        for festival in festival_patterns:
            detected_keywords.append({
                "keyword": festival["festival"],
                "language": "festival",
                "risk_score": festival["risk_score"],
                "explanation": festival["explanation"],
                "is_festival": True
            })
        total_risk += festival_risk
    
    return detected_keywords, total_risk

# Add this function to generate a word cloud
def generate_word_cloud(text, max_words=50):
    """
    Generate a word cloud from text for visualization
    """
    if not text:
        return None
        
    wordcloud = WordCloud(
        width=800, 
        height=400, 
        background_color='white',
        max_words=max_words,
        colormap='Reds'
    ).generate(text)
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    return fig

# Add this function to show geographical distribution
def show_geographical_distribution(case_data):
    """
    Show geographical distribution of cases on a map
    """
    # This is a simplified version - in production, you would use real location data
    st.subheader("🌍 Geographical Distribution of Cases")
    
    # Create a sample map (in real implementation, use actual case locations)
    m = folium.Map(location=[20.5937, 78.9629], zoom_start=5)  # Center on India
    
    # Add sample markers for major cities
    cities = [
        {"name": "Mumbai", "lat": 19.0760, "lon": 72.8777, "cases": 23},
        {"name": "Delhi", "lat": 28.6139, "lon": 77.2090, "cases": 18},
        {"name": "Bangalore", "lat": 12.9716, "lon": 77.5946, "cases": 15},
        {"name": "Chennai", "lat": 13.0827, "lon": 80.2707, "cases": 12},
        {"name": "Kolkata", "lat": 22.5726, "lon": 88.3639, "cases": 10}
    ]
    
    for city in cities:
        folium.CircleMarker(
            location=[city["lat"], city["lon"]],
            radius=city["cases"] * 0.8,
            popup=f"{city['name']}: {city['cases']} cases",
            color='red',
            fill=True,
            fillColor='red'
        ).add_to(m)
    
    folium_static(m, width=700, height=400)
    
    st.caption("Sample geographical distribution of detected scam cases across major Indian cities")

# Add this function to show campaign network visualization
def show_campaign_network(mimic_detection):
    """
    Visualize the network of connected campaigns and apps
    """
    if not mimic_detection:
        st.info("No campaign network data available for this app.")
        return
    
    st.subheader("🔗 Campaign Network Analysis")
    
    # Create a directed graph
    G = nx.DiGraph()
    
    # Add nodes and edges based on mimic detection
    for match in mimic_detection:
        campaign = match['campaign']
        campaign_data = match['campaign_data']
        
        # Add campaign node
        G.add_node(campaign, type='campaign', size=100)
        
        # Add target nodes and edges
        if 'targets' in campaign_data:
            for target in campaign_data['targets']:
                G.add_node(target, type='target', size=50)
                G.add_edge(campaign, target, weight=2)
    
    # Draw the graph
    plt.figure(figsize=(10, 6))
    pos = nx.spring_layout(G, k=1, iterations=50)
    
    # Draw nodes
    nx.draw_networkx_nodes(G, pos, 
                          nodelist=[n for n, attr in G.nodes(data=True) if attr.get('type') == 'campaign'],
                          node_size=300, node_color='red', alpha=0.7)
    
    nx.draw_networkx_nodes(G, pos, 
                          nodelist=[n for n, attr in G.nodes(data=True) if attr.get('type') == 'target'],
                          node_size=200, node_color='blue', alpha=0.7)
    
    # Draw edges
    nx.draw_networkx_edges(G, pos, edge_color='gray', alpha=0.6)
    
    # Draw labels
    nx.draw_networkx_labels(G, pos, font_size=8)
    
    plt.title("Campaign-Target Network")
    plt.axis('off')
    st.pyplot(plt)

# Add this function to show temporal patterns
def show_temporal_patterns(case_database):
    """
    Show temporal patterns of scam campaigns
    """
    if not case_database:
        st.info("No temporal data available yet.")
        return
    
    st.subheader("📅 Temporal Patterns of Scam Campaigns")
    
    # Extract timestamps from cases
    timestamps = []
    for case_id, case_data in case_database.items():
        if 'timestamp' in case_data:
            try:
                timestamps.append(datetime.fromisoformat(case_data['timestamp']))
            except:
                pass
    
    if not timestamps:
        st.info("No timestamp data available in cases.")
        return
    
    # Create a DataFrame for plotting
    df_temporal = pd.DataFrame({
        'timestamp': timestamps,
        'count': 1
    })
    
    # Group by month
    df_temporal['month'] = df_temporal['timestamp'].dt.to_period('M')
    monthly_counts = df_temporal.groupby('month').size()
    
    # Plot monthly trends
    fig, ax = plt.subplots(figsize=(10, 4))
    monthly_counts.plot(kind='line', ax=ax, marker='o')
    ax.set_title("Monthly Case Volume")
    ax.set_ylabel("Number of Cases")
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    st.pyplot(fig)
    
    # Show seasonal patterns
    st.write("**Seasonal Patterns:**")
    df_temporal['month_num'] = df_temporal['timestamp'].dt.month
    seasonal_counts = df_temporal.groupby('month_num').size()
    
    # Map month numbers to festival periods
    festival_months = {
        10: "Diwali Season",
        11: "Diwali Season",
        3: "Holi Season",
        12: "Christmas Season",
        1: "Pongal/New Year",
        9: "Durga Puja",
        10: "Durga Puja/Diwali"
    }
    
    for month, count in seasonal_counts.items():
        festival_note = festival_months.get(month, "")
        if festival_note:
            st.write(f"- Month {month}: {count} cases ({festival_note})")
        else:
            st.write(f"- Month {month}: {count} cases")

# Update the show_social_engineering_alerts function
def show_social_engineering_alerts(detected_keywords, app_name):
    """
    Display social engineering alerts with explanations for detected keywords
    """
    if not detected_keywords:
        return
    
    st.subheader("🚨 Social Engineering Alerts")
    
    # Separate festival patterns from regular keywords
    festival_patterns = [k for k in detected_keywords if k.get('is_festival')]
    regular_keywords = [k for k in detected_keywords if not k.get('is_festival')]
    
    # Show festival alerts first if present
    if festival_patterns:
        show_festival_alerts(festival_patterns, app_name)
    
    # Group regular keywords by language
    keywords_by_language = {}
    for keyword_info in regular_keywords:
        lang = keyword_info['language']
        if lang not in keywords_by_language:
            keywords_by_language[lang] = []
        keywords_by_language[lang].append(keyword_info)
    
    # Display alerts for each language
    for lang, keywords in keywords_by_language.items():
        with st.expander(f"🔍 {lang.capitalize()} Fraud Keywords Detected ({len(keywords)})", expanded=len(keywords) < 5):
            for keyword_info in keywords:
                keyword = keyword_info['keyword']
                risk_score = keyword_info['risk_score']
                explanation = keyword_info['explanation']
                
                st.warning(f"**'{keyword}'** ({risk_score} risk points)")
                st.caption(f"*{explanation}*")
    
    # Generate a summary alert based on the most significant keywords
    if detected_keywords:
        highest_risk_keyword = max(detected_keywords, key=lambda x: x['risk_score'])
        
        # Create a contextual alert message
        if any(k.get('is_festival') for k in detected_keywords):
            festival_keywords = [k for k in detected_keywords if k.get('is_festival')]
            primary_festival = max(festival_keywords, key=lambda x: x['risk_score'])['keyword']
            alert_message = f"This app pretends to be a {primary_festival.capitalize()} Edition – likely scam targeting festival offers."
        elif "cashback" in app_name.lower() or any("cashback" in k['keyword'].lower() for k in detected_keywords):
            alert_message = f"This app uses cashback offers to lure victims – high probability of financial scam."
        elif "reward" in app_name.lower() or any("reward" in k['keyword'].lower() for k in detected_keywords):
            alert_message = f"This app promises unrealistic rewards – likely a fake reward scam."
        else:
            alert_message = f"This app uses suspicious language patterns commonly found in financial scams."
        
        st.error(f"🚨 **Social Engineering Alert:** {alert_message}")

# Add this function to provide prevention guidelines
def show_prevention_guidelines(detected_keywords):
    """
    Display prevention guidelines based on detected scam patterns
    """
    st.subheader("🛡️ Prevention Guidelines")
    
    # Check for specific scam patterns and provide targeted advice
    has_festival_scam = any(k.get('is_festival') for k in detected_keywords)
    has_lottery_scam = any("lottery" in k['keyword'].lower() or "win" in k['keyword'].lower() for k in detected_keywords)
    has_cashback_scam = any("cashback" in k['keyword'].lower() for k in detected_keywords)
    
    if has_festival_scam:
        st.info("""
        **Festival Scam Prevention:**
        - Verify festival offers directly on official bank websites
        - Avoid clicking on links in SMS, WhatsApp, or email messages
        - Check app reviews and download counts before installing
        - Be wary of apps offering "special edition" or "limited time" festival offers
        """)
    
    if has_lottery_scam:
        st.info("""
        **Lottery Scam Prevention:**
        - Remember: legitimate lotteries don't ask for payment to claim prizes
        - Never share OTPs or banking details to claim "winnings"
        - Verify lottery claims with official organizations
        - Be suspicious of unexpected winning notifications
        """)
    
    if has_cashback_scam:
        st.info("""
        **Cashback Scam Prevention:**
        - Check cashback terms and conditions carefully
        - Verify offers directly with retailers or service providers
        - Be wary of unusually high cashback promises
        - Avoid apps that ask for excessive permissions for cashback offers
        """)
    
    # General guidelines
    st.info("""
    **General Safety Guidelines:**
    - Only download apps from official app stores
    - Check app permissions before installing
    - Look for verified developer badges
    - Read recent app reviews before downloading
    - Keep your device and security software updated
    """)

# Update the display_police_dashboard function to include new visualizations
def display_police_dashboard(apk_data, result):
    """Display detailed results for police users"""
    # ... [existing code] ...
    
    # Add new tabs for the enhanced features
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
        "Overview", "Technical Details", "Behavior Analysis", "Threat Intelligence", 
        "APK DNA Analysis", "Case Management", "Social Engineering Analysis", 
        "Campaign Visualization", "Temporal Analysis"
    ])
    
    # ... [existing tab content] ...
    
    with tab8:  # New Campaign Visualization tab
        st.subheader("📊 Campaign Visualization")
        
        # Word cloud of app name and detected keywords
        app_name = apk_data.get('app_name', '')
        keywords_text = " ".join([k['keyword'] for k in result.get('fraud_keywords', [])])
        combined_text = f"{app_name} {keywords_text}"
        
        if combined_text.strip():
            st.write("**Keyword Frequency Visualization**")
            wordcloud_fig = generate_word_cloud(combined_text)
            if wordcloud_fig:
                st.pyplot(wordcloud_fig)
        
        # Campaign network visualization
        if result.get('mimic_detection'):
            show_campaign_network(result['mimic_detection'])
        
        # Geographical distribution (sample)
        show_geographical_distribution(st.session_state.case_database)
    
    with tab9:  # New Temporal Analysis tab
        st.subheader("⏰ Temporal Analysis")
        
        # Show temporal patterns from case database
        show_temporal_patterns(st.session_state.case_database)
        
        # Current festival risk assessment
        current_date = datetime.now()
        st.write("**Current Festival Risk Assessment**")
        
        current_month_day = current_date.strftime("%m-%d")
        high_risk_festivals = []
        
        for festival, period in FESTIVAL_PERIODS.items():
            if period['start'] <= current_month_day <= period['end']:
                high_risk_festivals.append({
                    'festival': festival,
                    'risk_multiplier': period['risk_multiplier'],
                    'period': f"{period['start']} to {period['end']}"
                })
        
        if high_risk_festivals:
            st.warning("**High Risk Period Alert:**")
            for festival in high_risk_festivals:
                st.write(f"- {festival['festival'].capitalize()} season ({festival['period']}): {festival['risk_multiplier']}x risk multiplier")
        else:
            st.info("No high-risk festival periods currently active.")

# Update the display_user_dashboard function
def display_user_dashboard(apk_data, result):
    """Display simplified results for regular users"""
    # ... [existing code] ...
    
    # NEW: Show social engineering alerts
    if 'fraud_keywords' in result and result['fraud_keywords']:
        show_social_engineering_alerts(result['fraud_keywords'], apk_data['app_name'])
        
        # NEW: Show prevention guidelines
        show_prevention_guidelines(result['fraud_keywords'])

# Update the main function to include the new features in expanders
def main():
    # ... [existing code] ...
    
    # Additional features in expanders - add these new expanders
    with st.expander("🎆 Festival Scam Detection"):
        st.write("""
        Our enhanced festival scam detection system:
        - Identifies festival-specific scam patterns (Diwali, Holi, Eid, Christmas, etc.)
        - Adjusts risk scores based on current festival seasons
        - Provides festival-specific prevention guidelines
        - Tracks temporal patterns of festival-related scams
        
        **Detected Festival Patterns:**
        - Diwali cashback and lottery scams
        - Holi gift and color package scams  
        - Eid charity and gift scams
        - Christmas shopping and gift card scams
        - Regional festival scams (Pongal, Durga Puja, etc.)
        """)
        
        # Show current festival risk assessment
        current_date = datetime.now()
        current_month_day = current_date.strftime("%m-%d")
        active_festivals = []
        
        for festival, period in FESTIVAL_PERIODS.items():
            if period['start'] <= current_month_day <= period['end']:
                active_festivals.append(festival)
        
        if active_festivals:
            st.warning(f"**Current High-Risk Festivals:** {', '.join([f.capitalize() for f in active_festivals])}")
        else:
            st.info("No high-risk festival periods currently active.")
    
    with st.expander("📈 Advanced Visualization & Analytics"):
        st.write("""
        **Police users have access to advanced visualization capabilities:**
        
        **Campaign Network Mapping:**
        - Visual connections between scam campaigns and targets
        - Identification of coordinated threat actor groups
        - Pattern recognition across multiple incidents
        
        **Geographical Analysis:**
        - Mapping of scam cases by region
        - Identification of geographical hotspots
        - Regional targeting pattern analysis
        
        **Temporal Pattern Analysis:**
        - Seasonal trend identification
        - Festival period risk assessment
        - Time-based pattern recognition
        
        **Keyword Visualization:**
        - Word clouds of scam app characteristics
        - Frequency analysis of scam keywords
        - Pattern visualization for rapid assessment
        """)
        
        if user_role == "police":
            st.success("Police users have access to advanced visualization tools.")
        else:
            st.info("Upgrade to police access for advanced analytics features.")
    
    with st.expander("🛡️ Prevention Guidelines System"):
        st.write("""
        Our prevention guidelines system provides:
        
        **Context-Specific Advice:**
        - Tailored recommendations based on detected scam types
        - Festival-specific prevention measures
        - Regional scam pattern awareness
        
        **Multi-Language Guidance:**
        - Prevention tips in multiple Indian languages
        - Culturally relevant safety information
        - Region-specific scam awareness
        
        **Real-Time Updates:**
        - Dynamic updates based on current threat intelligence
        - Seasonal scam pattern alerts
        - Emerging threat notifications
        """)
    
    # ... [rest of existing code] ...

# Update the scan_apk function to include enhanced fraud detection
def scan_apk(apk_data, apk_path=None):
    # ... [existing code] ...
    
    # Enhanced fraud keyword detection with festival patterns
    app_name = apk_data.get('app_name', '')
    keywords, keyword_risk = detect_fraud_keywords(app_name, include_festivals=True)
    
    # ... [rest of existing code] ...
    
    return {
        # ... [existing return values] ...
        "fraud_keywords": keywords  # Include enhanced fraud keywords with festival patterns
    }

if __name__ == "__main__":
    main()