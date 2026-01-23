<template>
  <nav 
    class="sticky top-0 z-40 w-full border-b transition-all duration-300 font-['Inter']"
    :class="isDarkMode 
      ? 'bg-black border-white/5 shadow-2xl shadow-black/80' 
      : 'bg-white/90 backdrop-blur-xl border-gray-200/50 shadow-lg shadow-gray-200/20'"
  >
    <div class="px-8 h-20 flex items-center justify-between">
      <!-- Left: Breadcrumbs / Page Title -->
      <div class="flex items-center gap-4">
        <div class="flex flex-col">
          <span 
            class="text-[10px] uppercase tracking-[0.2em] font-black"
            :class="isDarkMode ? 'text-amber-500/90' : 'text-amber-600/90'"
          >
            OpenCHS Platform
          </span>
          <h1 
            class="text-xl font-black tracking-tight"
            :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'"
          >
            {{ pageTitle }}
          </h1>
        </div>
      </div>

      <!-- Center: Status Area (Replaces Search Bar) -->
      <div class="hidden lg:flex items-center justify-center flex-1 mx-8 relative font-['Inter']">
        <Transition
          enter-active-class="transition duration-500 ease-out"
          enter-from-class="transform -translate-y-4 opacity-0"
          enter-to-class="transform translate-y-0 opacity-100"
          leave-active-class="transition duration-300 ease-in"
          leave-from-class="transform translate-y-0 opacity-100"
          leave-to-class="transform -translate-y-4 opacity-0"
        >
          <!-- Incoming Call Alert -->
          <div 
            v-if="isIncomingCall && !isCallActive"
            class="flex items-center gap-8 px-8 py-3 rounded-full border shadow-[0_10px_40px_-10px_rgba(0,0,0,0.1)] transition-all duration-300"
            :class="isDarkMode 
              ? 'bg-neutral-900 border-white/10 text-white' 
              : 'bg-white border-gray-100 text-gray-900'"
          >
            <div class="flex items-center gap-4">
              <div class="relative flex items-center justify-center w-10 h-10 rounded-full bg-amber-500/10 text-amber-600">
                <i-mdi-phone-ring class="w-5 h-5 animate-pulse" />
                <div class="absolute inset-0 rounded-full border-2 border-amber-500 animate-ping opacity-20"></div>
              </div>
              <div class="flex flex-col">
                <span class="text-[9px] font-black uppercase tracking-[0.2em] opacity-30">Incoming Call</span>
                <span class="text-sm font-black tracking-tight">{{ dialNumber }}</span>
              </div>
            </div>

            <div class="flex items-center gap-3 border-l pl-8 border-gray-100 dark:border-white/5">
              <button 
                @click.stop="answerCall"
                class="px-6 py-2 bg-emerald-600 text-white rounded-full text-[10px] font-black uppercase tracking-widest hover:bg-emerald-500 transition-all active:scale-95 shadow-lg shadow-emerald-500/20"
              >
                Pick Call
              </button>
              <button 
                @click.stop="endCall"
                class="p-2 text-gray-400 hover:text-red-500 transition-colors"
              >
                <i-mdi-close class="w-5 h-5" />
              </button>
            </div>
          </div>

          <div 
            v-else-if="isCallActive"
            class="flex items-center px-2 py-2 rounded-full border shadow-[0_15px_40px_-10px_rgba(0,0,0,0.08)] transition-all duration-500"
            :class="isDarkMode 
              ? 'bg-neutral-900 border-white/10 text-white' 
              : 'bg-white border-gray-100 text-gray-900 font-medium'"
          >
            <!-- Section 1: Active Call Info -->
            <div class="flex items-center gap-3 px-6 pr-8">
              <div class="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse shadow-[0_0_10px_rgba(16,185,129,0.5)]"></div>
              <div class="flex flex-col">
                <span class="text-[9px] font-black uppercase tracking-[0.2em] opacity-40">Active Call</span>
                <span class="text-sm font-black tracking-tight">{{ dialNumber }}</span>
              </div>
            </div>

            <!-- Section 2: Timer -->
            <div class="flex flex-col px-8 border-x border-gray-200/50 dark:border-white/5">
              <span class="text-[9px] font-black uppercase tracking-[0.2em] opacity-40">Duration</span>
              <span class="text-sm font-black font-mono tracking-widest">{{ formatDuration(callDuration) }}</span>
            </div>

            <!-- Section 3: Contextual Actions -->
            <div class="flex items-center gap-2 pl-6 pr-2">
              <button 
                @click="router.push('/case-creation')"
                class="flex items-center gap-2 px-4 py-2 rounded-full text-[9px] font-black uppercase tracking-widest transition-all hover:bg-black/5 dark:hover:bg-white/5 active:scale-95"
              >
                <i-mdi-plus-circle class="w-4 h-4 opacity-70" />
                Create Case
              </button>
              
              <!-- Contextual Dispose Dropdown Container -->
              <div class="relative">
                <button 
                  @click="isDisposing = !isDisposing"
                  class="flex items-center gap-2 px-4 py-2 rounded-full text-[9px] font-black uppercase tracking-widest transition-all active:scale-95"
                  :class="isDisposing ? 'bg-amber-500 text-white shadow-lg shadow-amber-500/20' : 'hover:bg-black/5 dark:hover:bg-white/5'"
                >
                  <i-mdi-file-document-edit class="w-4 h-4 opacity-70" />
                  Dispose
                </button>

                <!-- Actual Dropdown Menu -->
                <Transition
                  enter-active-class="transition duration-200 ease-out"
                  enter-from-class="transform -translate-y-2 opacity-0"
                  enter-to-class="transform translate-y-0 opacity-100"
                  leave-active-class="transition duration-150 ease-in"
                  leave-from-class="transform translate-y-0 opacity-100"
                  leave-to-class="transform -translate-y-2 opacity-0"
                >
                  <div 
                    v-if="isDisposing"
                    class="absolute top-12 left-1/2 -translate-x-1/2 w-48 rounded-2xl shadow-[0_20px_50px_rgba(0,0,0,0.15)] border overflow-hidden z-[100]"
                    :class="isDarkMode ? 'bg-neutral-900 border-white/10' : 'bg-white border-gray-100'"
                  >
                    <div class="py-1.5">
                      <div class="px-4 py-2 text-[9px] font-black uppercase tracking-[0.2em] opacity-30 border-b border-inherit">
                        Select Outcome
                      </div>
                      <button 
                        v-for="reason in ['Prank Call', 'No Caller', 'Dropped Call', 'General Inquiry', 'Escalated', 'Other']"
                        :key="reason"
                        @click="submitDisposition(reason)"
                        class="w-full text-left px-4 py-2.5 text-xs font-bold transition-all hover:bg-amber-500/10 hover:text-amber-500"
                        :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
                      >
                        {{ reason }}
                      </button>
                    </div>
                  </div>
                </Transition>
              </div>

              <button 
                @click="endCall"
                class="flex items-center gap-3 px-5 py-2.5 bg-red-600 text-white rounded-full text-[9px] font-black uppercase tracking-widest shadow-xl shadow-red-500/20 hover:bg-red-500 active:scale-95 transition-all ml-2"
              >
                <i-mdi-phone-hangup class="w-4 h-4" />
                End Call
              </button>
            </div>
          </div>
        </Transition>
      </div>

      <!-- Right: Actions & User Profile -->
      <div class="flex items-center gap-1 lg:gap-3 relative nav-actions font-sans">
        <!-- Softphone (Call Actions) -->
        <div class="flex items-center gap-1">
          <!-- Incoming Simulate Trigger -->
          <button 
            @click.stop="triggerIncomingCall"
            class="p-2 rounded-xl transition-all duration-300 relative group"
            :class="isIncomingCall 
              ? 'text-amber-500 bg-amber-500/10'
              : (isDarkMode ? 'text-gray-500 hover:text-white' : 'text-gray-400 hover:text-gray-900')"
          >
            <i-mdi-phone-incoming class="w-5 h-5" />
          </button>

          <!-- Dialer Toggle -->
          <div class="relative">
            <button 
              @click.stop="toggleDropdown('softphone')"
              class="p-2 rounded-xl transition-all duration-300 relative group"
              :class="dropdown === 'softphone' 
                ? (isDarkMode ? 'text-amber-500 bg-amber-500/10' : 'text-amber-600 bg-amber-600/10')
                : (isDarkMode ? 'text-gray-500 hover:text-white' : 'text-gray-400 hover:text-gray-900')"
            >
              <i-mdi-phone class="w-5 h-5" />
            </button>
          </div>
        </div>

          <!-- Softphone Dropdown -->
          <Transition
            enter-active-class="transition duration-150 ease-out"
            enter-from-class="transform translate-y-2 opacity-0"
            enter-to-class="transform translate-y-0 opacity-100"
          >
            <div 
              v-if="dropdown === 'softphone'"
              class="absolute top-12 right-0 w-80 rounded-[2rem] shadow-[0_30px_70px_rgba(0,0,0,0.6)] border overflow-hidden z-[70] font-sans"
              :class="isDarkMode ? 'bg-black border-white/10' : 'bg-white border-gray-100'"
            >
              <!-- Dialer Header -->
              <div class="p-6 pb-2" :class="isDarkMode ? 'text-white' : 'text-gray-900'">
                <div class="flex justify-between items-center mb-6">
                  <div class="flex flex-col">
                    <span class="text-[9px] font-black uppercase tracking-[0.2em] opacity-30">Voice Terminal</span>
                    <span class="text-xs font-bold flex items-center gap-1.5">
                      <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                      SIP Registered
                    </span>
                  </div>
                  <div class="flex items-center gap-2">
                    <span class="text-[9px] font-bold opacity-30 tracking-widest uppercase">Ext</span>
                    <span class="text-xs font-black px-2 py-0.5 rounded-lg border" :class="isDarkMode ? 'border-white/10 bg-white/5' : 'border-gray-100 bg-gray-50'">
                      {{ authStore.user?.extension || '---' }}
                    </span>
                  </div>
                </div>
                
                <div class="relative group mb-4 h-16 flex items-center justify-center">
                  <input 
                    v-model="dialNumber"
                    type="text" 
                    readonly
                    placeholder="Dial Pad"
                    class="w-full bg-transparent border-none text-4xl font-medium tracking-tight text-center focus:ring-0 placeholder-gray-500/20"
                    :class="isDarkMode ? 'text-white' : 'text-gray-900'"
                  />
                  <button 
                    v-if="dialNumber"
                    @click="dialNumber = ''"
                    class="absolute right-0 top-1/2 -translate-y-1/2 p-2 opacity-30 hover:opacity-100 transition-all hover:scale-110"
                  >
                    <i-mdi-backspace-outline class="w-5 h-5" />
                  </button>
                </div>
              </div>

              <!-- Keypad Grid (Only show if NOT in a call) -->
              <div v-if="!isCallActive" class="px-6 pb-6 grid grid-cols-3 gap-3 transition-all duration-500">
                <button 
                  v-for="(item, index) in [
                    { key: '1', sub: ' ' }, { key: '2', sub: 'ABC' }, { key: '3', sub: 'DEF' },
                    { key: '4', sub: 'GHI' }, { key: '5', sub: 'JKL' }, { key: '6', sub: 'MNO' },
                    { key: '7', sub: 'PQRS' }, { key: '8', sub: 'TUV' }, { key: '9', sub: 'WXYZ' },
                    { key: '*', sub: ' ' }, { key: '0', sub: '+' }, { key: '#', sub: ' ' }
                  ]" 
                  :key="index"
                  @click="dialNumber += item.key"
                  class="group flex flex-col items-center justify-center h-14 rounded-2xl transition-all duration-200 active:scale-90"
                  :class="isDarkMode 
                    ? 'hover:bg-white/5 border border-transparent hover:border-white/5' 
                    : 'hover:bg-gray-50 border border-transparent hover:border-gray-100'"
                >
                  <span class="text-2xl leading-none font-medium mb-0.5" :class="isDarkMode ? 'text-white' : 'text-gray-900'">{{ item.key }}</span>
                  <span class="text-[8px] font-black uppercase tracking-[0.1em] opacity-30 group-hover:opacity-60 transition-opacity">{{ item.sub }}</span>
                </button>
              </div>

              <!-- Active Call State -->
              <div v-if="isCallActive" class="px-6 pt-4 pb-10 flex flex-col items-center animate-in fade-in zoom-in duration-300">
                <div 
                  class="w-24 h-24 rounded-full flex items-center justify-center mb-6 relative"
                  :class="isDarkMode ? 'bg-white/5' : 'bg-gray-50'"
                >
                  <div class="absolute inset-0 rounded-full border-2 border-emerald-500 animate-ping opacity-20"></div>
                  <i-mdi-account-voice class="w-12 h-12" :class="isDarkMode ? 'text-white' : 'text-gray-900'" />
                </div>
                
                <h3 class="text-xl font-bold mb-1" :class="isDarkMode ? 'text-white' : 'text-gray-900'">
                  {{ isConnecting ? 'Calling...' : 'In Call' }}
                </h3>
                <p class="text-sm font-bold opacity-40 mb-8">{{ formatDuration(callDuration) }}</p>

                <div class="flex gap-4">
                  <button class="w-14 h-14 rounded-2xl flex items-center justify-center transition-colors" :class="isDarkMode ? 'bg-white/5 text-white hover:bg-white/10' : 'bg-gray-100 text-gray-900 hover:bg-gray-200'">
                    <i-mdi-microphone-off class="w-6 h-6" />
                  </button>
                  <button class="w-14 h-14 rounded-2xl flex items-center justify-center transition-colors" :class="isDarkMode ? 'bg-white/5 text-white hover:bg-white/10' : 'bg-gray-100 text-gray-900 hover:bg-gray-200'">
                    <i-mdi-pause class="w-6 h-6" />
                  </button>
                </div>
              </div>

              <!-- Call Actions -->
              <div class="px-6 pb-8 flex flex-col items-center">
                <button 
                  v-if="!isCallActive"
                  @click="startCall"
                  class="w-16 h-16 bg-emerald-600 hover:bg-emerald-500 text-white rounded-full flex items-center justify-center shadow-2xl shadow-emerald-500/40 active:scale-90 transition-all group/call"
                >
                  <i-mdi-phone class="w-8 h-8 transition-transform group-hover/call:rotate-12" />
                </button>
                
                <button 
                  v-else
                  @click="endCall"
                  class="w-16 h-16 bg-red-600 hover:bg-red-500 text-white rounded-full flex items-center justify-center shadow-2xl shadow-red-500/40 active:scale-90 transition-all group/hangup"
                >
                  <i-mdi-phone-hangup class="w-8 h-8 transition-transform group-hover/hangup:-rotate-12" />
                </button>
                
                <span class="mt-3 text-[10px] font-black uppercase tracking-[0.2em] opacity-40">
                  {{ isCallActive ? 'Terminate' : 'Initiate' }}
                </span>
              </div>
            </div>
          </Transition>

        <!-- Clock / History Icon (Now Activities) -->
        <button 
          @click.stop="toggleDropdown('activities')"
          class="p-2 rounded-xl transition-all duration-300 group relative"
          :class="dropdown === 'activities' 
            ? (isDarkMode ? 'text-white' : 'text-gray-900')
            : (isDarkMode ? 'text-gray-500 hover:text-white' : 'text-gray-400 hover:text-gray-900')"
        >
          <i-mdi-clock-outline class="w-5 h-5 stroke-1" />
        </button>

        <!-- Bell / Notifications Icon -->
        <div class="relative">
          <button 
            @click.stop="toggleDropdown('notifications')"
            class="p-2 rounded-xl transition-all duration-300 relative group"
            :class="dropdown === 'notifications' 
              ? (isDarkMode ? 'text-white' : 'text-gray-900')
              : (isDarkMode ? 'text-gray-500 hover:text-white' : 'text-gray-400 hover:text-gray-900')"
          >
            <i-mdi-bell class="w-5 h-5" />
            <span
              v-if="notificationsStore.unreadCount > 0"
              class="absolute top-1 right-1 min-w-[17px] h-[17px] px-1 bg-red-600 text-[9px] font-black text-white flex items-center justify-center rounded-full border-2 border-black shadow-xl"
              style="transform: translate(25%, -25%);"
            >
              {{ notificationsStore.unreadCount }}
            </span>
          </button>
        </div>

        <!-- User Profile Dropdown -->
        <div class="relative ml-0.5">
          <button 
            @click.stop="toggleDropdown('profile')"
            class="flex items-center justify-center w-9 h-9 rounded-full transition-all duration-300 border shadow-inner"
            :class="isDarkMode 
              ? 'border-white/10 bg-black hover:border-white/20' 
              : 'border-gray-200 bg-white hover:border-gray-300'"
          >
            <div 
              class="w-7 h-7 rounded-full flex items-center justify-center overflow-hidden transition-colors"
              :class="isDarkMode ? 'bg-neutral-800 text-gray-300 group-hover:bg-neutral-700' : 'bg-gray-100 text-gray-600'"
            >
              <i-mdi-account class="w-5 h-5" />
            </div>
          </button>

          <!-- Profile Dropdown Content -->
          <Transition
            enter-active-class="transition duration-150 ease-out"
            enter-from-class="transform scale-95 opacity-0"
            enter-to-class="transform scale-100 opacity-100"
            leave-active-class="transition duration-100 ease-in"
            leave-from-class="transform scale-100 opacity-100"
            leave-to-class="transform scale-95 opacity-0"
          >
            <div 
              v-if="dropdown === 'profile'"
              class="absolute right-0 mt-3 w-64 rounded-2xl shadow-[0_20px_50px_rgba(0,0,0,0.5)] border overflow-hidden z-[60] py-1.5 font-sans"
              :class="isDarkMode ? 'bg-black border-white/10' : 'bg-white border-gray-100 text-gray-900'"
            >
              <div class="px-5 py-4 border-b" :class="isDarkMode ? 'border-white/5' : 'border-gray-50'">
                <p class="text-sm font-black tracking-tight" :class="isDarkMode ? 'text-white' : 'text-gray-900'">
                  {{ authStore.userDisplayName }}
                </p>
                <div class="mt-2 flex items-center gap-1.5 text-[10px] font-bold text-gray-500 uppercase tracking-widest opacity-60">
                  <i-mdi-badge-account class="w-3 h-3" />
                  {{ authStore.roleDisplayName }}
                </div>
              </div>

              <div class="p-2 space-y-1">
                <button 
                  class="w-full text-left px-4 py-2.5 text-sm font-bold rounded-xl transition-all"
                  :class="isDarkMode ? 'text-gray-300 hover:bg-white/5 hover:text-amber-500' : 'text-gray-600 hover:bg-gray-50'"
                >
                  My Account
                </button>
                
                <div class="px-4 py-2 text-[11px] font-bold text-gray-500 opacity-80 flex items-center gap-2">
                  <i-mdi-phone-outline class="w-4 h-4" />
                  Extension {{ authStore.user?.extension || '---' }}
                </div>

                <!-- Join Queue Workflow Container -->
                <div class="py-2 px-1">
                  <button 
                    @click.stop="handleQueueAction"
                    class="w-full h-11 flex items-center justify-center gap-2 rounded-xl text-sm font-bold transition-all duration-300 transform active:scale-95 shadow-lg group/btn"
                    :class="getQueueButtonClass"
                    :disabled="isQueueActionLoading"
                  >
                    <template v-if="queueStatus === 'offline'">
                      <i-mdi-account-group class="w-5 h-5 transition-transform group-hover/btn:scale-110" />
                      Join Queue
                    </template>
                    <template v-else-if="queueStatus === 'registering'">
                      <i-mdi-play-circle class="w-5 h-5 text-amber-500 animate-pulse" />
                      Start (Register)
                    </template>
                    <template v-else-if="queueStatus === 'joining'">
                      <i-mdi-loading class="w-5 h-5 animate-spin" />
                      Joining Queue...
                    </template>
                    <template v-else-if="queueStatus === 'online'">
                      <i-mdi-account-minus class="w-5 h-5 transition-transform group-hover/btn:scale-110" />
                      Leave Queue
                    </template>
                  </button>
                </div>

                <button 
                  class="w-full text-left px-4 py-2.5 text-sm font-bold rounded-xl transition-all"
                  :class="isDarkMode ? 'text-gray-300 hover:bg-white/5 hover:text-amber-500' : 'text-gray-600 hover:bg-gray-50'"
                >
                  My Profile
                </button>
              </div>

              <div class="border-t mt-1 pt-1" :class="isDarkMode ? 'border-white/5' : 'border-gray-50'">
                <button 
                  @click="handleLogout"
                  class="w-full text-left px-5 py-3 text-sm font-black text-red-500 transition-colors hover:bg-red-500/5"
                >
                  Logout
                </button>
              </div>
            </div>
          </Transition>
        </div>

        <!-- Activities Panel (Image 0 Mock) -->
        <Transition
          enter-active-class="transition duration-150 ease-out"
          enter-from-class="transform translate-y-2 opacity-0"
          enter-to-class="transform translate-y-0 opacity-100"
        >
          <div 
            v-if="dropdown === 'activities'"
            class="absolute top-16 right-44 w-[400px] rounded-2xl shadow-2xl border overflow-hidden z-[60]"
            :class="isDarkMode ? 'bg-black border-white/10' : 'bg-white border-gray-100'"
          >
            <div class="px-5 py-4 border-b flex items-center justify-between" :class="isDarkMode ? 'border-white/5' : 'border-gray-50 text-gray-900'">
              <h3 class="font-black text-sm uppercase tracking-tight">Activities</h3>
            </div>
            <div class="max-h-[500px] overflow-y-auto">
              <div v-for="i in 10" :key="i" class="px-5 py-4 border-b last:border-0 hover:bg-white/5 transition-colors cursor-pointer" :class="isDarkMode ? 'border-white/5' : 'border-gray-100'">
                <div class="flex justify-between items-start mb-1">
                  <span class="text-xs font-bold" :class="isDarkMode ? 'text-gray-200' : 'text-gray-900'">Case Update <span class="text-gray-500 font-medium ml-1">test</span></span>
                  <span class="text-[10px] font-bold text-gray-500">0:00</span>
                </div>
                <div class="flex justify-between mt-2">
                  <span class="text-[10px] font-semibold text-gray-500">2 days ago</span>
                  <span class="text-[10px] font-semibold text-gray-500 uppercase">3:27 PM</span>
                </div>
              </div>
            </div>
            <div class="p-4 border-t" :class="isDarkMode ? 'border-white/5' : 'border-gray-50'">
              <div class="flex items-center justify-between px-2 text-[11px] font-bold text-gray-500">
                <span>1 - 10 of 2137</span>
                <div class="flex gap-4">
                  <button class="hover:text-amber-500 transition-colors"><i-mdi-chevron-left class="w-5 h-5" /></button>
                  <button class="hover:text-amber-500 transition-colors"><i-mdi-chevron-right class="w-5 h-5" /></button>
                </div>
              </div>
            </div>
          </div>
        </Transition>

        <!-- Notifications Panel (Image 1 Mock) -->
        <Transition
          enter-active-class="transition duration-150 ease-out"
          enter-from-class="transform translate-y-2 opacity-0"
          enter-to-class="transform translate-y-0 opacity-100"
        >
          <div 
            v-if="dropdown === 'notifications'"
            class="absolute top-16 right-24 w-[480px] rounded-2xl shadow-2xl border overflow-hidden z-[60]"
            :class="isDarkMode ? 'bg-black border-white/10' : 'bg-white border-gray-100'"
          >
            <div class="px-5 py-4 border-b flex items-center justify-between" :class="isDarkMode ? 'border-white/5' : 'border-gray-50 text-gray-900'">
              <h3 class="font-black text-sm uppercase tracking-tight">Notifications</h3>
            </div>
            <div class="max-h-[500px] overflow-y-auto">
              <div
                v-if="notificationsStore.loading"
                class="px-5 py-8 text-center"
              >
                <div class="animate-spin w-8 h-8 mx-auto border-4 border-amber-500 border-t-transparent rounded-full"></div>
                <p class="mt-2 text-sm text-gray-500">Loading notifications...</p>
              </div>

              <div
                v-else-if="notificationsStore.notifications.length === 0"
                class="px-5 py-8 text-center"
              >
                <i-mdi-bell-off class="w-12 h-12 mx-auto text-gray-400 mb-2" />
                <p class="text-sm text-gray-500">No notifications</p>
              </div>

              <div
                v-else
                v-for="(notification, index) in notificationsStore.notificationsAsObjects"
                :key="notification.id"
                class="px-5 py-4 border-b last:border-0 hover:bg-white/5 transition-colors cursor-pointer"
                :class="[
                  isDarkMode ? 'border-white/5' : 'border-gray-100',
                  !notification.read_on || notification.read_on === '0' ? (isDarkMode ? 'bg-white/5' : 'bg-amber-50/30') : ''
                ]"
                @click="handleNotificationClick(notification)"
              >
                <div class="flex justify-between items-start mb-2">
                  <div class="flex items-center gap-2">
                    <span class="text-xs font-bold" :class="isDarkMode ? 'text-white' : 'text-gray-900'">
                      {{ notification.action_verb || 'Case Update' }}
                    </span>
                    <span class="text-[10px] font-medium text-gray-500">
                      from {{ notification.created_by || 'Unknown' }}
                    </span>
                  </div>
                  <div class="text-right">
                    <span class="text-[10px] font-bold text-gray-500 block uppercase">
                      {{ formatTimeAgo(notification.created_on) }}
                    </span>
                    <span class="text-[10px] font-bold text-gray-500 uppercase">
                      {{ formatTime(notification.created_on) }}
                    </span>
                  </div>
                </div>
                <div class="flex items-center gap-1.5 mb-3 text-[10px] font-bold text-gray-500 opacity-80 overflow-x-hidden">
                  <span v-if="notification.case_id">#{{ notification.case_id }}</span>
                  <template v-if="notification.case_details">
                    <i-mdi-chevron-right class="w-3 h-3 opacity-50" />
                    <span class="truncate">{{ notification.case_details }}</span>
                  </template>
                </div>
                <span
                  v-if="!notification.read_on || notification.read_on === '0'"
                  class="px-2 py-0.5 bg-red-600 text-[9px] font-black text-white rounded uppercase tracking-widest inline-block"
                >
                  unread
                </span>
              </div>
            </div>
            <div class="p-4 border-t" :class="isDarkMode ? 'border-white/5' : 'border-gray-50'">
              <div class="flex items-center justify-between px-2 text-[11px] font-bold text-gray-500">
                <span>{{ notificationsStore.paginationInfo.rangeStart }} - {{ notificationsStore.paginationInfo.rangeEnd }} of {{ notificationsStore.paginationInfo.total }}</span>
                <div class="flex gap-4">
                  <button
                    @click="handleNotificationPrevPage"
                    :disabled="!notificationsStore.hasPrevPage"
                    :class="notificationsStore.hasPrevPage ? 'hover:text-amber-500 transition-colors' : 'opacity-30 cursor-not-allowed'"
                  >
                    <i-mdi-chevron-left class="w-5 h-5" />
                  </button>
                  <button
                    @click="handleNotificationNextPage"
                    :disabled="!notificationsStore.hasNextPage"
                    :class="notificationsStore.hasNextPage ? 'hover:text-amber-500 transition-colors' : 'opacity-30 cursor-not-allowed'"
                  >
                    <i-mdi-chevron-right class="w-5 h-5" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </Transition>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, markRaw, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useSearchStore } from '@/stores/search'
