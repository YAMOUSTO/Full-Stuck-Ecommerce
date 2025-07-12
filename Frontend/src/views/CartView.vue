<script setup>
import { useCartStore } from '@/stores/cart';
import { RouterLink } from 'vue-router';

const cartStore = useCartStore();

</script>

<template>
  <div class="container mx-auto p-4">
    <h1 class="text-3xl font-bold text-center my-6 text-gray-800 dark:text-gray-100">Your Shopping Cart</h1>

    <div v-if="cartStore.items.length === 0" class="text-center py-10">
      <p class="text-xl text-gray-500 dark:text-gray-400">Your cart is empty.</p>
      <RouterLink to="/products" class="mt-4 inline-block bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2 px-6 rounded-lg transition-colors">
        Continue Shopping
      </RouterLink>
    </div>

    <div v-else class="bg-white dark:bg-gray-800 shadow-lg rounded-lg p-6">
      <!-- Cart Items -->
      <div v-for="item in cartStore.items" :key="item.product.id" class="flex flex-col sm:flex-row items-center justify-between py-4 border-b border-gray-200 dark:border-gray-700 last:border-b-0">
        <div class="flex items-center mb-4 sm:mb-0">
          <div class="w-20 h-20 bg-gray-200 dark:bg-gray-700 rounded-md mr-4 flex items-center justify-center text-gray-400">
            <img v-if="item.product.image_url" :src="`http://127.0.0.1:8000${item.product.image_url}`" :alt="item.product.name" class="w-full h-full object-cover rounded-md">
            <span v-else>No Image</span>
          </div>
          <div>
            <h2 class="text-lg font-semibold text-gray-900 dark:text-white">{{ item.product.name }}</h2>
            <p class="text-sm text-gray-600 dark:text-gray-400">${{ item.product.price.toFixed(2) }} each</p>
          </div>
        </div>

        <div class="flex items-center space-x-3">
          <label :for="`quantity-${item.product.id}`" class="text-sm font-medium text-gray-700 dark:text-gray-300">Qty:</label>
          <input type="number" :id="`quantity-${item.product.id}`" :value="item.quantity" 
                @input="cartStore.updateQuantity(item.product.id, parseInt($event.target.value) || 0)" 
                min="0" 
                class="w-16 px-2 py-1 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
          <button @click="cartStore.removeItemFromCart(item.product.id)" class="text-red-500 hover:text-red-700 dark:hover:text-red-400 font-semibold">
            Remove
          </button>
        </div>
        <div class="text-right font-semibold text-gray-900 dark:text-white w-full sm:w-auto mt-2 sm:mt-0">
          ${{ (item.product.price * item.quantity).toFixed(2) }}
        </div>
      </div>

      <!-- Cart Summary & Actions -->
      <div class="mt-8 pt-6 border-t border-gray-200 dark:border-gray-700">
        <div class="flex justify-between items-center mb-4">
          <p class="text-xl font-semibold text-gray-900 dark:text-white">Total:</p>
          <p class="text-2xl font-bold text-indigo-600 dark:text-indigo-400">${{ cartStore.cartTotalPrice.toFixed(2) }}</p>
        </div>
        <div class="flex flex-col sm:flex-row justify-end space-y-2 sm:space-y-0 sm:space-x-4">
          <button @click="cartStore.clearCart()" class="px-6 py-2 border border-red-500 text-red-500 hover:bg-red-500 hover:text-white rounded-lg font-semibold transition-colors">
            Clear Cart
          </button>
      <!--    <button class="px-6 py-2 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-lg transition-colors">
            Proceed to Checkout
          </button>
          -->

          <router-link to="/checkout" class="block text-center px-6 py-2 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-lg transition-colors">
            Proceed to Checkout
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Add any specific styles for the cart view */
</style>