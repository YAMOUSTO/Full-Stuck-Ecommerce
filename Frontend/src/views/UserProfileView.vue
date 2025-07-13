<script setup>
import { ref, onMounted, watch, reactive } from 'vue'; 
import { useRouter } from 'vue-router';
import { authState, attemptFetchCurrentUser } from '@/services/auth'; 
import whateverNameYouWantForDefault from '@/services/api';

const router = useRouter();

const isEditing = ref(false);
// Use reactive for the form data to easily reset or copy
const editableUser = reactive({
  full_name: '',
  // email: '' // If you allow email editing (more complex due to uniqueness and JWT)
});

const isLoadingData = ref(true); // For initial load
const isSaving = ref(false);
const error = ref(null);
const successMessage = ref('');

const populateEditableUser = () => {
  if (authState.currentUser) {
    editableUser.full_name = authState.currentUser.full_name || '';
     editableUser.email = authState.currentUser.email; // If editing email
  }
};

onMounted(async () => {
  isLoadingData.value = true;
  if (!authState.isAuthenticated || !authState.currentUser) {
    await attemptFetchCurrentUser();
  }
  // If still not authenticated after trying, redirect to login
  if (!authState.isAuthenticated) {
    router.push('/login');
  } else {
    populateEditableUser(); // Populate form once currentUser is available
  }
  isLoadingData.value = false;
});

// Watch for changes in authState.currentUser to re-populate form if needed
watch(() => authState.currentUser, (newUser) => {
  if (newUser) {
    populateEditableUser();
  }
}, { deep: true });


const toggleEdit = () => {
  if (authState.currentUser && !isEditing.value) { // When starting to edit
    populateEditableUser(); // Ensure form has fresh data from currentUser
  }
  isEditing.value = !isEditing.value;
  error.value = null; // Clear errors when toggling edit mode
  successMessage.value = '';
};

const handleProfileUpdate = async () => {
  if (!editableUser.full_name.trim() && !editableUser.email.trim()) { // Basic validation
      error.value = "At least one field must have a value to update.";
      return;
  }
  isSaving.value = true;
  error.value = null;
  successMessage.value = '';

  try {
    // Prepare only the data you want to send for update
    const updatePayload = {
      full_name: editableUser.full_name,
       email: editableUser.email, // if email editing is enabled
    };

    const response = await whateverNameYouWantForDefault.put('/api/users/me', updatePayload);

    console.log('Profile updated:', response.data);
    successMessage.value = 'Profile updated successfully!';
    
    // Re-fetch current user to update global authState.currentUser with latest data
    await attemptFetchCurrentUser(); 
    
    isEditing.value = false; // Exit edit mode
  } catch (err) {
    console.error('Error updating profile:', err);
    if (err.response && err.response.data && err.response.data.detail) {
      error.value = `Update failed: ${err.response.data.detail}`;
    } else {
      error.value = `Update failed: ${err.message || 'An unexpected error occurred.'}`;
    }
  } finally {
    isSaving.value = false;
  }
};
</script>

<template>
  <div class="container mx-auto p-4 max-w-2xl">
    <h1 class="text-3xl font-bold text-center my-6 text-gray-800 dark:text-gray-100">Your Profile</h1>

    <div v-if="isLoadingData" class="text-center py-10">
      <p class="text-xl text-gray-500 dark:text-gray-400">Loading user data...</p>
    </div>

    <div v-else-if="authState.currentUser" class="bg-white dark:bg-gray-800 shadow-xl rounded-lg p-8">
      <!-- Display Mode -->
      <div v-if="!isEditing" class="space-y-4">
        <div>
          <h3 class="text-sm font-medium text-gray-500 dark:text-gray-400">Full Name</h3>
          <p class="mt-1 text-lg text-gray-900 dark:text-white">{{ authState.currentUser.full_name || 'Not Provided' }}</p>
        </div>
        <div>
          <h3 class="text-sm font-medium text-gray-500 dark:text-gray-400">Email Address</h3>
          <p class="mt-1 text-lg text-gray-900 dark:text-white">{{ authState.currentUser.email }}</p>
        </div>
        <div>
          <h3 class="text-sm font-medium text-gray-500 dark:text-gray-400">Account Status</h3>
          <p :class="['mt-1 text-lg', authState.currentUser.is_active ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400']">
            {{ authState.currentUser.is_active ? 'Active' : 'Inactive' }}
          </p>
        </div>
        <div class="pt-4">
          <button @click="toggleEdit" class="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2 px-4 rounded-lg">
            Edit Profile
          </button>
        </div>
      </div>

      <!-- Edit Mode Form -->
      <form v-else @submit.prevent="handleProfileUpdate" class="space-y-4">
        <div>
          <label for="fullNameEdit" class="block text-sm font-medium text-gray-700 dark:text-gray-300">Full Name</label>
          <input type="text" id="fullNameEdit" v-model.trim="editableUser.full_name"
                 class="mt-1 block w-full px-3 py-2 
                 bg-white dark:bg-gray-700 border 
                 border-gray-300 dark:border-gray-600 
                 rounded-md shadow-sm focus:outline-none 
                 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">
        </div>
        <div>
          <label for="emailEdit" class="block text-sm font-medium text-gray-700 dark:text-gray-300">Email Address</label>
          <input type="email" id="emailEdit" v-model.trim="editableUser.email"
                 class="mt-1 block w-full px-3 py-2 
                 bg-white dark:bg-gray-700 border 
                 border-gray-300 dark:border-gray-600 
                 rounded-md shadow-sm text-gray-900 dark:text-white 
                 focus:outline-none focus:ring-indigo-500 
                 focus:border-indigo-500 sm:text-sm">
        </div>
        

        <div v-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded text-sm" role="alert">
          {{ error }}
        </div>
        <div v-if="successMessage" class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded text-sm" role="alert">
          {{ successMessage }}
        </div>

        <div class="flex space-x-4 pt-4">
          <button type="button" @click="toggleEdit" :disabled="isSaving"
                  class="flex-1 justify-center py-2 px-4 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm font-medium text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none">
            Cancel
          </button>
          <button type="submit" :disabled="isSaving"
                  class="flex-1 justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50">
            <span v-if="isSaving" class="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></span>
            {{ isSaving ? 'Saving...' : 'Save Changes' }}
          </button>
        </div>
      </form>
    </div>

    <div v-else class="text-center py-10">
         <p class="text-xl text-gray-500 dark:text-gray-400">Could not load user profile. Please try logging in again.</p>
         <RouterLink to="/login" class="mt-4 inline-block text-indigo-600 dark:text-indigo-400 hover:underline">Go to Login</RouterLink>
    </div>
  </div>
</template>