import { useNotificationsStore } from '@/stores/notifications'

const props = defineProps({
  isDarkMode: {
    type: Boolean,
    default: false
  }
})

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const searchStore = useSearchStore()
const notificationsStore = useNotificationsStore()

const dropdown = ref(null)
const dialNumber = ref('')
const isCallActive = ref(false)
const isConnecting = ref(false)
const isIncomingCall = ref(false)
const isDisposing = ref(false)
const callDuration = ref(0)
let callTimer = null

const triggerIncomingCall = () => {
  console.log('[SIP] Simulating incoming call...')
  if (isCallActive.value || isIncomingCall.value) return
  isIncomingCall.value = true
  // Simulate a specific incoming number
  dialNumber.value = '+254 712 345 678'
}

const answerCall = () => {
  console.log('[SIP] Answering incoming call...')
  isIncomingCall.value = false
  isCallActive.value = true
  isConnecting.value = false
  // Start timer immediately for answered calls
  callTimer = setInterval(() => {
    callDuration.value++
  }, 1000)
}

const startCall = () => {
  if (!dialNumber.value) return
  isCallActive.value = true
  isConnecting.value = true
  
  // Simulate connection delay
  setTimeout(() => {
    isConnecting.value = false
    callTimer = setInterval(() => {
      callDuration.value++
    }, 1000)
  }, 1500)
}

