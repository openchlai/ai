<template>
  <aside class="h-screen bg-white shadow-md p-6 flex flex-col">
    <h2 class="text-xl font-bold mb-8 text-blue-600">My App</h2>

    <nav class="flex flex-col gap-4 text-gray-700">
      <RouterLink
        to="/"
        class="hover:text-blue-600 transition"
        active-class="text-blue-600 font-semibold"
      >
        🏠 Dashboard
      </RouterLink>
      
      <RouterLink
        to="/calls"
        class="hover:text-blue-600 transition"
        active-class="text-blue-600 font-semibold"
      >
        📊 Calls
      </RouterLink>
      
      <RouterLink
        to="/cases"
        class="hover:text-blue-600 transition"
        active-class="text-blue-600 font-semibold"
      >
        📊 Cases
      </RouterLink>
      <RouterLink
        to="/messages"
        class="hover:text-blue-600 transition"
        active-class="text-blue-600 font-semibold"
      >
        📊 Messages
      </RouterLink>
      <RouterLink
        to="/transcribe"
        class="hover:text-blue-600 transition"
        active-class="text-blue-600 font-semibold"
      >
        📊 Transcribe
      </RouterLink>
      <RouterLink
        to="/reports"
        class="hover:text-blue-600 transition"
        active-class="text-blue-600 font-semibold"
      >
        📊 Reports
      </RouterLink>
      <RouterLink
        to="/wallboard"
        class="hover:text-blue-600 transition"
        active-class="text-blue-600 font-semibold"
      >
        📊 Wallboard
      </RouterLink>
      
      <RouterLink
        to="/qa"
        class="hover:text-blue-600 transition"
        active-class="text-blue-600 font-semibold"
      >
        📊 Qa
      </RouterLink>
      
      </nav>
  </aside>
</template>
