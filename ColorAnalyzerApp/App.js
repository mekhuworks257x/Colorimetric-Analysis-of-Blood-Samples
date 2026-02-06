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
  FlatList,
} from "react-native";
import * as ImagePicker from "expo-image-picker";
import { LinearGradient } from "expo-linear-gradient";
import { LineChart } from "react-native-chart-kit";
import { analyzeImageColors } from "./services/colorAnalyzer";

const { width } = Dimensions.get("window");

export default function App() {
  const [image, setImage] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const pickImage = async () => {
    try {
      // Request photo library permissions
      const permission = await ImagePicker.requestMediaLibraryPermissionsAsync();
      
      if (!permission.granted) {
        Alert.alert(
          "Permission Required",
          "The app needs permission to access your photo library to analyze images."
        );
        return;
      }

      const res = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: 'images',
        quality: 1,
      });

      if (!res.canceled) {
        setImage(res.assets[0].uri);
        analyze(res.assets[0].uri);
      }
    } catch (error) {
      console.error("Error picking image:", error);
      Alert.alert("Error", "Failed to pick image from gallery");
    }
  };

  const takePhoto = async () => {
    try {
      // Request camera permissions
      const permission = await ImagePicker.requestCameraPermissionsAsync();
      
      if (!permission.granted) {
        Alert.alert(
          "Permission Required",
          "The app needs permission to access your camera to take photos."
        );
        return;
      }

      const res = await ImagePicker.launchCameraAsync({
        quality: 1,
      });

      if (!res.canceled) {
        setImage(res.assets[0].uri);
        analyze(res.assets[0].uri);
      }
    } catch (error) {
      console.error("Error taking photo:", error);
      Alert.alert("Error", "Failed to take photo");
    }
  };

  const analyze = async (uri) => {
    try {
      setLoading(true);
      setResult(null);
      const data = await analyzeImageColors(uri);
      setResult(data);
    } catch (e) {
      const errorMsg = e.response?.data?.error || e.message || "Unknown error occurred";
      Alert.alert(
        "Analysis Failed",
        `Error: ${errorMsg}\n\nMake sure the backend server is running and accessible.`
      );
      console.error("Analysis error:", e);
    } finally {
      setLoading(false);
    }
  };

  const evalPoly = (coeffs, x) => {
    if (!Array.isArray(coeffs) || coeffs.length === 0) {
      return 0;
    }
    return coeffs.reduce((sum, c, i) => {
      const power = coeffs.length - 1 - i;
      return sum + c * Math.pow(x, power);
    }, 0);
  };

  const buildChannelChart = (channel, dotColor) => {
    const xs = Array.isArray(channel?.actual_x) ? channel.actual_x : [];
    const ys = Array.isArray(channel?.actual_y) ? channel.actual_y : [];
    const coeffs = Array.isArray(channel?.coeffs) ? channel.coeffs : [];
    const fitAtActual = xs.map((x) => evalPoly(coeffs, x));
    const labels = xs.map((x, i) => (i % 6 === 0 ? x.toFixed(1) : ""));

    return {
      labels,
      datasets: [
        {
          data: ys,
          color: () => dotColor,
          strokeWidth: 2,
        },
        {
          data: fitAtActual,
          color: () => "#9b59b6",
          strokeWidth: 2,
        },
      ],
    };
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
            {/* TRIAL METRICS */}
            <Text style={styles.sectionTitle}>📈 Trial Metrics</Text>
            <View style={styles.metricsContainer}>
              <View style={styles.metricBox}>
                <Text style={styles.metricLabel}>R²</Text>
                <Text style={styles.metricValue}>{result.trial_metrics.r2.toFixed(4)}</Text>
              </View>
              <View style={styles.metricBox}>
                <Text style={styles.metricLabel}>MAE</Text>
                <Text style={styles.metricValue}>{result.trial_metrics.mae.toFixed(4)}</Text>
              </View>
              <View style={styles.metricBox}>
                <Text style={styles.metricLabel}>RMSE</Text>
                <Text style={styles.metricValue}>{result.trial_metrics.rmse.toFixed(4)}</Text>
              </View>
            </View>

            {/* RESULTS BY TRIAL */}
            {[1, 2, 3].map((trialNum) => {
              const trialWells = result.color_values.filter(cv => cv.trial === trialNum);
              if (trialWells.length === 0) return null;
              
              return (
                <View key={trialNum} style={styles.trialSection}>
                  <Text style={styles.trialTitle}>🧪 Trial {trialNum}</Text>
                  
                  {/* COLOR VALUES TABLE */}
                  <Text style={styles.subsectionTitle}>Color Values</Text>
                  <ScrollView horizontal style={styles.tableContainer}>
                    <View>
                      <View style={styles.tableHeader}>
                        <Text style={styles.tableCell}>Well</Text>
                        <Text style={styles.tableCell}>R</Text>
                        <Text style={styles.tableCell}>G</Text>
                        <Text style={styles.tableCell}>B</Text>
                        <Text style={styles.tableCell}>RGB</Text>
                        <Text style={styles.tableCell}>S</Text>
                      </View>
                      {trialWells.map((row, idx) => (
                        <View key={idx} style={styles.tableRow}>
                          <Text style={styles.tableCell}>{row.well}</Text>
                          <Text style={styles.tableCell}>{row.r.toFixed(1)}</Text>
                          <Text style={styles.tableCell}>{row.g.toFixed(1)}</Text>
                          <Text style={styles.tableCell}>{row.b.toFixed(1)}</Text>
                          <Text style={styles.tableCell}>{row.rgb_mean.toFixed(1)}</Text>
                          <Text style={styles.tableCell}>{row.s_mean.toFixed(1)}</Text>
                        </View>
                      ))}
                    </View>
                  </ScrollView>

                  {/* CONCENTRATIONS TABLE - Reference Format */}
                  <Text style={styles.subsectionTitle}>Predicted Concentrations</Text>
                  <ScrollView horizontal style={styles.tableContainer}>
                    <View>
                      <View style={styles.tableHeader}>
                        <Text style={styles.tableCell}>Well</Text>
                        <Text style={styles.tableCell}>R Value</Text>
                        <Text style={styles.tableCell}>Pred Conc</Text>
                      </View>
                      {trialWells.map((row, idx) => {
                        const globalIdx = result.color_values.indexOf(row);
                        const predConc = result.r_channel?.predicted_concentration?.[globalIdx];
                        // Renumber as 1-12 within each trial (was 0-11 in trialWells array)
                        const localWellNumber = idx + 1;
                        
                        return (
                          <View key={idx} style={styles.tableRow}>
                            <Text style={styles.tableCell}>{localWellNumber}</Text>
                            <Text style={styles.tableCell}>{row.r.toFixed(1)}</Text>
                            <Text style={styles.tableCell}>
                              {predConc !== undefined 
                                ? predConc.toFixed(2) 
                                : "N/A"}
                            </Text>
                          </View>
                        );
                      })}
                    </View>
                  </ScrollView>
                </View>
              );
            })}

            {/* GRAPHS */}
            {result.r_channel && result.s_channel && (
              <>
                <Text style={styles.sectionTitle}>📉 Channel Analysis</Text>
                
                <Text style={styles.graphTitle}>R Channel</Text>
                <LineChart
                  data={buildChannelChart(result.r_channel, "#ff6b6b")}
                  width={width - 40}
                  height={240}
                  yAxisLabel=""
                  xAxisLabel=""
                  chartConfig={{
                    backgroundGradientFrom: "#fff",
                    backgroundGradientTo: "#fff",
                    color: (opacity = 1) => `rgba(0, 0, 0, ${opacity})`,
                    strokeWidth: 2,
                    propsForLabels: { fontSize: 12 },
                    decimalPlaces: 1,
                  }}
                  style={styles.chart}
                  withInnerLines={true}
                  withOuterLines={true}
                  withVerticalLabels={true}
                  withHorizontalLabels={true}
                  segments={4}
                />

                <Text style={styles.graphTitle}>S Channel (Saturation)</Text>
                <LineChart
                  data={buildChannelChart(result.s_channel, "#9c27b0")}
                  width={width - 40}
                  height={240}
                  yAxisLabel=""
                  xAxisLabel=""
                  chartConfig={{
                    backgroundGradientFrom: "#fff",
                    backgroundGradientTo: "#fff",
                    color: (opacity = 1) => `rgba(0, 0, 0, ${opacity})`,
                    strokeWidth: 2,
                    propsForLabels: { fontSize: 12 },
                    decimalPlaces: 1,
                  }}
                  style={styles.chart}
                  withInnerLines={true}
                  withOuterLines={true}
                  withVerticalLabels={true}
                  withHorizontalLabels={true}
                  segments={4}
                />
              </>
            )}

            <TouchableOpacity 
              style={[styles.button, styles.secondaryButton]}
              onPress={() => {
                setImage(null);
                setResult(null);
              }}
            >
              <Text style={styles.buttonText}>Analyze Another Image</Text>
            </TouchableOpacity>
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
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: "bold",
    marginTop: 15,
    marginBottom: 10,
    color: "#c4161c",
  },
  trialSection: {
    marginTop: 20,
    marginBottom: 20,
    padding: 15,
    backgroundColor: "#fafafa",
    borderRadius: 10,
    borderWidth: 1,
    borderColor: "#e0e0e0",
  },
  trialTitle: {
    fontSize: 17,
    fontWeight: "bold",
    marginBottom: 12,
    color: "#c4161c",
    textAlign: "center",
  },
  subsectionTitle: {
    fontSize: 15,
    fontWeight: "600",
    marginTop: 10,
    marginBottom: 8,
    color: "#444",
  },
  tableContainer: {
    marginVertical: 10,
    borderWidth: 1,
    borderColor: "#e0e0e0",
    borderRadius: 8,
    overflow: "hidden",
  },
  tableHeader: {
    flexDirection: "row",
    backgroundColor: "#f5f5f5",
    borderBottomWidth: 2,
    borderBottomColor: "#c4161c",
  },
  tableRow: {
    flexDirection: "row",
    borderBottomWidth: 1,
    borderBottomColor: "#f0f0f0",
  },
  tableCell: {
    padding: 10,
    fontSize: 13,
    fontWeight: "600",
    color: "#333",
    textAlign: "center",
  },
  tableCellSmall: {
    minWidth: 55,
    width: 55,
  },
  metricsContainer: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginVertical: 10,
  },
  metricBox: {
    backgroundColor: "#f9f9f9",
    flex: 1,
    marginHorizontal: 5,
    padding: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: "#e0e0e0",
    alignItems: "center",
  },
  metricLabel: {
    fontSize: 14,
    fontWeight: "600",
    color: "#666",
    marginBottom: 5,
  },
  metricValue: {
    fontSize: 18,
    fontWeight: "bold",
    color: "#c4161c",
  },
  graphTitle: {
    fontSize: 15,
    fontWeight: "bold",
    marginTop: 12,
    marginBottom: 8,
    color: "#333",
  },
  chart: {
    marginVertical: 8,
    borderRadius: 8,
    backgroundColor: "#fff",
  },
  dataRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    paddingVertical: 8,
    paddingHorizontal: 10,
    borderBottomWidth: 1,
    borderBottomColor: "#f0f0f0",
  },
  dataLabel: {
    fontSize: 14,
    fontWeight: "600",
    color: "#333",
  },
  dataValue: {
    fontSize: 14,
    color: "#666",
  },
  metricBoxOld: {
    backgroundColor: "#f9f9f9",
    padding: 10,
    marginTop: 10,
    borderRadius: 8,
  },
});