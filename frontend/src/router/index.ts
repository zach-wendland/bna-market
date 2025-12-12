import { createRouter, createWebHistory } from 'vue-router';
import type { RouteRecordRaw } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('@/views/DashboardView.vue'),
    meta: { title: 'Dashboard - BNA Market' }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue'),
    meta: {
      requiresGuest: true,
      title: 'Login - BNA Market'
    }
  },
  {
    path: '/auth/callback',
    name: 'AuthCallback',
    component: () => import('@/views/AuthCallbackView.vue'),
    meta: { title: 'Authenticating - BNA Market' }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/ProfileView.vue'),
    meta: {
      requiresAuth: true,
      title: 'Profile - BNA Market'
    }
  },
  {
    path: '/lists',
    name: 'PropertyLists',
    component: () => import('@/views/PropertyListsView.vue'),
    meta: {
      requiresAuth: true,
      title: 'My Lists - BNA Market'
    }
  },
  {
    path: '/lists/:id',
    name: 'PropertyListDetail',
    component: () => import('@/views/PropertyListDetailView.vue'),
    meta: {
      requiresAuth: true,
      title: 'List Detail - BNA Market'
    }
  },
  {
    path: '/tools',
    name: 'Tools',
    component: () => import('@/views/ToolsView.vue'),
    meta: { title: 'Pricing Tools - BNA Market' }
  },
  {
    path: '/crm',
    name: 'CRM',
    component: () => import('@/views/CRMView.vue'),
    meta: {
      requiresAuth: true,
      title: 'CRM - BNA Market'
    }
  },
  {
    path: '/comps',
    name: 'Comps',
    component: () => import('@/views/CompsView.vue'),
    meta: {
      requiresAuth: true,
      title: 'Property Comps - BNA Market'
    }
  },
  {
    path: '/portfolio',
    name: 'Portfolio',
    component: () => import('@/views/PortfolioView.vue'),
    meta: {
      requiresAuth: true,
      title: 'Portfolio - BNA Market'
    }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFoundView.vue'),
    meta: { title: '404 - BNA Market' }
  }
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(_, __, savedPosition) {
    if (savedPosition) {
      return savedPosition;
    } else {
      return { top: 0 };
    }
  }
});

// Navigation guards for authentication
router.beforeEach((to, _, next) => {
  const authStore = useAuthStore();

  // Update page title
  if (to.meta.title) {
    document.title = to.meta.title as string;
  }

  // Check if route requires authentication
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    console.log('Route requires auth, redirecting to login');
    next({
      name: 'Login',
      query: { redirect: to.fullPath }
    });
  }
  // Check if route requires guest (e.g., login page)
  else if (to.meta.requiresGuest && authStore.isAuthenticated) {
    console.log('Route requires guest, redirecting to dashboard');
    next({ name: 'Dashboard' });
  }
  // Allow navigation
  else {
    next();
  }
});

// Global error handler
router.onError((error) => {
  console.error('Router error:', error);
});

export default router;
