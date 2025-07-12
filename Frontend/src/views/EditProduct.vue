<script setup>
import { ref, onMounted, watch } from 'vue';
import { fetchProductById, updateProduct, fetchCategories } from '@/services/api'; // Make sure fetchCategories is imported
import { useRoute, useRouter } from 'vue-router';

const route = useRoute();
const router = useRouter();

const productId = ref(null);
const product = ref({
  name: '',
  description: '',
  price: null,
  image_url: null,
  category_id: null, // Essential for v-model on the select dropdown
});

const categories = ref([]); // To hold categories for the dropdown
const productImageFile = ref(null);

const isLoading = ref(true);
const isSaving = ref(false);
const error = ref(null);
const successMessage = ref('');

// Renamed for clarity to fetch both product and categories
const fetchInitialDataForEdit = async (id) => {
  isLoading.value = true;
  error.value = null;
  successMessage.value = '';
  try {
    // Use Promise.all to fetch both required data sets concurrently
    const [productResponse, categoriesResponse] = await Promise.all([
      fetchProductById(id),
      fetchCategories()
    ]);

    // Populate the form with the specific product's data
    const productData = productResponse.data;
    product.value.name = productData.name;
    product.value.description = productData.description || '';
    product.value.price = productData.price;
    product.value.image_url = productData.image_url;
    product.value.category_id = productData.category_id; // This will pre-select the current category in the dropdown
    productId.value = productData.id;

    // Populate the categories ref for the dropdown
    categories.value = categoriesResponse.data;

  } catch (err) {
    console.error('Error fetching data for edit page:', err);
    error.value = `Failed to load data: ${err.message || 'An unexpected error occurred.'}`;
  } finally {
    isLoading.value = false;
  }
};

const handleImageUpload = (event) => {
  productImageFile.value = event.target.files[0] || null;
};

const handleSubmit = async () => {
  if (!product.value.name || product.value.price === null || product.value.price <= 0) {
    error.value = 'Product name and a valid price are required.';
    return;
  }

  isSaving.value = true;
  error.value = null;
  successMessage.value = '';

  const formData = new FormData();
  formData.append('name', product.value.name);
  formData.append('price', parseFloat(product.value.price));
  if (product.value.description) {
    formData.append('description', product.value.description);
  }
  
  // Append category_id if one is selected
  if (product.value.category_id) {
    formData.append('category_id', product.value.category_id);
  }
  
  if (productImageFile.value) {
    formData.append('image', productImageFile.value);
  }

  try {
    const response = await updateProduct(productId.value, formData);

    console.log('Product updated:', response.data);
    successMessage.value = `Product "${response.data.name}" updated successfully!`;
    
    setTimeout(() => {
      router.push(`/products/${productId.value}`);
    }, 1500);

  } catch (err) {
    // ... (your existing error handling for handleSubmit) ...
    console.error('Error updating product (EditProduct.vue):', err);
    if (err.response?.status === 401) {
        error.value = "Unauthorized. You might need to log in to update products.";
    } else if (err.response?.data?.detail) {
      error.value = `Failed to update product: ${err.response.data.detail}`;
    } else {
      error.value = `Failed to update product: ${err.message || 'An unexpected error occurred.'}`;
    }
  } finally {
    isSaving.value = false;
  }
};

onMounted(() => {
  const idFromRoute = route.params.id;
  if (idFromRoute) {
    fetchInitialDataForEdit(idFromRoute);
  } else {
    error.value = "No product ID found in URL.";
    isLoading.value = false;
  }
});

watch(() => route.params.id, (newId, oldId) => {
  if (newId && newId !== oldId) {
    fetchInitialDataForEdit(newId);
  }
});

const goBack = () => {
  router.back();
};
</script>

