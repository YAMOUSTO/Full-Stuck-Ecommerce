<script setup>
import { ref, onMounted } from 'vue';
import { fetchOrders } from '@/services/api';
import { RouterLink } from 'vue-router';

const orders = ref([]);
const loading = ref(true);
const error = ref(null);

const loadOrders = async () => {
  loading.value = true;
  error.value = null;
  try {
    const response = await fetchOrders();
    orders.value = response.data;
  } catch (err) {
    console.error("Error fetching order history:", err);
    error.value = err;
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  loadOrders();
});

const formatDate = (dateString) => {
  if (!dateString) return '';
  const options = { year: 'numeric', month: 'long', day: 'numeric' };
  return new Date(dateString).toLocaleDateString(undefined, options);
};
</script>

<template>
  <div class="container mx-auto p-4 max-w-4xl">
    <h1 class="text-3xl font-bold text-center my-6 text-gray-800 dark:text-gray-100">Your Order History</h1>

    <div v-if="loading" class="text-center py-10">... Loading ...</div>
    <div v-else-if="error" class="text-center py-10 text-red-500">... Error loading orders ...</div>
    
    <div v-else-if="orders.length > 0" class="space-y-6">
      <div v-for="order in orders" :key="order.id" class="bg-white dark:bg-gray-800 shadow-md rounded-lg p-6">
        <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center border-b dark:border-gray-700 pb-4 mb-4">
          <div>
            <h2 class="text-xl font-semibold text-gray-900 dark:text-white">Order #{{ order.id }}</h2>
            <p class="text-sm text-gray-500 dark:text-gray-400">Placed on: {{ formatDate(order.created_at) }}</p>
          </div>
          <div class="mt-2 sm:mt-0">
            <span class="text-lg font-bold text-indigo-600 dark:text-indigo-400">${{ order.total_price.toFixed(2) }}</span>
            <span :class="['ml-4 px-3 py-1 text-xs font-semibold rounded-full', order.status === 'pending' ? 'bg-yellow-200 text-yellow-800' : 'bg-green-200 text-green-800']">
              {{ order.status }}
            </span>
          </div>
        </div>
        <div class="flex justify-end">
          <RouterLink :to="{ name: 'OrderDetail', params: { id: order.id } }" class="text-indigo-600 dark:text-indigo-400 hover:underline font-semibold">
            View Details
          </RouterLink>
        </div>
      </div>
    </div>

    <div v-else class="text-center py-20">
      <p class="text-xl text-gray-500 dark:text-gray-400">You have not placed any orders yet.</p>
      <RouterLink to="/products" class="mt-4 inline-block bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2 px-6 rounded-lg">
        Start Shopping
      </RouterLink>
    </div>
  </div>
</template>