const endCall = () => {
  clearInterval(callTimer)
  isCallActive.value = false
  isConnecting.value = false
  isIncomingCall.value = false
  callDuration.value = 0
  dialNumber.value = ''
}

const submitDisposition = (reason) => {
  console.log('Call Disposed:', reason)
  isDisposing.value = false
  endCall()
  // Show a success toast or notification
}

const formatDuration = (seconds) => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

const queueStatus = ref('offline') // 'offline', 'registering', 'joining', 'online'
const isQueueActionLoading = ref(false)

// Search logic linked to store
const searchQuery = ref(searchStore.query)
const isSearchFocused = ref(false)

// Sync local ref with store
watch(searchQuery, (newQuery) => {
  searchStore.setQuery(newQuery)
})

// Sync store with local ref (in case external clear)
watch(() => searchStore.query, (newQuery) => {
  searchQuery.value = newQuery
})

const allPages = [
  { title: 'Dashboard', path: '/', icon: 'i-mdi-view-dashboard-outline', group: 'Navigation', permission: 'dashboard' },
  { title: 'Case Management', path: '/cases', icon: 'i-mdi-folder-account-outline', group: 'Navigation', permission: 'cases' },
  { title: 'Create Case', path: '/case-creation', icon: 'i-mdi-plus-circle-outline', group: 'Quick Actions', permission: 'cases' },
  { title: 'Call Recordings', path: '/calls', icon: 'i-mdi-phone-outline', group: 'Tools', permission: 'calls' },
  { title: 'Other Channels', path: '/messages', icon: 'i-mdi-message-text-outline', group: 'Tools', permission: 'messages' },
  { title: 'Quality Assurance', path: '/qa', icon: 'i-mdi-shield-check-outline', group: 'Tools', permission: 'qa' },
  { title: 'Real-time Wallboard', path: '/wallboard', icon: 'i-mdi-monitor-dashboard', group: 'Tools', permission: 'wallboard' },
  { title: 'User Management', path: '/users', icon: 'i-mdi-account-group-outline', group: 'Admin', permission: 'users' },
  { title: 'Activity Logs', path: '/activities', icon: 'i-mdi-pulse', group: 'Admin', permission: 'activities' },
  { title: 'Knowledge Base', path: '/faqs', icon: 'i-mdi-book-open-page-variant-outline', group: 'Resources', permission: 'faqs' },
]