<template>
  <div class="container mx-auto p-4 max-w-2xl">
     <button @click="goBack" class="mb-6 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-800 dark:text-gray-200 font-semibold py-2 px-4 rounded-lg inline-flex items-center transition-colors">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
        <path fill-rule="evenodd" d="M9.707 14.707a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 1.414L7.414 9H15a1 1 0 110 2H7.414l2.293 2.293a1 1 0 010 1.414z" clip-rule="evenodd" />
      </svg>
      Back
    </button>
    <h1 class="text-3xl font-bold text-center my-6 text-gray-800 dark:text-gray-100">Edit Product</h1>

    <div v-if="isLoading" class="text-center py-10">
      <p class="text-xl text-gray-600 dark:text-gray-400">Loading product data...</p>
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500 mx-auto mt-3"></div>
    </div>

    <form v-else-if="product && productId" @submit.prevent="handleSubmit" 
    class="
    bg-white 
    dark:bg-gray-800 
    shadow-xl 
    rounded-lg 
    p-8 
    space-y-6">
      <div>
        <label for="productName" 
        class="block text-sm 
        font-medium text-gray-700 
        dark:text-gray-300">Product Name</label>
        <input type="text" id="productName" v-model.trim="product.name" required
              class="mt-1 block w-full 
              px-3 py-2 bg-white 
              dark:bg-gray-700 border 
              border-gray-300 dark:border-gray-600 
              rounded-md shadow-sm focus:outline-none 
              focus:ring-indigo-500 focus:border-indigo-500 
              sm:text-sm">
      </div>

      <div>
        <label for="productDescription" 
        class="block text-sm font-medium 
        text-gray-700 
        dark:text-gray-300">Description (Optional)</label>
        <textarea id="productDescription" 
        v-model.trim="product.description" rows="4"
                  class="mt-1 
                  block w-full px-3 py-2 
                  bg-white dark:bg-gray-700 
                  border border-gray-300 
                  dark:border-gray-600 
                  rounded-md shadow-sm 
                  focus:outline-none 
                  focus:ring-indigo-500 
                  focus:border-indigo-500 
                  sm:text-sm">
        </textarea>
      </div>

      <div>
        <label for="productPrice" 
        class="block text-sm 
        font-medium text-gray-700 
        dark:text-gray-300">Price
        </label>
        <input 
        type="number" 
        id="productPrice" 
        v-model.number="product.price" 
        required step="0.01" min="0.01"
        class="mt-1 block w-full 
        px-3 py-2 bg-white 
        dark:bg-gray-700 border 
        border-gray-300 
        dark:border-gray-600 
        rounded-md shadow-sm focus:outline-none 
        focus:ring-indigo-500 
        focus:border-indigo-500 sm:text-sm">
      </div>

       <div>
        <label for="productCategory" class="block text-sm font-medium text-gray-700 dark:text-gray-300">Category</label>
        <select id="productCategory" v-model="product.category_id"
                class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 dark:border-gray-600 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
          <option :value="null">-- Select a Category --</option>
          <option v-for="category in categories" :key="category.id" :value="category.id">
            {{ category.name }}
          </option>
        </select>
      </div>

      <div>
        <label 
        for="productImage" 
        class="block text-sm 
        font-medium text-gray-700 
        dark:text-gray-300">Change Product Image (Optional)</label>
        <input 
        type="file" 
        id="productImage" 
        @change="handleImageUpload" 
        accept="image/png, image/jpeg, image/webp"
        class="mt-1 block w-full text-sm text-gray-500 
        dark:text-gray-400
                      file:mr-4 file:py-2 file:px-4
                      file:rounded-md file:border-0
                      file:text-sm file:font-semibold
                      file:bg-indigo-50 dark:file:bg-gray-700 
                      file:text-indigo-700 
                      dark:file:text-indigo-300
                      hover:file:bg-indigo-100 dark:hover:file:bg-gray-600">
        <p v-if="productImageFile" 
        class="text-xs 
        text-gray-500 mt-1">New image selected: {{ productImageFile.name }}</p>
        
        <div v-if="product.image_url && !productImageFile" class="mt-4"> 
          <p class="text-sm text-gray-500 dark:text-gray-400">Current Image:</p>

          <img :src=" (product.image_url.startsWith('http') ? product.image_url : 'http://127.0.0.1:8000' + product.image_url) " 
               alt="Current Product Image" 
               class="w-32 h-32 object-cover rounded-md border border-gray-300 dark:border-gray-600">
        </div>
      </div>

      <!-- Ensure only one message (error or success) is shown -->
      <div v-if="error" 
      class="bg-red-100 border 
      border-red-400 text-red-700 
      px-4 py-3 rounded" role="alert">
        <span class="block sm:inline"> {{ error }}</span>
      </div>
      <div v-else-if="successMessage" 
      class="bg-green-100 border 
      border-green-400 text-green-700 
      px-4 py-3 rounded" role="alert">
        <span class="block sm:inline"> {{ successMessage }}</span>
      </div>

      <div>
        <button type="submit" :disabled="isSaving"
                class="w-full flex justify-center 
                py-2 px-4 border border-transparent 
                rounded-md shadow-sm text-sm font-medium 
                text-white bg-indigo-600 hover:bg-indigo-700 
                focus:outline-none focus:ring-2 focus:ring-offset-2 
                focus:ring-indigo-500 disabled:opacity-50">
          <span v-if="isSaving" 
          class="animate-spin 
          rounded-full h-5 w-5 
          border-b-2 
          border-white mr-2"></span>
          {{ isSaving ? 'Saving...' : 'Save Changes' }}
        </button>
      </div>
    </form>
     <div v-else-if="error" 
     class="bg-red-100 border-l-4 
     border-red-500 text-red-700 p-6 
     rounded-md shadow-md" 
     role="alert">
      <p class="font-bold text-lg">Error loading product for editing.</p>
      <p>{{ error }}</p>
    </div>
  </div>
</template>

<style scoped>
/* Scoped styles if needed */
</style>