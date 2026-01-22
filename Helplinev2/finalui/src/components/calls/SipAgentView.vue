<template>
  <div class="space-y-6">
    <div class="max-w-md mx-auto">
      <!-- Loading state -->
      <div
        v-if="loadingExtension"
        class="p-6 border rounded-lg shadow-xl"
        :class="isDarkMode
          ? 'border-transparent bg-gray-800'
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
          ? 'border-transparent bg-gray-800'
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
              ? 'bg-gray-900/40 border-transparent'
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
              ? 'bg-gray-900/40 border-transparent'
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
              ? 'bg-gray-900/40 border-transparent'
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
              ? 'bg-gray-900/40 border-transparent'
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
                ? 'bg-gray-900 border-gray-700 text-white focus:ring-amber-600'
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
            :class="isDarkMode ? 'bg-gray-800' : 'bg-white'"
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
                ? 'bg-gray-900 border-gray-700 text-white focus:ring-amber-600'
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
  </div>
</template>

<script>
import * as SIP from "sip.js";
import { useAuthStore } from '@/stores/auth';
import { useUserStore } from '@/stores/users';
import { inject } from 'vue';
import { config, getSipConfig, getIceServers } from '@/config/sip';
import axiosInstance from '@/utils/axios';

export default {
  name: "SipAgentView",
  setup() {
    const isDarkMode = inject('isDarkMode');
    return { isDarkMode };
  },
  data() {
    return {
      agent: {
        ua: null,
        registerer: null,
        registered: false,
        connected: false,
        starting: false,
        stopping: false,
        session: null,
        inCall: false,
        isOnHold: false,
        callStatus: '',
        localStream: null,
        extension: null,
        callDirection: null // 'inbound' or 'outbound'
      },
      queue: {
        inQueue: false,
        loading: false
      },
      autoAnswer: false,
      dialNumber: '',
      showDtmfPad: false,
      showTransferDialog: false,
      transferTarget: '',
      dtmfKeys: ['1', '2', '3', '4', '5', '6', '7', '8', '9', '*', '0', '#'],
      loadingExtension: true,
      extensionError: null
    };
  },
  async mounted() {
    await this.fetchUserExtension();
  },
  methods: {
    async fetchUserExtension() {
      this.loadingExtension = true;
      this.extensionError = null;

      try {
        const authStore = useAuthStore();
        const userStore = useUserStore();

        const userId = authStore.userId;

        if (!userId) {
          throw new Error('User ID not found. Please log in again.');
        }

        console.log('[SIP] Fetching extension for user ID:', userId);

        const userData = await userStore.viewUser(userId);

        console.log('[SIP] User data received:', userData);

        const user = userData?.users?.[0];

        if (!user) {
          throw new Error('User data not found.');
        }

        const extenIndex = userData?.users_k?.exten?.[0];

        if (!extenIndex) {
          throw new Error('Extension mapping not found.');
        }

        const extension = user[extenIndex];

        if (!extension) {
          throw new Error('Extension not assigned to this user.');
        }

        this.agent.extension = extension;
        console.log('[SIP] Extension set to:', extension);

      } catch (err) {
        console.error('[SIP] Error fetching extension:', err);
        this.extensionError = err.message || 'Failed to load extension';
      } finally {
        this.loadingExtension = false;
      }
    },

    setupMediaStreams(session, audioRef) {
      const pc = session.sessionDescriptionHandler.peerConnection;

      const inboundStream = new MediaStream();
      pc.getReceivers().forEach((receiver) => {
        if (receiver.track && receiver.track.kind === "audio") {
          inboundStream.addTrack(receiver.track);
        }
      });

      if (inboundStream.getTracks().length > 0) {
        audioRef.srcObject = inboundStream;
        audioRef.play().catch(err => console.error("[SIP] Play failed:", err));
      }

      console.log(`[SIP:${this.agent.extension}] Media streams setup complete`);
    },

    cleanupMedia() {
      if (this.$refs.remoteAudio) {
        this.$refs.remoteAudio.srcObject = null;
      }
    },

    handleSessionStateChange(session, state) {
      console.log(`[SIP:${this.agent.extension}] Session state:`, state);

      switch (state) {
        case SIP.SessionState.Initial:
          this.agent.callStatus = 'Initializing...';
          break;
        case SIP.SessionState.Establishing:
          this.agent.callStatus = this.agent.callDirection === 'outbound'
            ? 'Calling...'
            : 'Incoming call...';
          break;
        case SIP.SessionState.Established:
          this.agent.callStatus = 'Connected';
          this.cleanupMedia();
          this.setupMediaStreams(session, this.$refs.remoteAudio);
          break;
        case SIP.SessionState.Terminating:
          this.agent.callStatus = 'Ending call...';
          break;
        case SIP.SessionState.Terminated:
          this.agent.inCall = false;
          this.agent.session = null;
          this.agent.isOnHold = false;
          this.agent.callStatus = 'Call ended';
          this.agent.callDirection = null;
          this.cleanupMedia();
          this.showDtmfPad = false;
          break;
      }
    },

    async handleIncomingCall(invitation) {
      console.log(`[SIP:${this.agent.extension}] Incoming call from:`, invitation.remoteIdentity?.uri?.user);

      // Auto-answer if enabled
      if (this.autoAnswer) {
        const displayName = invitation.remoteIdentity?.displayName;
        console.log(`[SIP:${this.agent.extension}] Auto-answering call from:`, displayName || invitation.remoteIdentity?.uri?.user);
        try {
          await invitation.accept({
            sessionDescriptionHandlerOptions: {
              constraints: { audio: true, video: false }
            }
          });
        } catch (err) {
          console.error(`[SIP:${this.agent.extension}] Auto-answer failed:`, err);
        }
        return;
      }

      this.agent.callDirection = 'inbound';
      this.agent.callStatus = `Incoming: ${invitation.remoteIdentity?.uri?.user || 'Unknown'}`;

      try {
        if (!this.agent.localStream) {
          this.agent.localStream = await navigator.mediaDevices.getUserMedia({
            audio: {
              echoCancellation: true,
              noiseSuppression: true,
              autoGainControl: true
            }
          });
        }

        this.agent.session = invitation;
        this.agent.inCall = true;

        invitation.stateChange.addListener((state) => {
          this.handleSessionStateChange(invitation, state);
        });

        await invitation.accept({
          sessionDescriptionHandlerOptions: {
            constraints: { audio: true, video: false }
          }
        });

        // Add local tracks
        const pc = invitation.sessionDescriptionHandler.peerConnection;
        this.agent.localStream.getTracks().forEach(track => {
          pc.addTrack(track, this.agent.localStream);
        });

      } catch (err) {
        console.error(`[SIP:${this.agent.extension}] Error handling incoming call:`, err);
        this.agent.callStatus = 'Error accepting call';
        this.agent.inCall = false;
      }
    },

    async makeCall() {
      if (!this.dialNumber.trim() || !this.agent.ua || this.agent.inCall) return;

      console.log(`[SIP:${this.agent.extension}] Dialing:`, this.dialNumber);
      this.agent.callDirection = 'outbound';

      try {
        if (!this.agent.localStream) {
          this.agent.localStream = await navigator.mediaDevices.getUserMedia({
            audio: {
              echoCancellation: true,
              noiseSuppression: true,
              autoGainControl: true
            }
          });
        }

        const target = SIP.UserAgent.makeURI(`sip:${this.dialNumber}@${config.SIP_HOST}`);
        if (!target) {
          throw new Error('Invalid dial target');
        }

        const inviter = new SIP.Inviter(this.agent.ua, target, {
          sessionDescriptionHandlerOptions: {
            constraints: { audio: true, video: false }
          }
        });

        this.agent.session = inviter;
        this.agent.inCall = true;

        // Set up call timeout
        const callTimeout = setTimeout(() => {
          if (inviter.state !== SIP.SessionState.Established &&
              inviter.state !== SIP.SessionState.Terminated) {
            console.log(`[SIP:${this.agent.extension}] Call timeout - no answer after ${config.SIP_CALL_TIMEOUT}ms`);
            inviter.cancel();
            this.agent.callStatus = 'No answer';
          }
        }, config.SIP_CALL_TIMEOUT);

        inviter.stateChange.addListener((state) => {
          // Clear timeout when call is established or terminated
          if (state === SIP.SessionState.Established ||
              state === SIP.SessionState.Terminated) {
            clearTimeout(callTimeout);
          }
          this.handleSessionStateChange(inviter, state);
        });

        await inviter.invite();
        console.log(`[SIP:${this.agent.extension}] INVITE sent`);

        // Add local tracks after invite
        const pc = inviter.sessionDescriptionHandler.peerConnection;
        this.agent.localStream.getTracks().forEach(track => {
          pc.addTrack(track, this.agent.localStream);
        });

        this.dialNumber = '';

      } catch (err) {
        console.error(`[SIP:${this.agent.extension}] Error making call:`, err);
        this.agent.callStatus = 'Call failed: ' + err.message;
        this.agent.inCall = false;
        this.agent.session = null;
      }
    },

    async toggleHold() {
      if (!this.agent.session) return;

      const newHoldState = !this.agent.isOnHold;
      console.log(`[SIP:${this.agent.extension}] ${newHoldState ? 'Holding' : 'Resuming'} call`);

      try {
        const options = {
          requestDelegate: {
            onAccept: () => {
              console.log(`[SIP:${this.agent.extension}] Hold ${newHoldState ? 'accepted' : 'released'}`);
              this.agent.isOnHold = newHoldState;

              // Mute/unmute local tracks
              const pc = this.agent.session.sessionDescriptionHandler.peerConnection;
              pc.getSenders().forEach(sender => {
                if (sender.track) {
                  sender.track.enabled = !newHoldState;
                }
              });
            },
            onReject: () => {
              console.warn(`[SIP:${this.agent.extension}] Hold ${newHoldState ? 'activation' : 'release'} rejected`);
            }
          }
        };

        // Set hold state on session description handler options
        const sessionDescriptionHandlerOptions = this.agent.session.sessionDescriptionHandlerOptionsReInvite || {};
        sessionDescriptionHandlerOptions.hold = newHoldState;
        this.agent.session.sessionDescriptionHandlerOptionsReInvite = sessionDescriptionHandlerOptions;

        // Send re-INVITE
        await this.agent.session.invite(options);
      } catch (err) {
        console.error(`[SIP:${this.agent.extension}] Error toggling hold:`, err);
      }
    },

    sendDtmf(digit) {
      if (!this.agent.session) return;

      console.log(`[SIP:${this.agent.extension}] Sending DTMF:`, digit);

      try {
        // Send DTMF via INFO message (RFC 2976)
        const body = {
          contentDisposition: 'render',
          contentType: 'application/dtmf-relay',
          content: `Signal=${digit}\r\nDuration=100`
        };

        this.agent.session.info({ requestOptions: { body } });
      } catch (err) {
        console.error(`[SIP:${this.agent.extension}] Error sending DTMF:`, err);
      }
    },

    async blindTransfer() {
      if (!this.agent.session || !this.transferTarget.trim()) return;

      console.log(`[SIP:${this.agent.extension}] Blind transfer to:`, this.transferTarget);

      try {
        const target = SIP.UserAgent.makeURI(`sip:${this.transferTarget}@${config.SIP_HOST}`);
        if (!target) {
          throw new Error('Invalid transfer target');
        }

        await this.agent.session.refer(target);
        console.log(`[SIP:${this.agent.extension}] Transfer initiated`);

        this.showTransferDialog = false;
        this.transferTarget = '';
      } catch (err) {
        console.error(`[SIP:${this.agent.extension}] Error transferring call:`, err);
      }
    },

    async toggleQueue() {
      this.queue.loading = true;

      try {
        const action = this.queue.inQueue ? '0' : '1';
        const body = this.queue.inQueue
          ? { action: '0', break: 'coffee' }
          : { action: '1' };

        console.log(`[SIP:${this.agent.extension}] ${this.queue.inQueue ? 'Leaving' : 'Joining'} queue`);

        await axiosInstance.post('/api/agent/', body);

        this.queue.inQueue = !this.queue.inQueue;
        console.log(`[SIP:${this.agent.extension}] Queue status:`, this.queue.inQueue ? 'In queue' : 'Not in queue');
      } catch (err) {
        console.error(`[SIP:${this.agent.extension}] Error toggling queue:`, err);
      } finally {
        this.queue.loading = false;
      }
    },

    startAgent() {
      this.agent.starting = true;

      try {
        const uri = SIP.UserAgent.makeURI(config.buildSipUri(this.agent.extension));
        if (!uri) throw new Error("Invalid SIP URI");

        const sipConfig = getSipConfig(this.agent.extension, {
          onInvite: (invitation) => this.handleIncomingCall(invitation)
        });

        sipConfig.uri = uri;

        console.log(`[SIP:${this.agent.extension}] Starting agent with config:`, {
          uri: uri.toString(),
          server: sipConfig.transportOptions.server
        });

        this.agent.ua = new SIP.UserAgent(sipConfig);

        this.agent.ua.transport.onConnect = () => {
          console.log(`[SIP:${this.agent.extension}] Transport connected`);
          this.agent.connected = true;
        };

        this.agent.ua.transport.onDisconnect = (error) => {
          console.warn(`[SIP:${this.agent.extension}] Transport disconnected`, error);
          this.agent.connected = false;
          this.agent.registered = false;
        };

        this.agent.ua.start()
          .then(() => {
            console.log(`[SIP:${this.agent.extension}] Agent started`);
            this.agent.registerer = new SIP.Registerer(this.agent.ua);

            this.agent.registerer.stateChange.addListener((state) => {
              if (state === SIP.RegistererState.Registered) {
                console.log(`[SIP:${this.agent.extension}] Registered`);
                this.agent.registered = true;
              } else if (state === SIP.RegistererState.Unregistered) {
                console.log(`[SIP:${this.agent.extension}] Unregistered`);
                this.agent.registered = false;
              }
            });

            this.agent.registerer.register();
          })
          .catch(err => {
            console.error(`[SIP:${this.agent.extension}] Failed to start:`, err);
            this.agent.callStatus = 'Failed to connect';
          })
          .finally(() => this.agent.starting = false);

      } catch (err) {
        console.error(`[SIP:${this.agent.extension}] Error starting agent:`, err);
        this.agent.starting = false;
      }
    },

    hangup() {
      if (!this.agent.session) return;

      console.log(`[SIP:${this.agent.extension}] Hanging up`);

      try {
        const state = this.agent.session.state;

        if (state === SIP.SessionState.Initial || state === SIP.SessionState.Establishing) {
          // Call not yet established
          if (this.agent.callDirection === 'outbound') {
            this.agent.session.cancel();
          } else {
            this.agent.session.reject();
          }
        } else if (state === SIP.SessionState.Established) {
          this.agent.session.bye();
        }
      } catch (err) {
        console.error(`[SIP:${this.agent.extension}] Error hanging up:`, err);
      }
    },

    stopAgent() {
      if (!this.agent.registerer || !this.agent.ua) return;

      this.agent.stopping = true;

      // Leave queue first if in queue
      if (this.queue.inQueue) {
        this.toggleQueue().catch(() => {});
      }

      this.agent.registerer.unregister()
        .then(() => {
          console.log(`[SIP:${this.agent.extension}] Unregistered`);
          return this.agent.ua.stop();
        })
        .then(() => {
          this.agent.connected = false;
          this.agent.registered = false;
          this.agent.ua = null;
          this.agent.registerer = null;
          this.agent.callStatus = '';

          if (this.agent.localStream) {
            this.agent.localStream.getTracks().forEach(track => track.stop());
            this.agent.localStream = null;
          }
        })
        .catch(err => console.error(`[SIP:${this.agent.extension}] Error stopping:`, err))
        .finally(() => this.agent.stopping = false);
    }
  },
  beforeUnmount() {
    if (this.agent.registered) {
      this.stopAgent();
    }
  }
};
</script>
