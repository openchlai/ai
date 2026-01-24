<template>
  <div class="space-y-6">
<<<<<<< HEAD
     <div class="w-full flex justify-center pt-10">
        <Dialpad />
     </div>
=======
    <div class="max-w-md mx-auto">
      <!-- Loading state -->
      <div
        v-if="loadingExtension"
        class="p-6 border rounded-lg shadow-xl"
        :class="isDarkMode
          ? 'border-transparent bg-black'
          : 'border-transparent bg-white'"
      >
        <div class="flex items-center justify-center py-8">
          <div
            class="animate-spin rounded-full h-8 w-8 border-b-2"
            :class="isDarkMode ? 'border-blue-500' : 'border-amber-600'"
          ></div>
          <span
            class="ml-3"
            :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
          >
            Loading extension...
          </span>
        </div>
      </div>

      <!-- Error state -->
      <div
        v-else-if="extensionError"
        class="p-6 border rounded-lg shadow-xl"
        :class="isDarkMode
          ? 'border-red-700 bg-red-900/20'
          : 'border-red-300 bg-red-50'"
      >
        <p
          class="text-center"
          :class="isDarkMode ? 'text-red-400' : 'text-red-700'"
        >
          {{ extensionError }}
        </p>
      </div>

      <!-- SIP Agent -->
      <div
        v-else
        class="p-6 border rounded-lg shadow-xl"
        :class="isDarkMode
          ? 'border-transparent bg-black'
          : 'border-transparent bg-white'"
      >
        <h3
          class="mb-4 text-xl font-semibold text-center"
          :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'"
        >
          SIP Agent - Extension {{ agent.extension }}
        </h3>

        <!-- Status indicators -->
        <div class="space-y-2 mb-6 text-sm">
          <div
            class="flex justify-between items-center p-3 rounded border"
            :class="isDarkMode
              ? 'bg-black/40 border-transparent'
              : 'bg-gray-50 border-transparent'"
          >
            <span
              class="font-medium"
              :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
            >
              Registered:
            </span>
            <span
              class="font-semibold"
              :class="agent.registered
                ? (isDarkMode ? 'text-green-400' : 'text-green-700')
                : (isDarkMode ? 'text-red-400' : 'text-red-700')"
            >
              {{ agent.registered ? 'Yes' : 'No' }}
            </span>
          </div>

          <div
            class="flex justify-between items-center p-3 rounded border"
            :class="isDarkMode
              ? 'bg-black/40 border-transparent'
              : 'bg-gray-50 border-transparent'"
          >
            <span
              class="font-medium"
              :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
            >
              Connection:
            </span>
            <span
              class="font-semibold"
              :class="agent.connected
                ? (isDarkMode ? 'text-green-400' : 'text-green-700')
                : (isDarkMode ? 'text-red-400' : 'text-red-700')"
            >
              {{ agent.connected ? 'Connected' : 'Disconnected' }}
            </span>
          </div>

          <!-- Queue Status -->
          <div
            class="flex justify-between items-center p-3 rounded border"
            :class="isDarkMode
              ? 'bg-black/40 border-transparent'
              : 'bg-gray-50 border-transparent'"
          >
            <span
              class="font-medium"
              :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
            >
              Queue:
            </span>
            <span
              class="font-semibold"
              :class="queue.inQueue
                ? (isDarkMode ? 'text-green-400' : 'text-green-700')
                : (isDarkMode ? 'text-yellow-400' : 'text-yellow-700')"
            >
              {{ queue.inQueue ? 'In Queue' : 'Not in Queue' }}
            </span>
          </div>

          <!-- Auto-Answer Status -->
          <div
            class="flex justify-between items-center p-3 rounded border"
            :class="isDarkMode
              ? 'bg-black/40 border-transparent'
              : 'bg-gray-50 border-transparent'"
          >
            <span
              class="font-medium"
              :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
            >
              Auto-Answer:
            </span>
            <span
              class="font-semibold"
              :class="autoAnswer
                ? (isDarkMode ? 'text-purple-400' : 'text-purple-700')
                : (isDarkMode ? 'text-gray-400' : 'text-gray-600')"
            >
              {{ autoAnswer ? 'Enabled' : 'Disabled' }}
            </span>
          </div>

          <div
            v-if="agent.callStatus"
            class="p-3 rounded border"
            :class="isDarkMode
              ? 'bg-amber-600/20 border-amber-600/50'
              : 'bg-amber-50 border-amber-300'"
          >
            <p
              class="text-sm font-medium"
              :class="isDarkMode ? 'text-amber-500' : 'text-amber-700'"
            >
              {{ agent.callStatus }}
              <span v-if="agent.isOnHold" class="ml-2 text-yellow-500">(ON HOLD)</span>
            </p>
          </div>
        </div>

        <!-- Dialer Section -->
        <div v-if="agent.registered && !agent.inCall" class="mb-6">
          <label
            class="block text-sm font-medium mb-2"
            :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
          >
            Dial Number
          </label>
          <div class="flex gap-2">
            <input
              v-model="dialNumber"
              type="text"
              placeholder="Enter number to dial"
              class="flex-1 px-4 py-2 rounded-lg border focus:outline-none focus:ring-2"
              :class="isDarkMode
                ? 'bg-black border-gray-700 text-white focus:ring-amber-600'
                : 'bg-white border-gray-300 text-gray-900 focus:ring-amber-500'"
              @keyup.enter="makeCall"
            />
            <button
              @click="makeCall"
              :disabled="!dialNumber.trim() || agent.inCall"
              class="px-4 py-2 rounded-lg font-medium transition flex items-center gap-2 disabled:cursor-not-allowed"
              :class="!dialNumber.trim() || agent.inCall
                ? (isDarkMode ? 'bg-gray-700 text-gray-500' : 'bg-gray-300 text-gray-500')
                : (isDarkMode ? 'bg-green-600 hover:bg-green-700 text-white' : 'bg-green-600 hover:bg-green-700 text-white')"
            >
              <i-mdi-phone class="w-5 h-5" />
              Call
            </button>
          </div>
        </div>

        <!-- Call Controls (shown during call) -->
        <div v-if="agent.inCall" class="mb-6 space-y-4">
          <!-- Hold/Transfer buttons -->
          <div class="flex gap-2">
            <button
              @click="toggleHold"
              class="flex-1 px-4 py-2 rounded-lg font-medium transition flex items-center justify-center gap-2"
              :class="agent.isOnHold
                ? (isDarkMode ? 'bg-yellow-600 hover:bg-yellow-700 text-white' : 'bg-yellow-500 hover:bg-yellow-600 text-white')
                : (isDarkMode ? 'bg-gray-600 hover:bg-gray-700 text-white' : 'bg-gray-500 hover:bg-gray-600 text-white')"
            >
              <i-mdi-pause v-if="!agent.isOnHold" class="w-5 h-5" />
              <i-mdi-play v-else class="w-5 h-5" />
              {{ agent.isOnHold ? 'Resume' : 'Hold' }}
            </button>
            <button
              @click="showTransferDialog = true"
              class="flex-1 px-4 py-2 rounded-lg font-medium transition flex items-center justify-center gap-2"
              :class="isDarkMode
                ? 'bg-blue-600 hover:bg-blue-700 text-white'
                : 'bg-blue-500 hover:bg-blue-600 text-white'"
            >
              <i-mdi-phone-forward class="w-5 h-5" />
              Transfer
            </button>
          </div>

          <!-- DTMF Keypad -->
          <div>
            <button
              @click="showDtmfPad = !showDtmfPad"
              class="w-full px-4 py-2 rounded-lg font-medium transition flex items-center justify-center gap-2"
              :class="isDarkMode
                ? 'bg-gray-700 hover:bg-gray-600 text-white'
                : 'bg-gray-200 hover:bg-gray-300 text-gray-800'"
            >
              <i-mdi-dialpad class="w-5 h-5" />
              {{ showDtmfPad ? 'Hide Keypad' : 'Show Keypad' }}
            </button>

            <div v-if="showDtmfPad" class="mt-3 grid grid-cols-3 gap-2">
              <button
                v-for="key in dtmfKeys"
                :key="key"
                @click="sendDtmf(key)"
                class="py-3 rounded-lg font-bold text-lg transition"
                :class="isDarkMode
                  ? 'bg-gray-700 hover:bg-gray-600 text-white'
                  : 'bg-gray-200 hover:bg-gray-300 text-gray-800'"
              >
                {{ key }}
              </button>
            </div>
          </div>
        </div>

        <!-- Main Control Buttons -->
        <div class="flex flex-col gap-3">
          <button
            @click="startAgent"
            :disabled="agent.registered || agent.starting"
            class="px-6 py-3 text-white rounded-lg transition font-medium flex items-center justify-center gap-2 disabled:cursor-not-allowed"
            :class="agent.registered || agent.starting
              ? (isDarkMode ? 'bg-gray-700' : 'bg-gray-300')
              : (isDarkMode ? 'bg-amber-600 hover:bg-amber-700' : 'bg-amber-700 hover:bg-amber-800')"
          >
            <i-mdi-play class="w-5 h-5" />
            {{ agent.starting ? 'Starting...' : 'Start (Register)' }}
          </button>

          <!-- Queue Control -->
          <button
            v-if="agent.registered"
            @click="toggleQueue"
            :disabled="queue.loading"
            class="px-6 py-3 text-white rounded-lg transition font-medium flex items-center justify-center gap-2 disabled:cursor-not-allowed"
            :class="queue.loading
              ? (isDarkMode ? 'bg-gray-700' : 'bg-gray-300')
              : queue.inQueue
                ? (isDarkMode ? 'bg-orange-600 hover:bg-orange-700' : 'bg-orange-500 hover:bg-orange-600')
                : (isDarkMode ? 'bg-green-600 hover:bg-green-700' : 'bg-green-600 hover:bg-green-700')"
          >
            <i-mdi-account-group v-if="!queue.inQueue" class="w-5 h-5" />
            <i-mdi-account-off v-else class="w-5 h-5" />
            {{ queue.loading ? 'Loading...' : (queue.inQueue ? 'Leave Queue' : 'Join Queue') }}
          </button>

          <!-- Auto-Answer Toggle -->
          <button
            v-if="agent.registered"
            @click="autoAnswer = !autoAnswer"
            class="px-6 py-3 text-white rounded-lg transition font-medium flex items-center justify-center gap-2"
            :class="autoAnswer
              ? (isDarkMode ? 'bg-purple-600 hover:bg-purple-700' : 'bg-purple-600 hover:bg-purple-700')
              : (isDarkMode ? 'bg-gray-600 hover:bg-gray-700' : 'bg-gray-500 hover:bg-gray-600')"
          >
            <i-mdi-phone-check v-if="autoAnswer" class="w-5 h-5" />
            <i-mdi-phone-cancel v-else class="w-5 h-5" />
            Auto-Answer: {{ autoAnswer ? 'On' : 'Off' }}
          </button>

          <button
            @click="hangup"
            :disabled="!agent.inCall"
            class="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:bg-gray-700 disabled:cursor-not-allowed transition font-medium flex items-center justify-center gap-2"
            :class="!agent.inCall && !isDarkMode ? 'disabled:bg-gray-300' : ''"
          >
            <i-mdi-phone-hangup class="w-5 h-5" />
            Hang Up
          </button>

          <button
            @click="stopAgent"
            :disabled="!agent.registered || agent.stopping"
            class="px-6 py-3 text-white rounded-lg transition font-medium flex items-center justify-center gap-2 disabled:cursor-not-allowed"
            :class="!agent.registered || agent.stopping
              ? (isDarkMode ? 'bg-gray-700' : 'bg-gray-300')
              : (isDarkMode ? 'bg-gray-600 hover:bg-gray-700' : 'bg-gray-500 hover:bg-gray-600')"
          >
            <i-mdi-stop class="w-5 h-5" />
            {{ agent.stopping ? 'Stopping...' : 'Stop (Unregister)' }}
          </button>
        </div>

        <!-- Transfer Dialog -->
        <div
          v-if="showTransferDialog"
          class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
          @click.self="showTransferDialog = false"
        >
          <div
            class="p-6 rounded-lg shadow-xl max-w-sm w-full mx-4"
            :class="isDarkMode ? 'bg-black' : 'bg-white'"
          >
            <h4
              class="text-lg font-semibold mb-4"
              :class="isDarkMode ? 'text-white' : 'text-gray-900'"
            >
              Transfer Call
            </h4>
            <input
              v-model="transferTarget"
              type="text"
              placeholder="Enter extension or number"
              class="w-full px-4 py-2 rounded-lg border mb-4 focus:outline-none focus:ring-2"
              :class="isDarkMode
                ? 'bg-black border-gray-700 text-white focus:ring-amber-600'
                : 'bg-white border-gray-300 text-gray-900 focus:ring-amber-500'"
            />
            <div class="flex gap-2">
              <button
                @click="blindTransfer"
                :disabled="!transferTarget.trim()"
                class="flex-1 px-4 py-2 rounded-lg font-medium transition disabled:cursor-not-allowed"
                :class="!transferTarget.trim()
                  ? (isDarkMode ? 'bg-gray-700 text-gray-500' : 'bg-gray-300 text-gray-500')
                  : (isDarkMode ? 'bg-blue-600 hover:bg-blue-700 text-white' : 'bg-blue-500 hover:bg-blue-600 text-white')"
              >
                Blind Transfer
              </button>
              <button
                @click="showTransferDialog = false"
                class="flex-1 px-4 py-2 rounded-lg font-medium transition"
                :class="isDarkMode
                  ? 'bg-gray-700 hover:bg-gray-600 text-white'
                  : 'bg-gray-200 hover:bg-gray-300 text-gray-800'"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>

        <audio ref="remoteAudio" autoplay playsinline class="hidden"></audio>
      </div>
    </div>
>>>>>>> main
  </div>
</template>

<script setup>
import Dialpad from '@/components/softphone/Dialpad.vue'
import { inject } from 'vue'

const isDarkMode = inject('isDarkMode')
</script>
