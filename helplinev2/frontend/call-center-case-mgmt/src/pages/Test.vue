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
    
    myinvitefunction(invitation) {
      console.log("%c[onInvite] Incoming call received!", "color: green; font-weight: bold;");
      console.log("Full Invitation Object:", invitation);

      this.incomingCall = true;
      this.session = invitation;

      
      this.callerId = invitation.remoteIdentity?.uri?.user || "Unknown";
      this.remoteIdentity = invitation.remoteIdentity?.displayName || this.callerId;

      console.log(`Caller ID: ${this.callerId}`);
      console.log(`Remote Display Name: ${this.remoteIdentity}`);

      
      invitation.stateChange.addListener((state) => {
        console.log(`[Session State Change] New state: ${state}`);
        if (state === SIP.SessionState.Established) {
          console.log("%c[Call Connected]", "color: blue; font-weight: bold;");
        }
        if (state === SIP.SessionState.Terminated) {
          console.log("%c[Call Terminated]", "color: red; font-weight: bold;");
          this.resetCallState();
        }
      });
    },

    
    async answerCall() {
      if (!this.session) return;

      try {
        console.log("[Answer Call] Attempting to answer...");
        await this.session.accept({
          sessionDescriptionHandlerOptions: {
            constraints: { audio: true, video: false }
          }
        });

        this.inCall = true;
        this.incomingCall = false;

        
        const audioEl = this.$refs.remoteAudio;
        this.session.sessionDescriptionHandler.on("addTrack", () => {
          const pc = this.session.sessionDescriptionHandler.peerConnection;
          const remoteStream = new MediaStream();
          pc.getReceivers().forEach((receiver) => {
            if (receiver.track) remoteStream.addTrack(receiver.track);
          });
          audioEl.srcObject = remoteStream;
        });

        console.log("%c[Answer Call] Call answered successfully", "color: green; font-weight: bold;");
      } catch (err) {
        console.error("[Answer Call] Failed to answer:", err);
      }
    },

    
    async rejectCall() {
      if (!this.session) return;
      try {
        await this.session.reject();
        this.resetCallState();
        console.log("%c[Reject Call] Call rejected", "color: orange; font-weight: bold;");
      } catch (err) {
        console.error("[Reject Call] Failed to reject:", err);
      }
    },

    // Hang up active call
    async hangup() {
      if (!this.session) return;
      try {
        await this.session.terminate();
        console.log("%c[Hangup] Call terminated", "color: red; font-weight: bold;");
      } catch (err) {
        console.error("[Hangup] Failed to terminate:", err);
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
      console.log(`[Mute] Audio ${this.isMuted ? "Muted" : "Unmuted"}`);
    },

    // Start SIP agent
   startAgent() {
  try {
    const config = {
      uri: "sip:101@demo-openchs.bitz-itc.com",
      authorizationUsername: "101",
      authorizationPassword: "23kdefrtgos09812100",
       registerExpires: 300, // 5 minutes instead of 30 seconds
  keepAliveInterval: 30,
      displayName: "101",
      transportOptions: {
        server: "wss://demo-openchs.bitz-itc.com:8089/ws",
        traceSip: true, // Enables SIP message tracing
      },
      log: { level: "log" },
      delegate: { onInvite: this.myinvitefunction }
    };

    console.log("[SIP Agent] Starting with config:", config);

    this.ua = new SIP.UserAgent(config);

    // Listen for transport events
    this.ua.transport.onConnect = () => {
      console.log("[SIP Agent] Transport connected successfully");
    };
    this.ua.transport.onDisconnect = (error) => {
      console.error("[SIP Agent] Transport disconnected", error || "");
    };
    this.ua.transport.onClosed = (event) => {
      console.warn("[SIP Agent] Transport closed:", event);
    };

    // Start the UA
    this.ua.start()
      .then(() => {
        console.log("[SIP Agent] SIP Agent started successfully");
      })
      .catch((err) => {
        console.error("[SIP Agent] Failed to start SIP Agent:", err);
      });

  } catch (err) {
    console.error("[SIP Agent] Error starting SIP agent:", err);
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
        console.log("%c[SIP Agent] Stopped", "color: red; font-weight: bold;");
      } catch (err) {
        console.error("[SIP Agent] Failed to stop:", err);
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