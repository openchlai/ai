<template>
  <div class="sip-client">
    <h3>SIP Client (call center)</h3>

    <div class="status-row">
      <div><strong>Registered:</strong> {{ registered ? 'Yes' : 'No' }}</div>
      <div><strong>Agent:</strong> {{ extension }}</div>
      <div><strong>Connection:</strong> {{ connected ? 'Connected' : 'Disconnected' }}</div>
    </div>

    <div class="controls">
      <button @click="startAgent" :disabled="registered || starting">Start (Register)</button>
      <button @click="stopAgent" :disabled="!registered || stopping">Stop (Unregister)</button>
      <button @click="toggleMute" :disabled="!inCall">{{ isMuted ? 'Unmute' : 'Mute' }}</button>
      <button @click="hangup" :disabled="!inCall">Hangup</button>
    </div>

    <div v-if="incomingCall" class="incoming">
      <div><strong>Incoming call from:</strong> {{ callerId || 'Unknown' }}</div>
      <button @click="answerCall">Answer</button>
      <button @click="rejectCall">Reject</button>
    </div>

    <div v-if="inCall" class="call-info">
      <div><strong>On call with:</strong> {{ remoteIdentity || 'Remote' }}</div>
    </div>

    <!-- Hidden audio element for remote audio -->
    <audio ref="remoteAudio" autoplay playsinline></audio>
  </div>
</template>

<script>
import * as SIP from "sip.js";

export default {
  name: "Test",
  data() {
    return {
      ua: null,
      session: null,
      registered: false,
      connected: false,
      starting: false,
      stopping: false,
      incomingCall: false,
      inCall: false,
      isMuted: false,
      callerId: null,
      remoteIdentity: null,
      extension: "101"
    };
  },
  methods: {
    // Handle incoming call
    myinvitefunction(invitation) {
      console.log("Incoming call:", invitation);

      this.incomingCall = true;
      this.session = invitation;
      this.callerId = invitation.remoteIdentity.uri.user;
      this.remoteIdentity = invitation.remoteIdentity.displayName || this.callerId;

      // Attach session end events
      invitation.stateChange.addListener((state) => {
        if (state === SIP.SessionState.Terminated) {
          this.resetCallState();
        }
      });
    },

    // Answer incoming call
    async answerCall() {
      if (!this.session) return;

      try {
        await this.session.accept({
          sessionDescriptionHandlerOptions: {
            constraints: { audio: true, video: false }
          }
        });

        this.inCall = true;
        this.incomingCall = false;

        // Play remote audio
        const audioEl = this.$refs.remoteAudio;
        this.session.sessionDescriptionHandler.on("addTrack", () => {
          const pc = this.session.sessionDescriptionHandler.peerConnection;
          const remoteStream = new MediaStream();
          pc.getReceivers().forEach((receiver) => {
            if (receiver.track) remoteStream.addTrack(receiver.track);
          });
          audioEl.srcObject = remoteStream;
        });

        console.log("Call answered");
      } catch (err) {
        console.error("Failed to answer call:", err);
      }
    },

    // Reject incoming call
    async rejectCall() {
      if (!this.session) return;
      try {
        await this.session.reject();
        this.resetCallState();
        console.log("Call rejected");
      } catch (err) {
        console.error("Failed to reject call:", err);
      }
    },

    // Hang up active call
    async hangup() {
      if (!this.session) return;
      try {
        await this.session.terminate();
        console.log("Call terminated");
      } catch (err) {
        console.error("Failed to terminate call:", err);
      }
    },

    // Toggle mute/unmute
    toggleMute() {
      if (!this.session) return;
      const pc = this.session.sessionDescriptionHandler.peerConnection;
      pc.getSenders().forEach((sender) => {
        if (sender.track && sender.track.kind === "audio") {
          sender.track.enabled = this.isMuted;
        }
      });
      this.isMuted = !this.isMuted;
    },

    // Start SIP agent
    async startAgent() {
      try {
        this.starting = true;
        const config = {
          uri: "sip:101@demo-openchs.bitz-itc.com",
          authorizationUsername: "101",
          authorizationPassword: "23kdefrtgos09812100",
          displayName: "101",
          transportOptions: {
            server: "wss://demo-openchs.bitz-itc.com:8089/ws",
            traceSip: true,
          },
          log: { level: "log" },
          delegate: { onInvite: this.myinvitefunction }
        };

        console.log("Starting SIP agent with config:", config);

        this.ua = new SIP.UserAgent(config);

        this.ua.delegate = {
          onConnect: () => {
            this.connected = true;
            this.registered = true;
          },
          onDisconnect: () => {
            this.connected = false;
            this.registered = false;
          }
        };

        await this.ua.start();
        console.log("SIP Agent started successfully");
      } catch (err) {
        console.error("Failed to start SIP agent:", err);
      } finally {
        this.starting = false;
      }
    },

    // Stop SIP agent
    async stopAgent() {
      if (!this.ua) return;
      try {
        this.stopping = true;
        await this.ua.stop();
        this.registered = false;
        this.connected = false;
        console.log("SIP Agent stopped");
      } catch (err) {
        console.error("Failed to stop SIP agent:", err);
      } finally {
        this.stopping = false;
      }
    },

    // Reset call-related state
    resetCallState() {
      this.session = null;
      this.inCall = false;
      this.incomingCall = false;
      this.isMuted = false;
      this.callerId = null;
      this.remoteIdentity = null;
    }
  }
};
</script>

<style scoped>
.sip-client { padding: 12px; border: 1px solid #ddd; border-radius: 6px; max-width:420px; }
.status-row { display:flex; gap:12px; margin-bottom:8px; }
.controls button { margin-right:8px; }
.incoming { margin-top:12px; padding:8px; border:1px dashed #f39; background:#fff6f6 }
.call-info { margin-top:8px; padding:8px; border:1px solid #cfc; background:#f6fff6 }
</style>
