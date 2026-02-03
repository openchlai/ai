<template>
  <aside class="h-screen w-64 bg-white border-r border-gray-200 flex flex-col p-5">

    <h2 class="text-2xl font-bold mb-8 text-gray-800">
      Helpline System
    </h2>

    <nav class="flex flex-col gap-1 text-gray-700">

      <RouterLink
        to="/"
        class="flex items-center gap-3 px-3 py-3 rounded-lg hover:bg-amber-100 transition"
        :class="{ 'bg-amber-200 text-amber-900 font-semibold': $route.path === '/' }"
      >
        <i-mdi-view-dashboard-outline class="w-6 h-6" />
        <span>Dashboard</span>
      </RouterLink>

      <RouterLink
        to="/calls"
        class="flex items-center gap-3 px-3 py-3 rounded-lg hover:bg-amber-100 transition"
        :class="{ 'bg-amber-200 text-amber-900 font-semibold': $route.path === '/calls' }"
      >
        <i-mdi-phone-outline class="w-6 h-6" />
        <span>Calls</span>
      </RouterLink>

      <RouterLink
        to="/cases"
        class="flex items-center gap-3 px-3 py-3 rounded-lg hover:bg-amber-100 transition"
        :class="{ 'bg-amber-200 text-amber-900 font-semibold': $route.path === '/cases' }"
      >
        <i-mdi-folder-account-outline class="w-6 h-6" />
        <span>Cases</span>
      </RouterLink>

      <RouterLink
        to="/messages"
        class="flex items-center gap-3 px-3 py-3 rounded-lg hover:bg-amber-100 transition"
        :class="{ 'bg-amber-200 text-amber-900 font-semibold': $route.path === '/messages' }"
      >
        <i-mdi-message-text-outline class="w-6 h-6" />
        <span>Messages</span>
      </RouterLink>

      <RouterLink
        to="/case-creation"
        class="flex items-center gap-3 px-3 py-3 rounded-lg hover:bg-amber-100 transition"
        :class="{ 'bg-amber-200 text-amber-900 font-semibold': $route.path === '/case-create' }"
      >
        <i-mdi-folder-plus-outline class="w-6 h-6" />
        <span>Create Case</span>
      </RouterLink>

      <RouterLink
        to="/qa"
        class="flex items-center gap-3 px-3 py-3 rounded-lg hover:bg-amber-100 transition"
        :class="{ 'bg-amber-200 text-amber-900 font-semibold': $route.path === '/qa' }"
      >
        <i-mdi-check-decagram class="w-6 h-6" />
        <span>QA</span>
      </RouterLink>

      <RouterLink
        to="/qa-creation"
        class="flex items-center gap-3 px-3 py-3 rounded-lg hover:bg-amber-100 transition"
        :class="{ 'bg-amber-200 text-amber-900 font-semibold': $route.path === '/qa-create' }"
      >
        <i-mdi-plus-circle-outline class="w-6 h-6" />
        <span>Create QA</span>
      </RouterLink>

      <RouterLink
        to="/users"
        class="flex items-center gap-3 px-3 py-3 rounded-lg hover:bg-amber-100 transition"
        :class="{ 'bg-amber-200 text-amber-900 font-semibold': $route.path === '/users' }"
      >
        <i-mdi-account-multiple-outline class="w-6 h-6" />
        <span>Users</span>
      </RouterLink>

      <RouterLink
        to="/reports"
        class="flex items-center gap-3 px-3 py-3 rounded-lg hover:bg-amber-100 transition"
        :class="{ 'bg-amber-200 text-amber-900 font-semibold': $route.path === '/reports' }"
      >
        <i-mdi-chart-bar class="w-6 h-6" />
        <span>Reports</span>
      </RouterLink>

      <RouterLink
        to="/wallboard"
        class="flex items-center gap-3 px-3 py-3 rounded-lg hover:bg-amber-100 transition"
        :class="{ 'bg-amber-200 text-amber-900 font-semibold': $route.path === '/wallboard' }"
      >
        <i-mdi-monitor-dashboard class="w-6 h-6" />
        <span>Wallboard</span>
      </RouterLink>

    </nav>

  </aside>
</template>
