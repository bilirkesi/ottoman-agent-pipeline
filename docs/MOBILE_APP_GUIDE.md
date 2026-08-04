# Mobile App - Implementation Guide

## Overview

The Ottoman Agent Mobile app is built with React Native (Expo) and provides:
- Transliteration
- Agent chat
- Key management
- History tracking

## Project Structure

```
mobile/
├── App.js              # Main app
├── package.json        # Dependencies
└── assets/             # Images and icons
```

## Running the App

```bash
# Install dependencies
cd mobile
npm install

# Start Expo
npx expo start

# Run on Android
npx expo start --android

# Run on iOS
npx expo start --ios
```

## Features

### 1. Transliterate Screen
- Input: Ottoman Turkish text
- Mode selection
- Output display
- Confidence scoring

### 2. Chat Screen
- Chat interface
- Message history
- Model selection
- Streaming responses

### 3. Keys Screen
- Key list
- Create new key
- Key details

### 4. History Screen
- Execution history
- Search and filter
- Export results

## Backend Communication

```javascript
const API_BASE_URL = 'http://localhost:8000/api/v1';

// Transliterate
const response = await fetch(`${API_BASE_URL}/transliterate`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ text, mode })
});

// Chat
const response = await fetch(`${API_BASE_URL}/chat`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ message })
});

// Get keys
const response = await fetch(`${API_BASE_URL}/byok/keys`);
```

## Building for Production

### Android
```bash
eas build --platform android
```

### iOS
```bash
eas build --platform ios
```

## Troubleshooting

### CORS Issues
Make sure the backend allows requests from your mobile device's IP.

### Network Issues
On iOS simulator, use `http://10.0.2.2:8000` instead of `localhost`.

## References

- [React Native Documentation](https://reactnative.dev/docs)
- [Expo Documentation](https://docs.expo.dev/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
