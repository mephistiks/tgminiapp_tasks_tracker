<template>
    <div class="d-inline-block position-relative">
        <!-- Название столбца (по клику родитель может сортировать) -->
        <span class="cursor-pointer" @click.stop="onTitleClick">
            Создал
        </span>

        <!-- Кнопка-иконка "…" -->
        <button class="btn btn-sm btn-light ms-2 cursor-pointer" style="vertical-align: middle;"
            @click.stop="toggleMenu">
            …
        </button>

        <!-- Выпадающее меню -->
        <div v-if="showMenu" ref="menu" class="dropdown-menu-custom">
            <ul class="list-group list-group-flush m-0 p-0">
                <li class="list-group-item py-1 px-2 cursor-pointer" @click="selectItem('')">
                    Все
                </li>
                <li v-for="name in sortedItems" :key="name" class="list-group-item py-1 px-2 cursor-pointer"
                    @click="selectItem(name)">
                    {{ name }}
                </li>
            </ul>
        </div>
    </div>
</template>

<script>
/*
  Компонент-обёртка для столбца "Создал" с кнопкой вызова 
  локального фильтра (списка пользователей).
  
  При клике на заголовок "Создал" вызывается @title-click 
  (чтобы родитель мог выполнить сортировку).
  
  При выборе "Все" или конкретного имени генерирует 
  update:modelValue, тем самым обновляя локальный фильтр 
  в родительском компоненте.
*/
export default {
    name: "CreatorFilterDropdown",
    props: {
        modelValue: {
            type: String,
            default: "",
        },
        items: {
            type: Array,
            default: () => [],
        },
    },
    data() {
        return {
            showMenu: false,
        };
    },
    computed: {
        sortedItems() {
            return [...this.items].sort();
        },
    },
    mounted() {
        // Ловим клик вне элемента, чтобы закрыть меню
        document.addEventListener("click", this.handleOutsideClick);
    },
    beforeUnmount() {
        document.removeEventListener("click", this.handleOutsideClick);
    },
    methods: {
        toggleMenu() {
            this.showMenu = !this.showMenu;
        },
        selectItem(name) {
            this.$emit("update:modelValue", name);
            this.showMenu = false;
        },
        handleOutsideClick(event) {
            if (!this.showMenu) return;
            const menuEl = this.$refs.menu;
            if (menuEl && !menuEl.contains(event.target)) {
                this.showMenu = false;
            }
        },
        onTitleClick() {
            this.$emit("title-click");
        },
    },
};
</script>

<style scoped>
.cursor-pointer {
    cursor: pointer;
}

/* Выпадающее меню */
.dropdown-menu-custom {
    position: absolute;
    top: 100%;
    right: 0;
    z-index: 999;
    background-color: #fff;
    border: 1px solid #ccc;
    padding: 0.25rem;
    border-radius: 0.25rem;

    /* Чтобы автоматически подстраиваться под самую длинную строку */
    display: inline-block;
    width: fit-content;
    white-space: nowrap;
}

.list-group-item.cursor-pointer:hover {
    background-color: #f8f9fa;
}
</style>