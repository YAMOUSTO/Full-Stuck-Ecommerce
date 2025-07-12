<script setup>
import { ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { login } from '@/services/auth';

const router = useRouter();
const route = useRoute();

// --- Reactive State Definitions ---
const email = ref('');
const password = ref('');
const isLoading = ref(false); 
const error = ref(null);      
// --- End of Reactive State Definitions ---

const handleLogin = async () => {
  isLoading.value = true;
  error.value = null;

  try {
    const loginPayload = new URLSearchParams();
    loginPayload.append('username', email.value);
    loginPayload.append('password', password.value);

    await login(loginPayload);
    console.log('Login successful');

    const redirectPath = route.query.redirect || '/products';
    router.push(redirectPath);

  } catch (err) {
    console.error('Error object during login (LoginView.vue):', err);
    let errorMessage = 'Login failed: An unexpected error occurred.';
    if (err.response) {
      console.error('Error response data:', err.response.data);
      console.error('Error response status:', err.response.status);
      if (err.response.data && typeof err.response.data.detail === 'string') {
        errorMessage = `Login failed: ${err.response.data.detail}`;
      } else if (err.response.data && Array.isArray(err.response.data.detail) && err.response.data.detail[0] && err.response.data.detail[0].msg) {
        errorMessage = `Login failed: ${err.response.data.detail[0].msg}`;
      } else if (err.response.status === 401) {
        errorMessage = 'Login failed: Incorrect email or password.';
      } else if (err.response.status === 422) {
        errorMessage = 'Login failed: Invalid data provided. Please check your input.';
      } else {
        errorMessage = `Login failed: Server responded with status ${err.response.status}.`;
      }
    } else if (err.request) {
      errorMessage = 'Login failed: No response from server.';
    } else if (err.message) {
      errorMessage = `Login failed: ${err.message}`;
    }
    error.value = errorMessage;
  } finally {
    isLoading.value = false;
  }
};
</script>


<template>
  <div class="flex items-center justify-center min-h-screen bg-gradient-to-br from-slate-900 to-slate-700 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8 bg-white dark:bg-gray-800 p-10 rounded-xl shadow-2xl">
      <div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900 dark:text-white">
          Sign in to your account
        </h2>
      </div>
      <form class="mt-8 space-y-6" @submit.prevent="handleLogin">
        <input type="hidden" name="remember" value="true">
        <div class="rounded-md shadow-sm -space-y-px">
          <div>
            <label for="email-address" class="sr-only">Email address</label>
            <input id="email-address" name="email" type="email" autocomplete="email" required v-model="email"
                   class="appearance-none rounded-none relative block w-full px-3 py-3 border border-gray-300 dark:border-gray-600 placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-white bg-white dark:bg-gray-700 rounded-t-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                   placeholder="Email address">
          </div>
          <div>
            <label for="password" class="sr-only">Password</label>
            <input id="password" name="password" type="password" autocomplete="current-password" required v-model="password"
                   class="appearance-none rounded-none relative block w-full px-3 py-3 border border-gray-300 dark:border-gray-600 placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-white bg-white dark:bg-gray-700 rounded-b-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                   placeholder="Password">
          </div>
        </div>

        <div v-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded text-sm" role="alert">
          {{ error }}
        </div>

        <div>
          <button type="submit" :disabled="isLoading"
                  class="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50">
             <span v-if="isLoading" class="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></span>
            {{ isLoading ? 'Signing in...' : 'Sign in' }}
          </button>
        </div>
         <div class="text-sm text-center">
          <router-link to="/register" class="font-medium text-indigo-600 dark:text-indigo-400 hover:text-indigo-500 dark:hover:text-indigo-300">
            Don't have an account? Sign up
          </router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>


</style>