const filteredResults = computed(() => {
  if (!searchQuery.value) return []
  const query = searchQuery.value.toLowerCase()
  return allPages.filter(page => {
    const matchesQuery = page.title.toLowerCase().includes(query) || page.group.toLowerCase().includes(query)
    const hasPermission = authStore.hasPermission(page.permission)
    return matchesQuery && hasPermission
  }).slice(0, 8)
})

const groupedResults = computed(() => {
  const groups = {}
  filteredResults.value.forEach(item => {
    if (!groups[item.group]) {
      groups[item.group] = []
    }
    groups[item.group].push(item)
  })
  
  return Object.keys(groups).map(name => ({
    name,
    items: groups[name]
  }))
})

const clearSearch = () => {
  searchQuery.value = ''
  isSearchFocused.value = false
}

const handleSearchSelect = (item) => {
  router.push(item.path)
  clearSearch()
}

const handleQueueAction = async () => {
  if (isQueueActionLoading.value) return

  if (queueStatus.value === 'offline') {
    queueStatus.value = 'registering'
    return
  }

  if (queueStatus.value === 'registering') {
    isQueueActionLoading.value = true
    queueStatus.value = 'joining'
    await new Promise(resolve => setTimeout(resolve, 1500))
    queueStatus.value = 'online'
    isQueueActionLoading.value = false
    return
  }

  if (queueStatus.value === 'online') {
    isQueueActionLoading.value = true
    await new Promise(resolve => setTimeout(resolve, 1000))
    queueStatus.value = 'offline'
    isQueueActionLoading.value = false
    return
  }
}

