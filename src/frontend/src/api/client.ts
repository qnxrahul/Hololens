import axios from "axios";

const baseURL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8001";

export const apiClient = axios.create({
  baseURL,
  timeout: 10_000,
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
