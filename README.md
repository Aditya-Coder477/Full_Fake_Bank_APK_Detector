                                                 Fake Bank APK Detection Prototype
                                                                             

Public URL for accessing this prototype:https://fullfakebankapkdetector-fhjrqzjbsawsljurz7yzay.streamlit.app/

A comprehensive full-stack system featuring a mobile banking app prototype and a web-based backend for analysis and dashboarding. The project consists of:
Mobile App (fake_bank_apk_prototype): A React Native application built with Capacitor for Android, simulating a bank's mobile interface.
Backend & Analysis API: A FastAPI server that likely handles mobile app requests and provides APIs for the analysis tools.
Analysis Dashboard: A Streamlit web application that provides a visual interface for analyzing APK files and other data.


🏗️ Architecture & Tech Stack
Mobile App (APK)
Framework: React Native
Native Bridge: Capacitor
Language: TypeScript
Environment Management: react-native-dotenv

Backend & Analysis Service
Web Framework: FastAPI (for a modern, async REST/WebSocket API)
Web Server: Uvicorn (an ASGI server for running FastAPI)
Dashboard Framework: Streamlit (for building data-driven web apps rapidly)

Analysis & Data Processing
APK Analysis: androguard (to dissect Android APK files)
Data Manipulation: pandas, numpy, scipy
Data Visualization: matplotlib, seaborn, plotly, folium
Machine Learning: scikit-learn

Utilities
Environment Variables: python-dotenv
File Uploads: python-multipart, aiofiles
Network Requests: requests
WHOIS Lookups: python-whois
TideExtract:Specific library for analysis needs


Prerequisites
Before you begin, ensure you have the following installed on your system:
Node.js (v18 or higher) & npm - For the mobile app.
Download from nodejs.org
Python (3.8 or higher) & pip - For the backend and dashboard.
Java Development Kit (JDK) 11 or 17 - For building the Android APK.
Android Studio & Android SDK - For running the mobile app on an emulator or device.
Git

Installation & Setup
1. Clone the Repository-git clone <your-repository-url>
                        cd fake_bank_project
2. Backend & Dashboard Setup (FastAPI & Streamlit)
Navigate to the backend directory 
Create a Python Virtual Environment (Highly Recommended)
Install Python Dependencies


Mobile App Setup (React Native)
Navigate to the mobile app directory:
cd Fake_Bank_APK_Prototype

Install JavaScript Dependencies:
npm install

Configure Capacitor for Android:
npx cap add android

Sync your React Native code with the Android project:
npx cap sync

Running the Applications
Running the Backend (FastAPI Server)
From  backend directory with the virtual environment activated:
uvicorn main:app --reload --host 0.0.0.0 --port 8000
The API server will start on http://localhost:8000.
Interactive API documentation (Swagger UI) will be available at http://localhost:8000/docs.

Running the Dashboard (Streamlit App)
In New_APK_Working_Prototype folder,run this command
streamlit run unified_dashboard_app.py
The dashboard will start on http://localhost:8500 or http://localhost:8501.

In Fake_Bank_APK_Prototype folder(mobile app directory):
Start the Metro Bundler (Development Server):
# For development
npm run start:dev
# OR for production-like environment
npm run start:prod
Keep this terminal running.
In a new terminal, run the app on an Android emulator or connected device:
# For development
npm run android:dev
# OR for production-like environment
npm run android:prod
This script will use react-native-dotenv to set the APP_ENV variable, which this app can use to connect to the correct backend 


📱 Building the APK
To create a release-ready Android APK for distribution:
# Build for development
npm run build:android:dev

# Build for production (release)
npm run build:android:prod
This will execute the ./scripts/build-android.sh script with the appropriate environment variable set

Configuration
Environment Variables: Create a .env file in the backend/ directory for variables like database URLs, secret keys, and API keys. Use python-dotenv to load them.
Mobile App API URL: The React Native app uses react-native-dotenv. Create a .env file in the mobile/ directory to define backend's base URL for each environment (e.g., API_URL_DEV=http://10.0.2.2:8000, API_URL_PROD=https://your-real-api.com). Note: Use 10.0.2.2 on Android emulators to connect to localhost on  host machine.


Usage
Mobile App: Open the app on  Android device. It should connect to the locally running FastAPI backend (ensure the correct API_URL is set in mobile .env file for environment).
API: Interact with the backend directly via the Swagger docs at http://localhost:8000/docs.
Dashboard: Open http://localhost:8501 in your browser. Use the dashboard to upload and analyze APK files using the integrated tools like androguard and tideextract.


This is a prototype:
The "FakeBank" app does not handle real financial transactions.
The APK analysis tools are for demonstration and learning purposes only.
This software is not intended for production use without significant security and performance review.

Public URL for accessing this prototype:https://fullfakebankapkdetector-fhjrqzjbsawsljurz7yzay.streamlit.app/













https://fullfakebankapkdetector-fhjrqzjbsawsljurz7yzay.streamlit.app/
