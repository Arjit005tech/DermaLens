import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const client = axios.create({ baseURL: API_BASE_URL });

client.interceptors.request.use((config) => {
  const token = localStorage.getItem("dermalens_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export const signup = (name, email, password) =>
  client.post("/auth/signup", { name, email, password });

export const login = async (email, password) => {
  const res = await client.post("/auth/login", { email, password });
  localStorage.setItem("dermalens_token", res.data.access_token);
  return res.data;
};

export const logout = () => localStorage.removeItem("dermalens_token");

export const isAuthenticated = () => !!localStorage.getItem("dermalens_token");

export const analyzeImage = (file, answers = {}) => {
  const formData = new FormData();
  formData.append("file", file);
  // Only send fields the user actually answered - backend treats
  // missing fields as "skip this question"
  Object.entries(answers).forEach(([key, value]) => {
    if (value) formData.append(key, value);
  });
  return client.post("/analyze", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

export const getHistory = () => client.get("/history");

export default client;
