<template>
    <div class="container-fluid py-3">
        <div class="row justify-content-center">
            <div class="col-12 col-md-6 col-lg-5">

                <h4 class="mb-3">Сдача отчётности</h4>

                <!-- Если нет Telegram WebApp (может быть запущено вне телеги) -->
                <p v-if="!tg" class="text-danger">
                    Telegram WebApp недоступен - идентификация не работает
                </p>

                <form @submit.prevent="onSubmit">
                    <!-- Выбор группы -->
                    <div class="mb-3">
                        <label class="form-label fw-bold">Группа</label>
                        <select v-model="selectedGroupId" class="form-select">
                            <option v-for="g in groups" :key="g.id" :value="g.id">
                                {{ g.name }}
                            </option>

                            <!-- "Без группы" -->
                            <option :value="null">Без группы</option>
                        </select>
                    </div>

                    <div class="mb-3">
                        <label class="form-label fw-bold">Название</label>
                        <input type="text" class="form-control" v-model="title" required
                            placeholder="Например: Разработка функционала" />
                    </div>

                    <div class="mb-3">
                        <label class="form-label fw-bold">Описание</label>
                        <textarea class="form-control" v-model="description" @input="autoResizeTextarea"
                            placeholder="Краткое описание проделанной работы"></textarea>
                    </div>

                    <div class="mb-3">
                        <label class="form-label fw-bold">Затрачено времени (ч)</label>
                        <input type="number" step="0.1" class="form-control" v-model.number="timeSpent"
                            placeholder="0.5, 1.0, 2.5 и т.д." />
                    </div>

                    <div class="mb-3">
                        <label class="form-label fw-bold">Дата выполнения</label>
                        <input type="date" class="form-control" v-model="taskDate" />
                    </div>

                    <button class="btn btn-success w-100" type="submit">
                        Сохранить
                    </button>
                </form>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: "SubmitView",
    data() {
        return {
            tg: null,
            initData: "",
            groups: [],
            selectedGroupId: null, // по умолчанию
            title: "",
            description: "",
            timeSpent: null,
            taskDate: "",
        };
    },
    async mounted() {
        if (window.Telegram && window.Telegram.WebApp) {
            this.tg = window.Telegram.WebApp;
            this.initData = this.tg.initData || "";
        }

        await this.fetchGroups();
        this.setupDefaultGroup();
    },
    methods: {
        async fetchGroups() {
            if (!this.initData) return;
            try {
                const resp = await fetch("/api/groups/my?role=member", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ init_data: this.initData }),
                });
                this.groups = await resp.json();
            } catch (err) {
                console.error("Ошибка при получении групп:", err);
            }
        },
        setupDefaultGroup() {
            // Если есть хотя бы одна группа, выберем первую
            if (this.groups.length > 0) {
                this.selectedGroupId = this.groups[0].id;
            } else {
                // Иначе без группы
                this.selectedGroupId = null;
            }
        },
        autoResizeTextarea(e) {
            e.target.style.height = "auto";
            e.target.style.height = e.target.scrollHeight + "px";
        },
        async onSubmit() {
            const payload = {
                title: this.title,
                description: this.description,
                time_spent: this.timeSpent,
                task_date: this.taskDate,
                init_data: this.initData,
                group_id: this.selectedGroupId,
            };
            try {
                const resp = await fetch("/api/tasks", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify(payload),
                });
                if (!resp.ok) {
                    const errorData = await resp.json();
                    alert("Ошибка сохранения: " + (errorData.detail || resp.statusText));
                    return;
                }
                const data = await resp.json();
                alert(`Задача сохранена (ID: ${data.task_id}).`);

                // Сброс формы
                this.title = "";
                this.description = "";
                this.timeSpent = null;
                this.taskDate = "";
                // Снова выберем первую группу, если есть
                this.setupDefaultGroup();
            } catch (err) {
                console.error("Ошибка при сохранении задачи:", err);
                alert("Ошибка при сохранении задачи");
            }
        },
    },
};
</script>

<style scoped>
textarea {
    resize: none;
    overflow: hidden;
}
</style>