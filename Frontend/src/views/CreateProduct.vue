<script setup>
import { ref } from 'vue';
// import axios from 'axios'; // No longer needed directly
import { createProduct } from '@/services/api'; // Use the createProduct function from your api service
import { useRouter } from 'vue-router';
//import { useToast } from 'vue-toastification';

const router = useRouter();

const productName = ref('');
const productDescription = ref('');
const productPrice = ref(null);
const productImageFile = ref(null); // To hold the selected file object

const isLoading = ref(false);
const error = ref(null);
const successMessage = ref('');



// Function to handle file selection from the input
const handleImageUpload = (event) => {
  const file = event.target.files[0];
  if (file) {
    productImageFile.value = file;
    console.log("Selected image for upload:", productImageFile.value);
  } else {
    productImageFile.value = null;
  }
};

const handleSubmit = async () => {
  if (!productName.value || productPrice.value === null || productPrice.value <= 0) {
    error.value = 'Please fill in product name and a valid price.';
    successMessage.value = ''; // Clear success on new error
    return;
  }

  isLoading.value = true;
  error.value = null; // Clear previous error
  successMessage.value = '';

  const formData = new FormData();
  formData.append('name', productName.value);
  formData.append('price', parseFloat(productPrice.value));

  // Only append description if it has a value
  if (productDescription.value) {
    formData.append('description', productDescription.value);
  }
  // Only append image if a file has been selected
  if (productImageFile.value) {
    formData.append('image', productImageFile.value);
  }

  try {
    // Use the createProduct service function
    // This function already uses apiClient which includes the auth token if present
    // and sets Content-Type to multipart/form-data
    const response = await createProduct(formData);

    console.log('Product created:', response.data);
    successMessage.value = `Product "${response.data.name}" created successfully! ID: ${response.data.id}`;

    // Clear form fields
    productName.value = '';
    productDescription.value = '';
    productPrice.value = null;
    productImageFile.value = null; // Clear the stored file ref

    // Clear the file input element visually
    const fileInput = document.getElementById('productImage');
    if (fileInput) {
      fileInput.value = ''; // This resets the displayed filename in the input
    }

   

  } catch (err) {
    console.error('Error creating product (CreateProduct.vue):', err);
    // The error 'err' here is what's thrown by createProduct/apiClient/axios
    if (err.response && err.response.status === 401) {
        error.value = "Unauthorized. You might need to log in to create products.";
        
    } else if (err.response && err.response.data && err.response.data.detail) {
      error.value = `Failed to create product: ${err.response.data.detail}`;
    } else if (err.message) {
      error.value = `Failed to create product: ${err.message}`;
    } else {
      error.value = 'An unexpected error occurred while creating the product.';
    }
    successMessage.value = ''; // Clear success on error
  } finally {
    isLoading.value = false;
  }
};
</script>

<template>
  <div class="container mx-auto p-4 max-w-2xl">
    <h1 class="text-3xl font-bold text-center my-6 text-gray-800 dark:text-gray-100">Create New Product</h1>

    <form @submit.prevent="handleSubmit" class="bg-white dark:bg-gray-800 shadow-xl rounded-lg p-8 space-y-6">
      <div>
        <label for="productName" class="block text-sm font-medium text-gray-700 dark:text-gray-300">Product Name</label>
        <input type="text" id="productName" v-model.trim="productName" required
               class="mt-1 block w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm placeholder-gray-400 dark:placeholder-gray-500">
      </div>

      <div>
        <label for="productDescription" class="block text-sm font-medium text-gray-700 dark:text-gray-300">Description (Optional)</label>
        <textarea id="productDescription" v-model.trim="productDescription" rows="4"
                  class="mt-1 block w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm placeholder-gray-400 dark:placeholder-gray-500"></textarea>
      </div>

      <div>
        <label for="productPrice" class="block text-sm font-medium text-gray-700 dark:text-gray-300">Price</label>
        <input type="number" id="productPrice" v-model.number="productPrice" required step="0.01" min="0.01"
               class="mt-1 block w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm placeholder-gray-400 dark:placeholder-gray-500">
      </div>
      
      <div>
        <label for="productImage" class="block text-sm font-medium text-gray-700 dark:text-gray-300">Product Image (Optional)</label>
        <input type="file" id="productImage" @change="handleImageUpload" accept="image/png, image/jpeg, image/webp"
               class="mt-1 block w-full text-sm text-gray-500 dark:text-gray-400
                      file:mr-4 file:py-2 file:px-4
                      file:rounded-md file:border-0
                      file:text-sm file:font-semibold
                      file:bg-indigo-50 dark:file:bg-gray-700 file:text-indigo-700 dark:file:text-indigo-300
                      hover:file:bg-indigo-100 dark:hover:file:bg-gray-600
                      focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
        <p v-if="productImageFile" class="text-xs text-gray-500 mt-1">Selected: {{ productImageFile.name }}</p>
      </div>

      <!-- Ensure only one message (error or success) is shown -->
      <div v-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
        <strong class="font-bold">Error:</strong>
        <span class="block sm:inline"> {{ error }}</span>
      </div>
      <div v-else-if="successMessage" class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded relative" role="alert">
        <strong class="font-bold">Success!</strong>
        <span class="block sm:inline"> {{ successMessage }}</span>
      </div>

      <div>
        <button type="submit" :disabled="isLoading"
                class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50">
          <span v-if="isLoading" class="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></span>
          {{ isLoading ? 'Creating...' : 'Create Product' }}
        </button>
      </div>
    </form>
  </div>
</template>

<style scoped>
/* Scoped styles if needed */
</style>