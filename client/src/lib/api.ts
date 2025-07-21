import axios from "axios";
import { environment } from "@/environment";

const api = axios.create({
  baseURL: environment.api_url + "/api/v1",
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: true,
});

api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error?.response?.status === 401) {
    }
    return Promise.reject(error);
  }
);

export { api };
