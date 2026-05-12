import { createRouter, createWebHistory } from 'vue-router';
import Login from '@/views/Login.vue';
import ViewerUI from '@/views/ViewerUI.vue';
import ManagementUI from '@/views/ManagementUI.vue';
import PatientUI from '@/views/PatientUI.vue';
import { useUserStore } from '@/store/userStore';

const routes = [
    {
        path: '/login',
        name: 'Login',
        component: Login,
        meta: { requiresAuth: false }
    },
    {
        path: '/',
        name: 'ClinicalViewer',
        component: ViewerUI,
        meta: { requiresAuth: true, role: ['admin', 'staff'] }
    },
    {
        path: '/management',
        name: 'Management',
        component: ManagementUI,
        meta: { requiresAuth: true, role: ['admin'] }
    },
    {
        path: '/portal',
        name: 'PatientPortal',
        component: PatientUI,
        meta: { requiresAuth: true, role: ['patient'] }
    }
];

const router = createRouter({
    history: createWebHistory(),
    routes
});

router.beforeEach((to, from, next) => {
    const userStore = useUserStore();

    if (to.meta.requiresAuth && !userStore.isAuthenticated) {
        next({ name: 'Login' });
    } else if (to.meta.role && !to.meta.role.includes(userStore.role)) {
        // Redirect based on role if unauthorized for specific route
        if (userStore.role === 'patient') {
            next({ name: 'PatientPortal' });
        } else {
            next({ name: 'ClinicalViewer' });
        }
    } else {
        next();
    }
});

export default router;
