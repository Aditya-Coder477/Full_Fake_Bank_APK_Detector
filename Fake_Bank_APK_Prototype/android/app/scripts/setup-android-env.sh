#!/bin/bash

# Setup Android environment variables
echo "Setting up Android environment..."

# Set Java home (adjust path based on your system)
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64

# Set Android SDK path (adjust based on your system)
export ANDROID_HOME=$HOME/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/emulator
export PATH=$PATH:$ANDROID_HOME/platform-tools

echo "Environment setup complete!"