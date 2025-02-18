import { createRouter, createWebHistory } from "vue-router";
import SubmitView from "./views/SubmitView.vue";
import ReportView from "./views/ReportView.vue";
import SettingsView from "./views/SettingsView.vue";

const routes = [
  { path: "/", redirect: "/submit" },
  { path: "/submit", component: SubmitView },
  { path: "/report", component: ReportView },
  { path: "/settings", component: SettingsView },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
