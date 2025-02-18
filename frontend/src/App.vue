<template>
  <div class="app-container">
    <router-view></router-view>

    <!-- Нижняя навигационная панель (кнопки меньше и подписи короче) -->
    <nav class="navbar navbar-light bg-light fixed-bottom border-top py-1">
      <div class="container d-flex justify-content-around">
        <router-link to="/submit" class="btn btn-primary btn-sm">Отчёт</router-link>
        <router-link to="/report" class="btn btn-secondary btn-sm">Просмотр</router-link>
        <router-link to="/settings" class="btn btn-info btn-sm">Настройки</router-link>
      </div>
    </nav>
  </div>
</template>

<script>
export default {
  name: "App",
  mounted() {
    if (window.Telegram && window.Telegram.WebApp) {
      window.Telegram.WebApp.ready();
    }
  },
};
</script>

<style scoped>
.app-container {
  padding-bottom: 60px; /* Уменьшаем отступ, чтобы кнопки не перекрывали контент */
}
</style>
