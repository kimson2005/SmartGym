import axios from "axios";

const axiosClient = axios.create({
  baseURL: "http://localhost:8000/api/v1",
  headers: { "Content-Type": "application/json" },
});

// Optionally add interceptors here if needed in the future

export default axiosClient;