const getQueueButtonClass = computed(() => {
  if (queueStatus.value === 'offline') return 'bg-emerald-600 hover:bg-emerald-700 text-white shadow-lg shadow-emerald-900/20'
  if (queueStatus.value === 'registering') return 'bg-gray-400 dark:bg-gray-700 hover:bg-gray-500 dark:hover:bg-gray-600 text-white shadow-lg'
  if (queueStatus.value === 'joining') return 'bg-emerald-500/50 text-white cursor-not-allowed'
  if (queueStatus.value === 'online') return 'bg-red-600 hover:bg-red-700 text-white shadow-lg shadow-red-900/20'
  return ''
})

const toggleDropdown = (name) => {
  dropdown.value = dropdown.value === name ? null : name
}

const handleClickOutside = (event) => {
  if (dropdown.value && !event.target.closest('.nav-actions')) {
    dropdown.value = null
  }
  if (isSearchFocused.value && !event.target.closest('.search-container')) {
    isSearchFocused.value = false
  }
}

onMounted(async () => {
  window.addEventListener('click', handleClickOutside)
  // Fetch notifications only if user is authenticated
  if (authStore.isAuthenticated) {
    try {
      await notificationsStore.fetchNotifications()
    } catch (error) {
      console.error('Failed to load notifications:', error)
    }
  }
})

