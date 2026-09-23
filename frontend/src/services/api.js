import axios from "axios";
const api = axios.create({ baseURL: import.meta.env.VITE_API_URL || "" });
export const fetchSheet = () => api.get("/api/sheet");
export const saveRow = (row, data) => api.put(`/api/sheet/${row}`, data);
export function friendlyError(error) {
  const code = error.response?.status;
  if (code === 409) return "This Sheet changed externally. The latest data has been loaded.";
  if (code === 400 || code === 404) return error.response?.data?.detail || "The selected row cannot be updated.";
  if (code === 401 || code === 403) return "You are not authorized to update this Sheet.";
  if (code === 429) return "Google Sheets is busy. Please try again shortly.";
  return "Unable to synchronize with Google Sheets. Please try again.";
}
