import { defineStore } from 'pinia'
import axios from 'axios'

export const useCategoryStore = defineStore('category', {
  state: () => ({
    categories: [], // This will hold our list of categories
    loading: false,
  }),

  actions: {
    async fetchCategories() {
      if (this.categories.length > 0) return; // Don't fetch if we already have them

      this.loading = true
      try {
        // Ask our Python backend for the categories
        const response = await axios.get('http://localhost:8000/api/categories')
        this.categories = response.data
      } catch (error) {
        console.error('Failed to fetch categories:', error)
        // Here you could set an error state to show a message to the user
      } finally {
        this.loading = false
      }
    },
  },
})