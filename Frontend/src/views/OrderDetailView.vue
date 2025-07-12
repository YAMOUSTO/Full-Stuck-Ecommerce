<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { fetchOrderById } from '@/services/api';

const route = useRoute();
const order = ref(null);
const loading = ref(true);
const error = ref(null);

const loadOrderDetails = async (orderId) => {
  loading.value = true;
  error.value = null;
  try {
    const response = await fetchOrderById(orderId);
    order.value = response.data;
  } catch (err) {
    console.error("Error fetching order details:", err);
    error.value = err;
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  const orderId = route.params.id;
  if (orderId) {
    loadOrderDetails(orderId);
  }
});

const formatDate = (dateString) => {
  if (!dateString) return '';
  const options = { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' };
  return new Date(dateString).toLocaleString(undefined, options);
};
</script>

<template>
  <div class="container mx-auto p-4 max-w-4xl">
    <!-- Loading and Error states remain the same -->
    <div v-if="loading" class="text-center py-20">
      <p class="text-xl text-gray-500 dark:text-gray-400">Loading Order Details...</p>
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mt-4"></div>
    </div>
    <div v-else-if="error" class="bg-red-100 border-l-4 border-red-500 text-red-700 p-6 rounded-md shadow-md" role="alert">
      <p class="font-bold text-lg">Error</p>
      <p>Could not load order details: {{ error.message }}</p>
    </div>

    <!-- Main Order Details Display -->
    <div v-else-if="order" class="bg-white dark:bg-gray-800 shadow-xl rounded-lg overflow-hidden">
      <!-- Order Header -->
      <div class="p-6 bg-gray-50 dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700">
        <div class="flex flex-col sm:flex-row justify-between items-start">
          <div>
            <h1 class="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white">Order #{{ order.id }}</h1>
            <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">Placed on: {{ formatDate(order.created_at) }}</p>
          </div>
          <div class="mt-4 sm:mt-0 text-left sm:text-right">
             <p class="text-sm font-medium text-gray-500 dark:text-gray-400">Status</p>
             <p :class="['mt-1 inline-block px-3 py-1 text-sm font-semibold rounded-full', order.status === 'pending' ? 'bg-yellow-200 text-yellow-800' : 'bg-green-200 text-green-800']">
              {{ order.status.charAt(0).toUpperCase() + order.status.slice(1) }}
            </p>
          </div>
        </div>
      </div>
      
      <div class="p-6 grid grid-cols-1 md:grid-cols-5 gap-8">
        <!-- Items Ordered Section (takes up 3 columns) -->
        <div class="md:col-span-3">
          <h2 class="text-xl font-semibold mb-4 text-gray-800 dark:text-gray-200">Items Ordered</h2>
          <div class="space-y-4">
            <!-- Loop through items and display nested product info -->
            <div v-for="item in order.items" :key="item.id" class="flex items-start py-4 border-b border-gray-200 dark:border-gray-700 last:border-b-0">
              <!-- Product Image -->
              <div class="flex-shrink-0 w-20 h-20 bg-gray-200 dark:bg-gray-700 rounded-md">
                <img v-if="item.product.image_url" 
                     :src="`http://127.0.0.1:8000${item.product.image_url}`" 
                     :alt="item.product.name" 
                     class="w-full h-full object-cover rounded-md">
                <div v-else class="w-full h-full flex items-center justify-center text-gray-400 text-xs">No Image</div>
              </div>
              
              <!-- Product Info -->
              <div class="ml-4 flex-grow">
                <p class="font-semibold text-gray-900 dark:text-white">{{ item.product.name }}</p>
                <p class="text-sm text-gray-600 dark:text-gray-400">Qty: {{ item.quantity }}</p>
                <p class="text-sm text-gray-600 dark:text-gray-400">Price each: ${{ item.price_at_time_of_purchase.toFixed(2) }}</p>
              </div>
              
              <!-- Item Subtotal -->
              <div class="text-right font-semibold text-gray-900 dark:text-white">
                ${{ (item.price_at_time_of_purchase * item.quantity).toFixed(2) }}
              </div>
            </div>
          </div>
        </div>
        
        <!-- Shipping & Summary Section (takes up 2 columns) -->
        <div class="md:col-span-2">
          <div class="bg-gray-50 dark:bg-gray-900/50 p-6 rounded-lg">
            <h2 class="text-xl font-semibold mb-4 text-gray-800 dark:text-gray-200">Summary</h2>
            <div class="space-y-4">
              <div>
                <h3 class="text-md font-semibold text-gray-800 dark:text-gray-200">Shipping To</h3>
                <address class="not-italic text-gray-700 dark:text-gray-300 mt-1">
                  {{ order.shipping_address_line1 }}<br>
                  {{ order.shipping_city }}, {{ order.shipping_postal_code }}<br>
                  {{ order.shipping_country }}
                </address>
              </div>
              <div class="pt-4 border-t border-gray-200 dark:border-gray-700">
                <div class="flex justify-between items-center text-lg font-bold text-gray-900 dark:text-white">
                  <span>Total:</span>
                  <span>${{ order.total_price.toFixed(2) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div v-else class="text-center py-20">
      <p class="text-xl text-gray-500 dark:text-gray-400">Order not found.</p>
    </div>
  </div>
</template>