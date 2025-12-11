import { createApp } from 'vue';
import { createPinia } from 'pinia';
import { inject } from '@vercel/analytics';
import router from './router';
import App from './App.vue';
import './assets/main.css';

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);
app.use(router);
app.mount('#app');

// Initialize Vercel Web Analytics
inject();
