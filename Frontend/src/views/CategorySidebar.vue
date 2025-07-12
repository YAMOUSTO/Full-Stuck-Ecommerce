<script setup>
import { onMounted } from 'vue'
import { useCategoryStore } from '@/stores/categoryStore' // Adjust path if needed

// 1. Get a reference to our Pinia store
const store = useCategoryStore()

// 2. When the component is first created, tell the store to fetch the data
onMounted(() => {
  store.fetchCategories()
})
</script>

<template>
  <div class="p-4 bg-gray-100 rounded-lg">
    <h3 class="text-lg font-bold mb-3">Shop by Category</h3>
    
    <!-- Show a loading message -->
    <div v-if="store.loading">Loading categories...</div>

    <!-- Show the list of categories -->
    <ul v-else class="space-y-2">
      <li v-for="category in store.categories" :key="category.id">
        <!-- 
          Each category is a link. When clicked, it will navigate to a page
          showing products for that category. We will build this page later.
        -->
        <router-link 
          :to="`/category/${category.id}`" 
          class="text-gray-700 hover:text-blue-600 hover:underline"
        >
          {{ category.name }}
        </router-link>
      </li>
    </ul>
  </div>
</template>

