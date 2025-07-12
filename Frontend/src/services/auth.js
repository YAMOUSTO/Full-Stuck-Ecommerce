import { ref, reactive } from 'vue'; // Import reactive
import { loginUser as apiLogin, registerUser as apiRegister, fetchCurrentUser as apiFetchUser } from './api';

const TOKEN_KEY = 'accessToken';
const USER_EMAIL_KEY = 'userEmail';

// --- Use a single reactive object for auth state ---
export const authState = reactive({
  isAuthenticated: false,
  currentUser: null,
});
// --- End of reactive object ---

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export async function login(credentialsFormData) {
  const response = await apiLogin(credentialsFormData);
  localStorage.setItem(TOKEN_KEY, response.data.access_token);
  await attemptFetchCurrentUser();
  return response.data;
}

export async function register(userData) {
  return await apiRegister(userData);
}

export function logout() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_EMAIL_KEY);
  authState.currentUser = null;       // Update property on reactive object
  authState.isAuthenticated = false;  // Update property on reactive object
  console.log("AUTH.JS: User logged out, authState updated.");
}

export async function attemptFetchCurrentUser() {
  const token = getToken();
  if (token) {
    try {
      const response = await apiFetchUser();
      authState.currentUser = response.data;      // Update property
      authState.isAuthenticated = true;         // Update property
      localStorage.setItem(USER_EMAIL_KEY, response.data.email);
      console.log("AUTH.JS: Current user fetched:", authState.currentUser);
      console.log("AUTH.JS: isAuthenticated set to:", authState.isAuthenticated);
    } catch (error) {
      console.error("AUTH.JS: Failed to fetch current user:", error);
      logout(); // This will update authState.isAuthenticated to false
    }
  } else {
    authState.currentUser = null;
    authState.isAuthenticated = false;
  }
}