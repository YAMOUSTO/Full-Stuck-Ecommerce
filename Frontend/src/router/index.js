import { createRouter, createWebHistory } from 'vue-router';
import ProductListView from '../views/ProductList.vue';
import CreateProductView from '../views/CreateProduct.vue'; 
import ProductDetailView from '../views/ProductDetail.vue'; 
import EditProductView from '../views/EditProduct.vue';
import RegisterView from '../views/RegisterView.vue'; 
import LoginView from '../views/LoginView.vue'; 
import CartView from '@/views/CartView.vue';
import UserProfileView from '../views/UserProfileView.vue';
import CheckoutView from '../views/CheckoutView.vue';
import OrderHistoryView from '../views/OrderHistoryView.vue';
import OrderDetailView from '../views/OrderDetailView.vue';


const routes = [
  { path: '/register', name: 'Register', component: RegisterView },
  { path: '/login', name: 'Login', component: LoginView },
  {
    path: '/products',
    name: 'ProductList',
    component: ProductListView
  },
  {
    path: '/orders',
    name: 'OrderHistory',
    component: OrderHistoryView,
    meta: { requiresAuth: true } // Protected route
  },
  {
    path: '/orders/:id',
    name: 'OrderDetail',
    component: OrderDetailView,
    meta: { requiresAuth: true } // Protected route
  },
   {
    path: '/cart',
    name: 'Cart',
    component: CartView
  },
  {
    path: '/checkout',
    name: 'Checkout',
    component: CheckoutView,
    meta: { requiresAuth: true } // Checkout should require login
  },
  {
    path: '/products/create',
    name: 'CreateProduct',
    component: CreateProductView,
    meta: {
      requiresAuth: true 
    }
  },

  {
    path: '/products/:id', 
    name: 'ProductDetail',
    component: ProductDetailView,
    props: true 
  },
  {
    path: '/products/:id/edit', 
    name: 'EditProduct',
    component: EditProductView,
    meta: {
      requiresAuth: true // This route requires authentication
    },
    props: true 
  },
  {
    path: '/',
    redirect: '/products'
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/products'
  },
  {
    path: '/profile',
    name: 'UserProfile',
    component: UserProfileView,
    meta: { requiresAuth: true } // PROTECTED ROUTE
  }
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
});

import { getToken } from '@/services/auth'; 

router.beforeEach((to, from, next) => {
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth);
  const isLoggedIn = !!getToken(); 

  console.log(`Router Guard: Navigating to ${to.path}, requiresAuth: ${requiresAuth}, isLoggedIn: ${isLoggedIn}`);

  if (requiresAuth && !isLoggedIn) {
    console.log(`Router Guard: Access to ${to.path} denied. Redirecting to login.`);
    next({
      name: 'Login',
      query: { redirect: to.fullPath } 
                                      
    });
  } else if ((to.name === 'Login' || to.name === 'Register') && isLoggedIn) {
   
    console.log(`Router Guard: Logged-in user tried to access ${to.name}. Redirecting to products.`);
    next({ name: 'ProductList' });
  }
  else {
    
    next();
  }
});

export default router;