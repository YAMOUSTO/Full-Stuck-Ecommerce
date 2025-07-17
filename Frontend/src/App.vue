<script setup>
import { RouterView, RouterLink, useRouter } from 'vue-router';
import { authState, logout, attemptFetchCurrentUser } from '@/services/auth';
import { onMounted, watch } from 'vue';
import { useCartStore } from './stores/cart';

const router = useRouter();
const cartStore = useCartStore();

console.log("APP.VUE: authState.isAuthenticated (on setup):", authState.isAuthenticated);
console.log("APP.VUE: authState.currentUser (on setup):", authState.currentUser);


const handleLogout = () => {
  logout(); 
  router.push('/login');
};

onMounted(() => {
  console.log("APP.VUE: Mounted. Attempting to fetch current user...");
  attemptFetchCurrentUser(); 
});

watch(() => authState.isAuthenticated, (newValue, oldValue) => {
  console.log(`APP.VUE: authState.isAuthenticated changed from ${oldValue} to ${newValue}`);
});

watch(() => authState.currentUser, (newValue) => {
    console.log(`APP.VUE: authState.currentUser changed:`, newValue);
}, { deep: true });
</script>

<template>
  <div id="app-container" class="min-h-screen bg-gradient-to-br from-slate-900 to-slate-700 text-slate-100">
    <nav class="p-4 bg-slate-800 shadow-md">
      <div class="container mx-auto flex justify-between items-center">
        <div>
          <RouterLink to="/products" class="text-xl font-bold hover:text-sky-400 transition-colors">E-Shop</RouterLink>
        </div>
        <div class="space-x-4">
          <RouterLink to="/products" class="px-3 py-2 rounded hover:bg-sky-600 transition-colors">Products</RouterLink>
          
          <template v-if="authState.isAuthenticated"> 
            <RouterLink  v-if="authState.currentUser && (authState.currentUser.role === 'admin' || authState.currentUser.role === 'vendor')" to="/products/create" class="px-3 py-2 
            rounded hover:bg-green-600 transition-colors">Add Product</RouterLink>
            <RouterLink to="/profile" class="px-3 py-2 rounded hover:bg-teal-600 transition-colors">My Profile</RouterLink>
             <RouterLink to="/orders" class="px-3 py-2 rounded hover:bg-orange-600 transition-colors">My Orders</RouterLink>
            <span class="text-sm text-gray-300 px-3 py-2">Hi, {{ authState.currentUser?.email || 'User' }}</span> 
            <button @click="handleLogout" class="px-3 py-2 rounded bg-red-600 hover:bg-red-700 transition-colors">Logout</button>
          </template>
          <template v-else>
            <RouterLink to="/login" class="px-3 py-2 rounded hover:bg-blue-600 transition-colors">Login</RouterLink>
            <RouterLink to="/register" class="px-3 py-2 rounded hover:bg-purple-600 transition-colors">Register</RouterLink>
          </template>

           <RouterLink to="/cart" class="relative px-3 py-2 rounded hover:bg-sky-600 transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 inline-block" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
            <span v-if="cartStore.cartItemCount > 0" 
                  class="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
              {{ cartStore.cartItemCount }}
            </span>
          </RouterLink>
        </div>
      </div>
    </nav>
    <main class="container mx-auto p-4 mt-4">
      <RouterView />
    </main>
  </div>
</template>
<!-- style remains the same -->

<style scoped>
.router-link-exact-active {
  color: #38bdf8; /* Tailwind's text-sky-400 */
  font-weight: 600; /* Tailwind's font-semibold */
}
</style>