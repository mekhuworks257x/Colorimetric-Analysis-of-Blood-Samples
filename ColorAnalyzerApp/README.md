# Color Analyzer - Professional Mobile App

A professional, modern mobile application for analyzing colors from images and colorimetric strips. Extract RGB, HSV, and saturation values with precision and share your results.

## ✨ Features

- 📷 **Image Upload**: Choose images from gallery or take photos with camera
- 🎨 **Color Analysis**: Extract dominant colors with RGB, HSV, and saturation values
- 📊 **Detailed Metrics**: View comprehensive color information including:
  - RGB values (Red, Green, Blue)
  - HSV values (Hue, Saturation, Value)
  - Hex color codes
  - Saturation percentage
- 📋 **Copy to Clipboard**: Tap any value to copy it
- 📤 **Share Results**: Share color analysis results with others
- 🎯 **Professional UI**: Modern, clean interface with red and white color scheme
- 📱 **Cross-Platform**: Works on iOS, Android, and Web

## 🚀 Getting Started

### Prerequisites

- Node.js 14+ installed
- Expo CLI (install with `npm install -g expo-cli`)
- Expo Go app on your mobile device (for testing)

### Installation

1. **Clone or navigate to the project directory**
   ```bash
   cd ColorAnalyzerApp
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   npm start
   ```
   or
   ```bash
   expo start
   ```

4. **Run on your device**
   - Install **Expo Go** app on your iOS or Android device
   - Scan the QR code shown in the terminal/browser
   - The app will load on your device

### Running on Simulators/Emulators

**iOS Simulator (Mac only)**
```bash
npm run ios
```

**Android Emulator**
```bash
npm run android
```

## 📱 Usage

1. **Launch the app** on your device
2. **Choose an image**:
   - Tap "Choose from Gallery" to select an existing image
   - Tap "Take Photo" to capture a new image
3. **View results**: The app automatically analyzes the image and displays:
   - Dominant color preview
   - Hex color code
   - RGB values
   - HSV values
   - Saturation percentage
4. **Copy values**: Tap any color value to copy it to clipboard
5. **Share results**: Tap the "Share" button to share analysis results
6. **Analyze another**: Tap "Analyze Another Image" to start over

## 🛠️ Technical Details

### Color Extraction

- **Web**: Uses Canvas API for pixel-level color analysis
- **Mobile**: Uses expo-image-manipulator with intelligent fallback
- **Accuracy**: Samples center region of images for better results with colorimetric strips

### Technologies

- **React Native** - Cross-platform mobile framework
- **Expo** - Development platform and tooling
- **expo-image-picker** - Image selection and camera access
- **expo-image-manipulator** - Image processing
- **expo-clipboard** - Clipboard functionality
- **expo-linear-gradient** - Beautiful gradient backgrounds

## 📦 Project Structure

```
ColorAnalyzerApp/
├── App.js                 # Main app component
├── components/
│   └── ColorValueCard.js  # Reusable color value display component
├── services/
│   └── colorAnalyzer.js   # Color extraction and analysis logic
├── assets/                # Images and icons
├── package.json
├── app.json               # Expo configuration
└── babel.config.js
```

## 🎨 Color Scheme

The app features a professional red and white color scheme:
- **Primary Red**: `#DC143C` (Crimson)
- **Secondary Red**: `#C41E3A`
- **Dark Red**: `#B22222`
- **Background**: White with red gradient

## 🔧 Configuration

### App Metadata

Edit `app.json` to customize:
- App name and slug
- Bundle identifiers
- Permissions
- Icons and splash screens

### Color Analysis

The color analyzer can be enhanced by:
- Installing `react-native-image-colors` for better native color extraction
- Implementing a backend service for ML-based color prediction
- Adding support for multiple color extraction from images

## 📄 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

For issues, questions, or feature requests, please open an issue on the repository.

## 🚀 Building for Production

### iOS
```bash
expo build:ios
```

### Android
```bash
expo build:android
```

Or use EAS Build (recommended):
```bash
npm install -g eas-cli
eas build --platform ios
eas build --platform android
```

## 📝 Version History

- **1.0.0** - Initial release
  - Image upload and camera capture
  - Color analysis (RGB, HSV, Saturation)
  - Copy to clipboard functionality
  - Share results feature
  - Professional UI design

---

Made with ❤️ using React Native and Expo
