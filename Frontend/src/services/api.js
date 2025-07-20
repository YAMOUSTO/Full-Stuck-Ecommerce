import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'; 
//console.log("Using API Base URL:", API_BASE_URL);
console.log("Using API Base URL:", import.meta.env.VITE_API_BASE_URL);


const apiClient = axios.create({
   baseURL: import.meta.env.VITE_API_BASE_URL,
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


export const fetchProducts = () => apiClient.get('/products');
export const fetchProductById = (id) => apiClient.get(`/products/${id}`);
export const fetchCategories = () => apiClient.get('/categories');

// For creating products (which uses FormData)
export const createProduct = (formData) => {
  return apiClient.post('/products', formData, {
    headers: {
      'Content-Type': 'multipart/form-data', 
    },
  });
};

export const searchProducts = (query) => {
  const params = new URLSearchParams({ query });
  return apiClient.get(`/products/search?${params.toString()}`);
};

export const updateProduct = (id, formData) => {
  return apiClient.put(`/products/${id}`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};
export const deleteProduct = (id) => apiClient.delete(`/products/${id}`);

export const registerUser = (userData) => apiClient.post('/auth/register', userData); 
export const loginUser = (loginPayload) => { // loginPayload is URLSearchParams
  return apiClient.post('/auth/login', loginPayload, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  });
};

export const createOrder = (checkoutData) => {
  // checkoutData will be a JSON object like the one tested in /docs
  return apiClient.post('/orders', checkoutData);
};
export const fetchOrders = () => apiClient.get('/orders');
export const fetchOrderById = (id) => apiClient.get(`/orders/${id}`);

export const fetchCurrentUser = () => apiClient.get('/users/me');


export default apiClient; 