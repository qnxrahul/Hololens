import axios from "axios";

const baseURL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8001";
const tokenStorageKey = import.meta.env.VITE_AUTH_TOKEN_KEY ?? "viv_auth_token";

export const apiClient = axios.create({
  baseURL,
  timeout: 10_000,
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem(tokenStorageKey);
  if (token) {
    config.headers = config.headers ?? {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      console.error("API error:", error.response.status, error.response.data);
    } else {
      console.error("Network error:", error);
    }
    return Promise.reject(error);
  },
);
