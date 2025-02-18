<template>
    <div class="container-fluid py-3">
        <h4 class="mb-3">Просмотр отчётов</h4>

        <p v-if="!tg" class="text-danger">
            Telegram WebApp недоступен — не можем загрузить задачи.
        </p>

        <!-- Фильтр по типу (серверный) -->
        <div class="row mb-3">
            <div class="col-12 col-md-6 col-lg-4">
                <label class="form-label fw-bold">Фильтр задач</label>
                <select class="form-select" v-model="selectedFilter" @change="onFilterChange">
                    <option value="my">Мои задачи</option>
                    <option v-if="isAdmin" value="admin_all">Все (где я админ)</option>
                    <option v-if="isAdmin" v-for="g in adminGroups" :key="g.id" :value="`group_${g.id}`">
                        Группа #{{ g.id }} ({{ g.name }})
                    </option>
                </select>
            </div>
        </div>

        <div class="table-responsive" v-if="tasks.length">
            <table class="table table-bordered table-hover table-sm align-middle">
                <thead class="table-light">
                    <tr>
                        <!-- Порядок столбцов: ID, Название, Описание, Создал, Время, Дата, Группа, Создано -->
                        <th @click="sortBy('id')" class="cursor-pointer">ID</th>
                        <th @click="sortBy('title')" class="cursor-pointer">Название</th>
                        <th @click="sortBy('description')" class="cursor-pointer">Описание</th>

                        <!-- Столбец "Создал" через компонент -->
                        <th>
                            <CreatorFilterDropdown v-model="selectedCreatorFilter" :items="uniqueCreators"
                                @title-click="sortBy('creator_name')" />
                        </th>

                        <th @click="sortBy('time_spent')" class="cursor-pointer">Время (ч)</th>
                        <th @click="sortBy('task_date')" class="cursor-pointer">Дата</th>
                        <!-- Изменили название столбца и содержимое: теперь выводим название группы -->
                        <th @click="sortBy('group_name')" class="cursor-pointer">Группа</th>
                        <th @click="sortBy('created_at')" class="cursor-pointer">Создано</th>
                    </tr>
                </thead>

                <tbody>
                    <tr v-for="(row, idx) in finalFilteredTasks" :key="row.id + '_' + idx">
                        <td>{{ row.id }}</td>
                        <td>{{ row.title }}</td>
                        <td>{{ row.description }}</td>
                        <td>{{ row.creator_name || '(нет)' }}</td>
                        <td>{{ row.time_spent }}</td>
                        <td>{{ row.task_date }}</td>
                        <td>{{ row.group_id ? groupNamesMap[row.group_id] : '-' }}</td>
                        <td>{{ row.created_at }}</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <p v-else class="text-muted">Нет задач для отображения.</p>
    </div>
</template>

<script>
import CreatorFilterDropdown from "../components/CreatorFilterDropdown.vue";

export default {
    name: "ReportView",
    components: {
        CreatorFilterDropdown,
    },
    data() {
        return {
            tg: null,
            initData: "",
            tasks: [],
            allGroups: [],       // Список всех групп
            // Фильтрация (сервер)
            isAdmin: false,
            adminGroups: [],
            selectedFilter: "my", // "my" | "admin_all" | "group_XXX"
            // Локальный фильтр по "Создал"
            selectedCreatorFilter: "",
            // Сортировка
            sortKey: "",
            sortAsc: true,
        };
    },
    async mounted() {
        if (window.Telegram && window.Telegram.WebApp) {
            this.tg = window.Telegram.WebApp;
            this.initData = this.tg.initData || "";
        }
        
        await this.checkAdminStatus();
        await this.loadAllGroups();
        await this.loadTasks();
    },
    methods: {
        async checkAdminStatus() {
            if (!this.initData) return;
            try {
                const resp = await fetch("/api/groups/my?role=admin", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ init_data: this.initData }),
                });
                const data = await resp.json();
                if (Array.isArray(data) && data.length > 0) {
                    this.isAdmin = true;
                    this.adminGroups = data;
                } else {
                    this.isAdmin = false;
                    this.adminGroups = [];
                }
            } catch (err) {
                console.error("Ошибка проверки админ-статуса:", err);
            }
        },
        async loadAllGroups() {
            try {
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
                console.error("Ошибка при получении всех групп:", err);
            }
        },
        async loadTasks() {
            if (!this.initData) return;
            let filterMode = "my";
            let groupId = null;
            if (this.selectedFilter === "my") {
                filterMode = "my";
            } else if (this.selectedFilter === "admin_all") {
                filterMode = "admin_all";
            } else if (this.selectedFilter.startsWith("group_")) {
                filterMode = "group";
                groupId = Number(this.selectedFilter.split("_")[1]);
            }
            const payload = {
                init_data: this.initData,
                filter_mode: filterMode,
                group_id: groupId,
            };
            try {
                const resp = await fetch("/api/tasks/report/filter", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload),
                });
                if (!resp.ok) {
                    const errorData = await resp.json();
                    alert("Ошибка загрузки задач: " + (errorData.detail || resp.status));
                    return;
                }
                this.tasks = await resp.json();
                this.selectedCreatorFilter = "";
            } catch (err) {
                console.error("Ошибка загрузки отчетов:", err);
                alert("Ошибка загрузки отчетов");
            }
        },
        onFilterChange() {
            this.loadTasks();
        },
        sortBy(key) {
            if (this.sortKey === key) {
                this.sortAsc = !this.sortAsc;
            } else {
                this.sortKey = key;
                this.sortAsc = true;
            }
        },
    },
    computed: {
        groupNamesMap() {
            // Создаем объект: { group_id: group.name, ... }
            const map = {};
            for (const group of this.allGroups) {
                map[group.id] = group.name;
            }
            return map;
        },
        uniqueCreators() {
            const setNames = new Set();
            for (const t of this.tasks) {
                if (t.creator_name) {
                    setNames.add(t.creator_name);
                }
            }
            return [...setNames];
        },
        finalFilteredTasks() {
            let filtered = this.tasks;
            if (this.selectedCreatorFilter) {
                filtered = filtered.filter(
                    (t) => t.creator_name === this.selectedCreatorFilter
                );
            }
            if (!this.sortKey) return filtered;
            return [...filtered].sort((a, b) => {
                let valA = a[this.sortKey];
                let valB = b[this.sortKey];
                if (typeof valA === "string") valA = valA.toUpperCase();
                if (typeof valB === "string") valB = valB.toUpperCase();
                if (valA < valB) return this.sortAsc ? -1 : 1;
                if (valA > valB) return this.sortAsc ? 1 : -1;
                return 0;
            });
        },
    },
};
</script>

<style scoped>
.table-responsive {
    overflow-x: auto !important;
    overflow-y: visible !important;
}

.cursor-pointer {
    cursor: pointer;
}
</style>