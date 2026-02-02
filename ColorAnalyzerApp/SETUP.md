# Setup Instructions

## Quick Start

1. **Install Node.js** (if not already installed)
   - Download from https://nodejs.org/
   - Version 14 or higher recommended

2. **Install Expo CLI globally** (optional but recommended)
   ```bash
   npm install -g expo-cli
   ```

3. **Navigate to project directory**
   ```bash
   cd ColorAnalyzerApp
   ```

4. **Install dependencies**
   ```bash
   npm install
   ```

5. **Start the development server**
   ```bash
   npm start
   ```
   or
   ```bash
   expo start
   ```

6. **Run on your device**
   - Install **Expo Go** app on your iOS or Android device
   - Scan the QR code shown in the terminal/browser
   - The app will load on your device

## Running on Simulators/Emulators

### iOS Simulator (Mac only)
```bash
npm run ios
```
or press `i` in the Expo CLI

### Android Emulator
```bash
npm run android
```
or press `a` in the Expo CLI

**Note:** Requires Android Studio and an emulator set up

## Assets Setup

The app references some assets (icon.png, splash.png, etc.) in `app.json`. For development, these are optional. To add them:

1. Create or download images:
   - `assets/icon.png` - App icon (1024x1024 recommended)
   - `assets/splash.png` - Splash screen (1242x2436 recommended)
   - `assets/adaptive-icon.png` - Android adaptive icon (1024x1024)
   - `assets/favicon.png` - Web favicon (48x48)

2. Place them in the `assets/` folder

## Troubleshooting

### Permission Errors
- **iOS**: Make sure to grant camera and photo library permissions when prompted
- **Android**: Check app settings to ensure permissions are granted

### Color Extraction Not Working
- On web: Should work automatically with Canvas API
- On native: The app uses a fallback method. For better accuracy:
  - Install `react-native-image-colors` (requires bare workflow or custom native code)
  - Or implement a backend service for image analysis
  - Or use TensorFlow Lite for on-device ML color prediction

### Module Not Found Errors
```bash
# Clear cache and reinstall
rm -rf node_modules
npm install
expo start -c
```

## Production Build

To create a production build:

```bash
# For iOS
expo build:ios

# For Android
expo build:android
```

Or use EAS Build (recommended):
```bash
npm install -g eas-cli
eas build --platform ios
eas build --platform android
```

## Features

✅ Image upload from gallery
✅ Camera photo capture
✅ Color extraction (RGB, HSV, Saturation)
✅ Modern gradient UI
✅ Cross-platform support

## Next Steps for Enhanced Color Analysis

For more accurate color extraction from colorimetric strips:

1. **Use ML Model**: Train a TensorFlow Lite model to predict colors from test strips
2. **Backend Service**: Create an API endpoint that uses OpenCV or similar for precise color analysis
3. **Native Module**: Create a custom native module for pixel-level image analysis
4. **Region Selection**: Add UI to let users select specific regions of the image for analysis
