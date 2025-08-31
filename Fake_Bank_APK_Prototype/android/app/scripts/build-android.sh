#!/bin/bash
# Build script for Android

echo "Building Android app..."
cd android
./gradlew clean
./gradlew assembleRelease

# Check if build was successful
if [ $? -eq 0 ]; then
    echo "=== Build successful! ==="
    echo "APK location: app/build/outputs/apk/release/"
    echo "Generated APK: app/build/outputs/apk/release/app-release.apk"
    
    # Copy APK to project root for easy access
    cp app/build/outputs/apk/release/app-release.apk ../fake-apk-detector-app-release.apk
    echo "APK also copied to: ../fake-apk-detector-app-release.apk"
else
    echo "=== Build failed! ==="
    exit 1
fi

echo "Build completed. APK location: android/app/build/outputs/apk/release/"