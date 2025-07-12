import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000'; 

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Accept': 'application/json',
    'Content-Type': 'application/json', 
  },
});


apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);


export const fetchProducts = () => apiClient.get('/api/products');
export const fetchProductById = (id) => apiClient.get(`/api/products/${id}`);
export const fetchCategories = () => apiClient.get('/api/categories');

// For creating products (which uses FormData)
export const createProduct = (formData) => {
  return apiClient.post('/api/products', formData, {
    headers: {
      'Content-Type': 'multipart/form-data', 
    },
  });
};

export const searchProducts = (query) => {
  const params = new URLSearchParams({ query });
  return apiClient.get(`/api/products/search?${params.toString()}`);
};

export const updateProduct = (id, formData) => {
  return apiClient.put(`/api/products/${id}`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};
export const deleteProduct = (id) => apiClient.delete(`/api/products/${id}`);

export const registerUser = (userData) => apiClient.post('/api/auth/register', userData); 
export const loginUser = (loginPayload) => { // loginPayload is URLSearchParams
  return apiClient.post('/api/auth/login', loginPayload, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  });
};

export const createOrder = (checkoutData) => {
  // checkoutData will be a JSON object like the one tested in /docs
  return apiClient.post('/api/orders', checkoutData);
};
export const fetchOrders = () => apiClient.get('/api/orders');
export const fetchOrderById = (id) => apiClient.get(`/api/orders/${id}`);

export const fetchCurrentUser = () => apiClient.get('/api/users/me');


export default apiClient; 