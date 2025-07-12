// frontend/src/stores/cart.js
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export const useCartStore = defineStore('cart', () => {
  // --- State ---
  const items = ref([]); // Array to hold cart items: [{ product, quantity }, ...]

  // --- Getters (Computed Properties) ---
  const cartItemCount = computed(() => {
    return items.value.reduce((total, item) => total + item.quantity, 0);
  });

  const cartTotalPrice = computed(() => {
    return items.value.reduce((total, item) => {
      return total + (item.product.price * item.quantity);
    }, 0);
  });

  // --- Actions (Methods) ---
  function addProductToCart(product, quantity = 1) {
    const existingItem = items.value.find(item => item.product.id === product.id);

    if (existingItem) {
      existingItem.quantity += quantity;
      console.log(`Increased quantity for ${product.name} to ${existingItem.quantity}`);
    } else {
      items.value.push({ product: { ...product }, quantity }); // Store a copy of product
      console.log(`Added ${quantity} of ${product.name} to cart`);
    }
    // Optional: Persist cart to localStorage
    // saveCartToLocalStorage();
  }

  function updateQuantity(productId, newQuantity) {
    const item = items.value.find(item => item.product.id === productId);
    if (item) {
      if (newQuantity > 0) {
        item.quantity = newQuantity;
      } else {
        // If quantity is 0 or less, remove the item
        removeItemFromCart(productId);
      }
    }
    // saveCartToLocalStorage();
  }

  function removeItemFromCart(productId) {
    items.value = items.value.filter(item => item.product.id !== productId);
    console.log(`Removed product ID ${productId} from cart`);
    // saveCartToLocalStorage();
  }

  function clearCart() {
    items.value = [];
    console.log('Cart cleared');
    // saveCartToLocalStorage();
  }

  // --- Optional: Persistence with localStorage ---
  // function saveCartToLocalStorage() {
  //   localStorage.setItem('shoppingCart', JSON.stringify(items.value));
  // }

  // function loadCartFromLocalStorage() {
  //   const savedCart = localStorage.getItem('shoppingCart');
  //   if (savedCart) {
  //     items.value = JSON.parse(savedCart);
  //   }
  // }

  // Load cart when store is initialized (optional)
  // onMounted(() => { // Or just call it directly if onMounted isn't appropriate here
  //  loadCartFromLocalStorage();
  // });
  // Simpler: just call it if you want to load on store creation (runs once)
  // if (typeof window !== 'undefined') { // Ensure localStorage is available
  //    loadCartFromLocalStorage();
  // }


  return {
    items,
    addProductToCart,
    updateQuantity,
    removeItemFromCart,
    clearCart,
    cartItemCount,
    cartTotalPrice,
    // loadCartFromLocalStorage, // Expose if you want to call it from elsewhere too
  };
});