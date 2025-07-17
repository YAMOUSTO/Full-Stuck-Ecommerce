<script setup>

import { ref, onMounted, watch } from 'vue';
import { useRoute, useRouter, RouterLink } from 'vue-router'; 
import { fetchProductById, deleteProduct } from '@/services/api'; 
import { useToast } from 'vue-toastification';
import { authState } from '@/services/auth';

const route = useRoute();
const router = useRouter();

const product = ref(null);
const loading = ref(true);
const error = ref(null);
const isDeleting = ref(false); 



const fetchProductDetails = async (productId) => {
  if (!productId) {
    error.value = new Error('Product ID is missing from route.');
    loading.value = false;
    return;
  }
  loading.value = true;
  error.value = null;
  console.log(`Fetching product details for ID: ${productId} (ProductDetail.vue)`);
  try {
    // Use the service function
    const response = await fetchProductById(productId);
    console.log('API Response (Product Detail):', response.data);
    product.value = response.data;
  } catch (err) {
    console.error(`Error fetching product ID ${productId} (ProductDetail.vue):`, err);
    if (err.response && err.response.status === 404) {
      error.value = new Error(`Product with ID ${productId} not found.`);
    } else if (err.response && err.response.data && err.response.data.detail) {
      error.value = new Error(`Failed to load product: ${err.response.data.detail}`);
    } else {
      error.value = new Error(`Failed to load product: ${err.message || 'An unexpected error occurred.'}`);
    }
     toast.error(error.value.message || "Failed to delete product."); 
  } finally {
    loading.value = false;
  }
};

const handleDeleteProduct = async () => {
  if (!product.value || !product.value.id) {
    console.error("Cannot delete: Product or Product ID is missing.");
    return;
  }

  if (window.confirm(`Are you sure you want to delete "${product.value.name}"? This action cannot be undone.`)) {
    isDeleting.value = true;
    error.value = null; 
    try {
      await deleteProduct(product.value.id);
      console.log(`Product ID ${product.value.id} deleted successfully.`);
      //alert(`Product "${product.value.name}" deleted successfully.`); 
      toast.success(`Product "${product.value.name}" deleted successfully!`);

      router.push('/products'); 
    } catch (err) {
      console.error('Error deleting product (ProductDetail.vue):', err);
      let deleteErrorMsg = `Failed to delete product: ${err.message || 'An unexpected error occurred.'}`;
      if (err.response && err.response.status === 401) {
        deleteErrorMsg = "Unauthorized. You might need to log in again to delete products.";
      } else if (err.response && err.response.data && err.response.data.detail) {
        deleteErrorMsg = `Failed to delete product: ${err.response.data.detail}`;
      }
      error.value = new Error(deleteErrorMsg);
      alert(`Error: ${deleteErrorMsg}`); 
    } finally {
      isDeleting.value = false;
    }
  }
};

onMounted(() => {
  const idFromRoute = route.params.id;
  if (idFromRoute) {
    fetchProductDetails(idFromRoute);
  } else {
    error.value = "No product ID found in URL.";
    loading.value = false;
  }
});

watch(() => route.params.id, (newId, oldId) => {
  if (newId && newId !== oldId) { 
    fetchProductDetails(newId);
  }
});

const goBack = () => {
  router.push('/products'); 
};
</script>

<template>
  <div class="container mx-auto p-4 max-w-3xl">
    <button @click="goBack" class="mb-6 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-800 dark:text-gray-200 font-semibold py-2 px-4 rounded-lg inline-flex items-center transition-colors">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
        <path fill-rule="evenodd" d="M9.707 14.707a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 1.414L7.414 9H15a1 1 0 110 2H7.414l2.293 2.293a1 1 0 010 1.414z" clip-rule="evenodd" />
      </svg>
      Back to Products
    </button>

    <div v-if="loading" class="text-center py-20">
      <p class="text-xl text-gray-500 dark:text-gray-400">Loading product details...</p>
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mt-4"></div>
    </div>

    <div v-else-if="error && !product" class="bg-red-100 border-l-4 border-red-500 text-red-700 p-6 rounded-md shadow-md" role="alert">
      <p class="font-bold text-lg">Oops! Something went wrong.</p>
      <p>{{ error.message }}</p>
    </div>

    <div v-else-if="product" class="bg-white dark:bg-gray-800 shadow-xl rounded-lg overflow-hidden">
      <div class="w-full h-64 bg-gray-200 dark:bg-gray-700 flex items-center justify-center text-gray-400">
        <!-- Construct full URL if image_url is relative -->
        <img v-if="product.image_url" 
             :src="(product.image_url.startsWith('http') ? product.image_url : 'http://127.0.0.1:8000' + product.image_url)" 
             :alt="product.name" class="w-full h-full object-cover">
        <span v-else>No Image Available</span>
      </div>
      <div class="p-6 md:p-8">
        <h1 class="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">{{ product.name }}</h1>
        <p v-if="product.description" class="text-gray-700 dark:text-gray-300 mb-6 text-base leading-relaxed">
          {{ product.description }}
        </p>
        <p v-else class="text-gray-500 dark:text-gray-400 mb-6 italic">No description available.</p>
        
        <div class="flex items-center justify-between mb-6">
          <p class="text-3xl font-extrabold text-indigo-600 dark:text-indigo-400">${{ product.price ? product.price.toFixed(2) : 'N/A' }}</p>
        </div>
 
        <!-- Add to Cart Button (Functionality to be implemented) -->
        <button @click="handleAddToCart(product)" class="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3 px-6 rounded-lg text-lg transition-colors duration-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-opacity-50">
          Add to Cart
        </button>
        <div v-if="authState.isAuthenticated && 
              authState.currentUser && 
              (authState.currentUser.role === 'admin' || 
              authState.currentUser.id === product.owner.id)"
              class="mt-4 border-t border-gray-200 
            dark:border-gray-700 pt-4"
        >
      <p class="text-xs text-center ...">Select Actions</p>
        <!-- Edit Product Link -->
        <router-link :to="{ name: 'EditProduct', params: { id: product.id } }"
                      class="mt-4 w-full block text-center py-3 px-6 border border-indigo-600 dark:border-indigo-400 text-indigo-600 dark:text-indigo-400 font-bold rounded-lg hover:bg-indigo-100 dark:hover:bg-gray-700 transition-colors duration-300">
          Edit Product
        </router-link>

        <!-- Delete Product Button -->
        <button @click="handleDeleteProduct" :disabled="isDeleting"
                class="mt-4 w-full bg-red-600 hover:bg-red-700 text-white font-bold py-3 px-6 rounded-lg transition-colors duration-300 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-opacity-50 disabled:opacity-50">
          
                <span v-if="isDeleting" class="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2 inline-block"></span>
          {{ isDeleting ? 'Deleting...' : 'Delete Product' }}
        </button>
        </div>
        <!-- Display general error message if it occurred during delete and wasn't a 404 during load -->
         <div v-if="error && product" class="mt-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded text-sm" role="alert">
            {{ error.message }}
        </div>
      </div>
    </div>
    
    <!-- Fallback if product is null after loading and no specific loading error was set -->
    <div v-else-if="!loading && !error" class="text-center py-20">
        <p class="text-xl text-gray-500 dark:text-gray-400">Product not found or could not be loaded.</p>
    </div>
  </div>
</template>

<style scoped>
/* Scoped styles if needed */
</style>