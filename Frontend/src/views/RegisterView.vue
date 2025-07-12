<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { register } from '@/services/auth'; // Import the register function from your auth service

const router = useRouter();

const fullName = ref('');
const email = ref('');
const password = ref('');
const confirmPassword = ref('');

const isLoading = ref(false);
const error = ref(null); // Will store error messages (string)
const successMessage = ref('');

// apiBaseUrl is no longer needed here as it's handled by the service

const handleRegister = async () => {
  if (password.value !== confirmPassword.value) {
    error.value = 'Passwords do not match.';
    successMessage.value = ''; // Clear success message on new error
    return;
  }
  if (!email.value || !password.value) {
    error.value = 'Email and password are required.';
    successMessage.value = ''; // Clear success message on new error
    return;
  }

  isLoading.value = true;
  error.value = null; // Clear previous errors before new attempt
  successMessage.value = '';

  try {
    const registrationData = {
      full_name: fullName.value || null, // Send null if empty, or backend handles optional
      email: email.value,
      password: password.value,
    };

    // Use the register function from auth.js
    // It internally calls apiRegister from api.js, which uses apiClient
    const responseData = await register(registrationData);

    console.log('Registration successful (RegisterView.vue):', responseData); // responseData is what apiRegister returns
    successMessage.value = `User "${responseData.email}" registered successfully! Please log in.`;

    // Clear form
    fullName.value = '';
    email.value = '';
    password.value = '';
    confirmPassword.value = '';

    // Optional: redirect to login page after a short delay
    setTimeout(() => {
      if (!error.value) { // Only redirect if there was no subsequent error during this process
          router.push('/login');
      }
    }, 2000);

  } catch (err) {
    console.error('Error during registration (RegisterView.vue):', err);
    // The error object 'err' here is what's thrown by the register/apiRegister/axios call
    if (err.response && err.response.data && err.response.data.detail) {
      error.value = `Registration failed: ${err.response.data.detail}`;
    } else if (err.message) { // Fallback to err.message if no detailed response
      error.value = `Registration failed: ${err.message}`;
    } else {
      error.value = 'An unexpected registration error occurred.';
    }
    successMessage.value = ''; // Clear success message on error
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
          Create your account
        </h2>
      </div>
      <form class="mt-8 space-y-6" @submit.prevent="handleRegister">
        <div class="rounded-md shadow-sm -space-y-px">
          <div>
            <label for="full-name" class="sr-only">Full name</label>
            <input id="full-name" name="full-name" type="text" v-model="fullName"
                   class="appearance-none rounded-none relative block w-full px-3 py-3 border border-gray-300 dark:border-gray-600 placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-white bg-white dark:bg-gray-700 rounded-t-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                   placeholder="Full name (Optional)">
          </div>
          <div>
            <label for="email-address" class="sr-only">Email address</label>
            <input id="email-address" name="email" type="email" autocomplete="email" required v-model="email"
                   class="appearance-none rounded-none relative block w-full px-3 py-3 border border-gray-300 dark:border-gray-600 placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-white bg-white dark:bg-gray-700 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                   placeholder="Email address">
          </div>
          <div>
            <label for="password" class="sr-only">Password</label>
            <input id="password" name="password" type="password" autocomplete="new-password" required v-model="password"
                   class="appearance-none rounded-none relative block w-full px-3 py-3 border border-gray-300 dark:border-gray-600 placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-white bg-white dark:bg-gray-700 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                   placeholder="Password">
          </div>
          <div>
            <label for="confirm-password" class="sr-only">Confirm password</label>
            <input id="confirm-password" name="confirm-password" type="password" autocomplete="new-password" required v-model="confirmPassword"
                   class="appearance-none rounded-none relative block w-full px-3 py-3 border border-gray-300 dark:border-gray-600 placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-white bg-white dark:bg-gray-700 rounded-b-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                   placeholder="Confirm password">
          </div>
        </div>

        <!-- Ensure only one message (error or success) is shown at a time -->
        <div v-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded text-sm" role="alert">
          {{ error }}
        </div>
        <div v-else-if="successMessage" class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded text-sm" role="alert">
          {{ successMessage }}
        </div>

        <div>
          <button type="submit" :disabled="isLoading"
                  class="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50">
            <span v-if="isLoading" class="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></span>
            {{ isLoading ? 'Registering...' : 'Sign up' }}
          </button>
        </div>
        <div class="text-sm text-center">
          <router-link to="/login" class="font-medium text-indigo-600 dark:text-indigo-400 hover:text-indigo-500 dark:hover:text-indigo-300">
            Already have an account? Sign in
          </router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
/* Minimal additional styles if needed */
</style>