onUnmounted(() => {
  window.removeEventListener('click', handleClickOutside)
})

const handleLogout = async () => {
  await authStore.logout()
  router.push('/login')
}

const pageTitle = computed(() => {
  const path = route.path
  if (path === '/') return 'Dashboard'

  const customTitles = {
    '/calls': 'Call Recordings',
    '/cases': 'Case Management',
    '/messages': 'Other Channels',
    '/qa': 'Quality Assurance',
    '/wallboard': 'Real-time Wallboard',
    '/users': 'User Management',
    '/activities': 'Activity Logs',
    '/faqs': 'Knowledge Base',
    '/case-creation': 'Create New Case'
  }

  if (customTitles[path]) return customTitles[path]

  const segment = path.split('/')[1] || ''
  if (!segment) return 'Home'

  return segment
    .split('-')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
})

// Notification helper functions
const formatTimeAgo = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(Number(timestamp) * 1000)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 1) return 'just now'
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  if (diffDays < 7) return `${diffDays}d ago`
  return date.toLocaleDateString()
}

const formatTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(Number(timestamp) * 1000)
  return date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true })
}

const handleNotificationClick = async (notification) => {
  console.log('Notification clicked:', notification)

  // Mark as read if unread
  if (!notification.read_on || notification.read_on === '0') {
    try {
      await notificationsStore.markAsRead(notification.id)
    } catch (error) {
      console.error('Failed to mark notification as read:', error)
    }
  }

  // Navigate to the case if case_id exists
  if (notification.case_id) {
    router.push(`/cases/${notification.case_id}`)
    dropdown.value = null // Close dropdown
  }
}

const handleNotificationPrevPage = async () => {
  try {
    await notificationsStore.prevPage()
  } catch (error) {
    console.error('Failed to load previous page:', error)
  }
}

const handleNotificationNextPage = async () => {
  try {
    await notificationsStore.nextPage()
  } catch (error) {
    console.error('Failed to load next page:', error)
  }
}
</script>

<style scoped>
.scrollbar-hide::-webkit-scrollbar {
  display: none;
}

/* Custom scrollbar for dark mode panels */
::-webkit-scrollbar {
  width: 4px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
}
::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.2);
}
</style>
