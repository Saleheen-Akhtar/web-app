import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/';

const api = axios.create({
  baseURL: API_URL,
  withCredentials: true,
});

export const login = async (username, password) => {
    try {
        const response = await api.post('token-auth/', { username, password });
        const token = response.data.token;
        api.defaults.headers.common['Authorization'] = `Token ${token}`;
        return true;
    } catch (error) {
        delete api.defaults.headers.common['Authorization'];
        throw error;
    }
};

export const uploadFile = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('upload/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};

export const getDashboard = (uploadId = null) => {
  const url = uploadId ? `dashboard/${uploadId}/` : 'dashboard/';
  return api.get(url);
};

export const getHistory = () => {
  return api.get('history/');
};

export const getReportUrl = (uploadId) => {
  return `${API_URL}report/${uploadId}/`;
};

export default api;
