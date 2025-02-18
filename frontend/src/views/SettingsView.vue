<template>
    <div class="container py-4">
        <h3 class="mb-4">Настройки</h3>

        <!-- Форма редактирования ФИО -->
        <div class="mb-4">
            <label for="fullName" class="form-label fw-bold">Фамилия Имя</label>
            <input id="fullName" type="text" class="form-control" v-model="fullName"
                placeholder="Введите Фамилию Имя" />
        </div>

        <!-- Секция выбора групп -->
        <div class="mb-4">
            <label class="form-label fw-bold">Присоединиться к группам</label>
            <div v-if="allGroups.length">
                <div v-for="group in allGroups" :key="group.id" class="form-check mb-1">
                    <input class="form-check-input" type="checkbox" :id="'group-' + group.id" :value="group.id"
                        v-model="selectedGroups" />
                    <label class="form-check-label" :for="'group-' + group.id">
                        {{ group.name }}
                    </label>
                </div>
            </div>
            <div v-else>
                <p class="text-muted">Нет доступных групп.</p>
            </div>
        </div>

        <!-- Кнопка сохранения -->
        <button class="btn btn-primary" @click="onSave">Сохранить</button>
    </div>
</template>

<script>
export default {
    name: "SettingsView",
    data() {
        return {
            fullName: "",
            allGroups: [],        // Список всех групп (предполагается, что endpoint GET /api/groups возвращает список)
            selectedGroups: [],   // Массив id выбранных групп
            tg: null,
            initData: "",
            telegramId: "",       // Извлечённый telegram_id из initData
        };
    },
    async mounted() {
        // Инициализация Telegram WebApp
        if (window.Telegram && window.Telegram.WebApp) {
            this.tg = window.Telegram.WebApp;
            this.initData = this.tg.initData || "";
            this.telegramId = this.extractTelegramId(this.initData);
        }
        
        this.telegramId = this.extractTelegramId(this.initData);

        await this.fetchAllGroups();
    },
    methods: {
        extractTelegramId(initData) {
            // Простая реализация аналогичная тому, что используется в бекенде
            try {
                const params = new URLSearchParams(initData);
                const userJson = params.get("user");
                if (userJson) {
                    const userObj = JSON.parse(decodeURIComponent(userJson));
                    return String(userObj.id);
                }
            } catch (err) {
                console.error("Ошибка извлечения telegram_id из initData:", err);
            }
            return "";
        },
        async fetchAllGroups() {
            try {
                // Предполагается, что GET /api/groups возвращает список всех групп
                const resp = await fetch("/api/groups", {
                    method: "GET",
                    headers: { "Content-Type": "application/json" },
                });
                if (!resp.ok) {
                    console.error("Ошибка загрузки групп:", await resp.text());
                    return;
                }
                this.allGroups = await resp.json();
            } catch (err) {
                console.error("Ошибка при получении групп:", err);
            }
        },
        async onSave() {
            if (!this.telegramId) {
                alert("Не удалось определить telegram_id. Проверьте initData.");
                return;
            }
            // Обновляем пользователя (POST /api/user)
            try {
                const userPayload = {
                    telegram_id: this.telegramId,
                    fio: this.fullName,
                };
                const userResp = await fetch("/api/user", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(userPayload),
                });
                if (!userResp.ok) {
                    const errorData = await userResp.json();
                    alert("Ошибка сохранения пользователя: " + (errorData.detail || userResp.status));
                    return;
                }
            } catch (err) {
                console.error("Ошибка при сохранении пользователя:", err);
                alert("Ошибка при сохранении пользователя.");
                return;
            }

            // Для каждого выбранного элемента вызываем PUT /api/groups/members
            try {
                // Для каждого выбранного group id
                for (const groupId of this.selectedGroups) {
                    // Находим группу по id
                    const group = this.allGroups.find(g => g.id === groupId);
                    if (!group) continue;
                    const payload = {
                        group_name: group.name,
                        telegram_id: this.telegramId,
                    };
                    const groupResp = await fetch("/api/groups/members", {
                        method: "PUT",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify(payload),
                    });
                    if (!groupResp.ok) {
                        // Если ошибка, выводим предупреждение и продолжаем
                        const errData = await groupResp.json();
                        console.warn(`Ошибка при присоединении к группе ${group.name}: ${errData.detail || groupResp.status}`);
                    }
                }
            } catch (err) {
                console.error("Ошибка при присоединении к группам:", err);
                alert("Ошибка при присоединении к группам.");
                return;
            }

            alert("Настройки сохранены!");
        },
    },
};
</script>

<style scoped>
/* Простая стилизация для страницы настроек */
.container {
    max-width: 600px;
}
</style>