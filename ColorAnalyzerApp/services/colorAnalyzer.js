import axios from "axios";

const API = axios.create({
  baseURL: "http://10.79.195.109:8000", // ⚠️ USE YOUR PC IP
  timeout: 30000,
});

export async function analyzeImageColors(imageUri) {
  try {
    console.log("📤 Sending RAW image to backend:", imageUri);

    const formData = new FormData();
    formData.append("file", {
      uri: imageUri,
      name: "image.jpg",
      type: "image/jpeg",
    });

    const response = await API.post("/analyze", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });

    console.log("✅ Backend response received:", response.data);
    return response.data;

  } catch (error) {
    console.error("❌ Backend connection failed:", error);
    throw error;
  }
}
