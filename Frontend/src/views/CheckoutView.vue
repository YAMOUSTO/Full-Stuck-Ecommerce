<script setup>
import { reactive, ref } from 'vue';
import { useCartStore } from '@/stores/cart';
import { useRouter } from 'vue-router';
import { createOrder } from '@/services/api';
import { useToast } from 'vue-toastification';


const toast = useToast();
const cartStore = useCartStore();
const router = useRouter();

const shippingDetails = reactive({
  address_line1: '',
  city: '',
  postal_code: '',
  country: 'USA', // Default value
});

const isProcessing = ref(false);
const error = ref(null);

// Redirect away if cart is empty
if (cartStore.items.length === 0) {
  router.push('/products');
}

const handlePlaceOrder = async () => {
  // Basic validation
  if (!shippingDetails.address_line1 || !shippingDetails.city || !shippingDetails.postal_code || !shippingDetails.country) {
    error.value = "All shipping fields are required.";
    return;
  }

  isProcessing.value = true;
  error.value = null;

  try {
    const orderPayload = {
      shipping_address_line1: shippingDetails.address_line1,
      shipping_city: shippingDetails.city,
      shipping_postal_code: shippingDetails.postal_code,
      shipping_country: shippingDetails.country,
      items: cartStore.items.map(item => ({
        product_id: item.product.id,
        quantity: item.quantity
      }))
    };
    
    const response = await createOrder(orderPayload);
    console.log("Order created successfully:", response.data);

    // Order was successful, clear the cart
    cartStore.clearCart();

    // alert(`Order #${response.data.id} placed successfully!`);
     toast.success(`Order #${response.data.id} placed successfully!`); 
    router.push('/');

  } catch (err) {
    console.error("Error placing order:", err);
    if (err.response?.data?.detail) {
      error.value = `Failed to place order: ${err.response.data.detail}`;
      toast.error(error.value || 'Failed to place order.');
    } else {
      error.value = `Failed to place order: ${err.message || 'An unexpected error occurred.'}`;
    }
  } finally {
    isProcessing.value = false;
  }
};
</script>

<template>
  <div class="container mx-auto p-4 max-w-4xl">
    <h1 class="text-3xl font-bold text-center my-6 text-gray-800 dark:text-gray-100">Checkout</h1>
    
    <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
      <!-- Shipping Details Form -->
      <div class="bg-white dark:bg-gray-800 shadow-lg rounded-lg p-6">
        <h2 class="text-xl font-semibold mb-4">Shipping Information</h2>
        <form @submit.prevent="handlePlaceOrder" class="space-y-4">
          <div>
            <label for="address" class="block text-sm font-medium text-gray-700 dark:text-gray-300">Address Line 1</label>
            <input type="text" id="address" v-model="shippingDetails.address_line1" required class="mt-1 block w-full p-2 border dark:bg-gray-700 dark:border-gray-600 rounded-md">
          </div>
          <div>
            <label for="city" class="block text-sm font-medium text-gray-700 dark:text-gray-300">City</label>
            <input type="text" id="city" v-model="shippingDetails.city" required class="mt-1 block w-full p-2 border dark:bg-gray-700 dark:border-gray-600 rounded-md">
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label for="postal_code" class="block text-sm font-medium text-gray-700 dark:text-gray-300">Postal Code</label>
              <input type="text" id="postal_code" v-model="shippingDetails.postal_code" required class="mt-1 block w-full p-2 border dark:bg-gray-700 dark:border-gray-600 rounded-md">
            </div>
            <div>
              <label for="country" class="block text-sm font-medium text-gray-700 dark:text-gray-300">Country</label>
              <input type="text" id="country" v-model="shippingDetails.country" required class="mt-1 block w-full p-2 border dark:bg-gray-700 dark:border-gray-600 rounded-md">
            </div>
          </div>
        </form>
      </div>

      <!-- Order Summary -->
      <div class="bg-white dark:bg-gray-800 shadow-lg rounded-lg p-6">
        <h2 class="text-xl font-semibold mb-4">Order Summary</h2>
        <div v-for="item in cartStore.items" :key="item.product.id" class="flex justify-between items-center py-2 border-b dark:border-gray-700">
          <span class="text-gray-700 dark:text-gray-300">{{ item.product.name }} (x{{ item.quantity }})</span>
          <span class="font-semibold">${{ (item.product.price * item.quantity).toFixed(2) }}</span>
        </div>
        <div class="flex justify-between items-center mt-4 pt-4 border-t dark:border-gray-700">
          <span class="text-xl font-bold">Total</span>
          <span class="text-xl font-bold">${{ cartStore.cartTotalPrice.toFixed(2) }}</span>
        </div>
        <div v-if="error" class="mt-4 bg-red-100 text-red-700 p-3 rounded text-sm">
          {{ error }}
        </div>
        <button @click="handlePlaceOrder" :disabled="isProcessing" class="mt-6 w-full bg-green-600 hover:bg-green-700 text-white font-bold py-3 rounded-lg text-lg transition-colors disabled:opacity-50">
          <span v-if="isProcessing" class="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2 inline-block"></span>
          {{ isProcessing ? 'Placing Order...' : 'Place Order' }}
        </button>
      </div>
    </div>
  </div>
</template>