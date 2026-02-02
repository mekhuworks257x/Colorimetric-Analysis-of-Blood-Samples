import React, { useState } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  Image,
  ScrollView,
  StyleSheet,
  Alert,
  ActivityIndicator,
  Dimensions,
} from "react-native";
import * as ImagePicker from "expo-image-picker";
import { LinearGradient } from "expo-linear-gradient";
import { analyzeImageColors } from "./services/colorAnalyzer";

const { width } = Dimensions.get("window");

export default function App() {
  const [image, setImage] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const pickImage = async () => {
    const res = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      quality: 1,
    });

    if (!res.canceled) {
      setImage(res.assets[0].uri);
      analyze(res.assets[0].uri);
    }
  };

  const takePhoto = async () => {
    const res = await ImagePicker.launchCameraAsync({
      quality: 1,
    });

    if (!res.canceled) {
      setImage(res.assets[0].uri);
      analyze(res.assets[0].uri);
    }
  };

  const analyze = async (uri) => {
    try {
      setLoading(true);
      setResult(null);
      const data = await analyzeImageColors(uri);
      setResult(data);
    } catch (e) {
      Alert.alert("Error", "Backend connection failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <LinearGradient
      colors={["#ffffff", "#ffe6ea", "#f7b6c4"]}
      style={styles.container}
    >
      <ScrollView contentContainerStyle={styles.scroll}>

        {/* LOGO */}
        <Image
          source={require("./assets/logo.png")}
          style={styles.logo}
          resizeMode="contain"
        />

        {/* TITLE */}
        <Text style={styles.title}>Color Analyzer</Text>
        <Text style={styles.subtitle}>
          Analyze colors from images and{"\n"}colorimetric strips
        </Text>

        {/* BUTTONS */}
        {!result && !loading && (
          <>
            <TouchableOpacity style={styles.button} onPress={pickImage}>
              <Text style={styles.buttonText}>Choose from Gallery</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={[styles.button, styles.secondaryButton]}
              onPress={takePhoto}
            >
              <Text style={styles.buttonText}>Take Photo</Text>
            </TouchableOpacity>
          </>
        )}

        {/* IMAGE PREVIEW */}
        {image && (
          <Image source={{ uri: image }} style={styles.preview} />
        )}

        {/* LOADING */}
        {loading && <ActivityIndicator size="large" color="#c4161c" />}

        {/* RESULTS */}
        {result && (
          <View style={styles.resultBox}>
            <Text style={styles.sectionTitle}>Intermediate Steps</Text>
            <Text>Trials detected: {result.steps.trials_detected}</Text>
            <Text>Wells detected: {result.steps.wells_detected}</Text>
            <Text>Feature: {result.steps.feature_type}</Text>
            <Text>Model: {result.steps.model}</Text>

            <Text style={styles.sectionTitle}>Predicted Concentrations</Text>

            {result.predictions.map((trialObj, idx) => (
              <View key={idx} style={styles.trialBox}>
                <Text style={styles.trialTitle}>
                  Trial {trialObj.trial}
                </Text>
                {trialObj.concentrations.map((val, wIdx) => (
                  <Text key={wIdx}>
                    Well {wIdx + 1}: {val} g/dL
                  </Text>
                ))}
              </View>
            ))}
          </View>
        )}
      </ScrollView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  scroll: {
    alignItems: "center",
    paddingVertical: 40,
    paddingHorizontal: 20,
  },
  logo: {
    width: 120,
    height: 120,
    marginBottom: 20,
  },
  title: {
    fontSize: 30,
    fontWeight: "bold",
    color: "#c4161c",
  },
  subtitle: {
    fontSize: 16,
    color: "#c4161c",
    textAlign: "center",
    marginVertical: 10,
  },
  button: {
    width: width * 0.85,
    backgroundColor: "#d1122f",
    paddingVertical: 16,
    borderRadius: 14,
    marginTop: 20,
    alignItems: "center",
    shadowColor: "#000",
    shadowOpacity: 0.25,
    shadowRadius: 6,
    elevation: 5,
  },
  secondaryButton: {
    backgroundColor: "#b01028",
  },
  buttonText: {
    color: "#fff",
    fontSize: 17,
    fontWeight: "600",
  },
  preview: {
    width: width * 0.9,
    height: 250,
    borderRadius: 12,
    marginTop: 20,
  },
  resultBox: {
    width: "100%",
    backgroundColor: "#fff",
    marginTop: 30,
    padding: 16,
    borderRadius: 14,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: "bold",
    marginTop: 10,
    marginBottom: 6,
  },
  trialBox: {
    backgroundColor: "#f9f9f9",
    padding: 10,
    marginTop: 10,
    borderRadius: 8,
  },
  trialTitle: {
    fontWeight: "bold",
    marginBottom: 4,
  },
});
