<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { fetchProducts, fetchCategories, searchProducts } from '@/services/api';
import { RouterLink } from 'vue-router';
import { useCartStore } from '@/stores/cart';
import { useToast } from 'vue-toastification';
import SkeletonCard from '@/components/SkeletonCard.vue';

// --- State ---
const allProducts = ref([]); // Master list of products
const categories = ref([]);
const selectedCategoryId = ref(null);
const searchQuery = ref('');    
const isSearching = ref(false);     

const loading = ref(true); // For initial page load
const error = ref(null);
const cartStore = useCartStore();
const toast = useToast();

// --- Computed Property for Display ---
const displayedProducts = computed(() => {

  if (!selectedCategoryId.value) {
    return allProducts.value; 
  }
  return allProducts.value.filter(
    product => product.category_id === selectedCategoryId.value
  );
});

// --- Data Fetching and Searching ---
const loadInitialData = async () => {
  loading.value = true;
  error.value = null;
  try {
    const [productsResponse, categoriesResponse] = await Promise.all([
      fetchProducts(),
      fetchCategories()
    ]);
    allProducts.value = productsResponse.data;
    categories.value = categoriesResponse.data;
  } catch (err) {
    console.error('Error loading initial data:', err);
    error.value = err;
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  loadInitialData();
});

const performSearch = async () => {
  // When a search is performed, we clear the category filter
  selectedCategoryId.value = null;

  if (!searchQuery.value.trim()) {
    // If search box is cleared, reload the original full list of products and categories
    await loadInitialData();
    return;
  }

  isSearching.value = true;
  error.value = null;
  try {
    console.log(`Searching for: "${searchQuery.value}"`);
    const response = await searchProducts(searchQuery.value);
    allProducts.value = response.data; 
  } catch (err) {
    console.error('Error during search:', err);
    error.value = err;
    allProducts.value = []; 
  } finally {
    isSearching.value = false;
  }
};

// --- Event Handlers ---
const selectCategory = (categoryId) => {
  if (searchQuery.value.trim() !== '') {
    searchQuery.value = '';
    loadInitialData().then(() => {
        
        selectedCategoryId.value = categoryId;
    });
  } else {
    // Standard category selection
    if (selectedCategoryId.value === categoryId) {
      selectedCategoryId.value = null; // Toggle off
    } else {
      selectedCategoryId.value = categoryId;
    }
  }
};

const handleAddToCart = (product) => {
  cartStore.addProductToCart(product);
  //alert(`${product.name} added to cart!`);
   toast.success(`${product.name} added to cart!`);
};
</script>

<template>
  <div class="container mx-auto p-4">
    <h1 class="text-3xl font-bold text-center my-6 text-gray-800 dark:text-gray-100">Our Products</h1>

    <!-- Search Bar -->
    <div class="max-w-xl mx-auto mb-8">
      <form @submit.prevent="performSearch" class="relative">
        <input type="search" v-model="searchQuery" @search="performSearch" placeholder="Search for products..."
               class="w-full px-5 py-3 text-lg border-2 border-gray-300 dark:border-gray-600 rounded-full focus:ring-indigo-500 focus:border-indigo-500 transition-colors dark:bg-gray-700 dark:text-white" />
        <button type="submit" class="absolute top-0 right-0 mt-2 mr-2 p-2.5 bg-indigo-600 text-white rounded-full hover:bg-indigo-700 focus:outline-none">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd" />
          </svg>
        </button>
      </form>
    </div>
     
    <!-- Category Filter Buttons -->
    <div class="flex justify-center flex-wrap gap-2 mb-8">
      <button 
        @click="selectCategory(null)"
        :class="['px-4 py-2 text-sm font-semibold rounded-full transition-colors', !selectedCategoryId ? 'bg-indigo-600 text-white shadow-md' : 'bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 hover:bg-gray-300 dark:hover:bg-gray-600']">
        All Products
      </button>
      <button 
        v-for="category in categories" 
        :key="category.id" 
        @click="selectCategory(category.id)"
        :class="['px-4 py-2 text-sm font-semibold rounded-full transition-colors', selectedCategoryId === category.id ? 'bg-indigo-600 text-white shadow-md' : 'bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 hover:bg-gray-300 dark:hover:bg-gray-600']">
        {{ category.name }}
      </button>
    </div>

    <!-- Loading State (combined for initial load and searching) -->
<div v-if="loading || isSearching" class="text-center py-10">
  
  <!-- The loading message appears at the top -->
  <p class="text-xl text-gray-500 dark:text-gray-400 mb-6">
    {{ isSearching ? 'Searching for products...' : 'Loading products, please wait...' }}
  </p>

  <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-x-6 gap-y-8">
    <SkeletonCard v-for="n in 8" :key="`skeleton-${n}`" />
    
  </div>

</div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-red-100 border-l-4 border-red-500 text-red-700 p-6 rounded-md shadow-md" role="alert">
      <p class="font-bold text-lg">Oops! Something went wrong.</p>
      <p>Could not load data. {{ error.message }}</p>
    </div>

    <!-- Main Product Grid -->
    <div v-else-if="displayedProducts.length > 0" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-x-6 gap-y-8">
      <div v-for="product in displayedProducts" :key="product.id"
           class="bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden flex flex-col group transform hover:shadow-2xl hover:scale-[1.02] transition-all duration-300">
        
        <router-link :to="{ name: 'ProductDetail', params: { id: product.id } }" class="block cursor-pointer">
          <div class="w-full h-48 bg-gray-200 dark:bg-gray-700 group-hover:opacity-75 transition-opacity">
            <img v-if="product.image_url" :src="`http://127.0.0.1:8000${product.image_url}`" :alt="product.name" class="w-full h-full object-cover">
            <div v-else class="w-full h-full flex items-center justify-center text-gray-400">
              <span>No Image</span>
            </div>
          </div>
        </router-link>
        
        <div class="p-5 flex flex-col flex-grow">
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-2 truncate group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">
            <router-link :to="{ name: 'ProductDetail', params: { id: product.id } }">
              {{ product.name }}
            </router-link>
          </h2>
          
          <p v-if="product.description" class="text-gray-600 dark:text-gray-300 text-sm mb-3 flex-grow h-16 overflow-hidden">
            {{ product.description }}
          </p>
          <p v-else class="text-gray-400 dark:text-gray-500 text-sm mb-3 flex-grow h-16 italic">No description available.</p>
          
          <div class="mt-auto">
            <p class="text-xl font-bold text-indigo-600 dark:text-indigo-400 mb-4">${{ product.price ? product.price.toFixed(2) : 'N/A' }}</p>
            <button @click="handleAddToCart(product)" class="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors duration-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-opacity-50">
              Add to Cart
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- No Products Found State -->
    <div v-else class="text-center py-20">
      <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
        <path vector-effect="non-scaling-stroke" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
      </svg>
      <h3 class="mt-2 text-lg font-medium text-gray-900 dark:text-gray-100">No Products Found</h3>
      <p v-if="searchQuery.trim() !== ''" class="mt-1 text-sm text-gray-500 dark:text-gray-400">
        Your search for "{{ searchQuery }}" did not match any products.
      </p>
      <p v-else class="mt-1 text-sm text-gray-500 dark:text-gray-400">
        There are no products available for the selected category.
      </p>
    </div>
  </div>
</template>

<style scoped>
.h-16 {
  height: 4rem; 
}
</style>