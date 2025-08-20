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
    </div>

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
      registerer: null,
      registered: false,
      connected: false,
      extension: "101",
      starting: false,
      stopping: false
    };
  },
  methods: {
async myinvitefunction(invitation) {
  console.log("Incoming call:", invitation);

  try {
    // Use pre-fetched mic stream if possible
    if (!this.localStream) {
      this.localStream = await navigator.mediaDevices.getUserMedia({ audio: true });
    }

    await invitation.accept({
      sessionDescriptionHandlerOptions: {
        constraints: { audio: true, video: false },
        localStream: this.localStream
      }
    });

    const remoteAudio = this.$refs.remoteAudio;

    invitation.stateChange.addListener((state) => {
      if (state === SIP.SessionState.Established) {
        const pc = invitation.sessionDescriptionHandler.peerConnection;

        // Ensure mic is in outbound stream
        this.localStream.getTracks().forEach(track => {
          pc.addTrack(track, this.localStream);
        });

        // Capture incoming audio
        const inboundStream = new MediaStream();
        pc.getReceivers().forEach((receiver) => {
          if (receiver.track && receiver.track.kind === "audio") {
            inboundStream.addTrack(receiver.track);
          }
        });
        remoteAudio.srcObject = inboundStream;
        remoteAudio.play().catch(err => console.error("Play failed:", err));
      }
    });

  } catch (err) {
    console.error("Error handling incoming call:", err);
  }
}

,
    startAgent() {
      this.starting = true;
      try {
        const uri = SIP.UserAgent.makeURI(`sip:${this.extension}@demo-openchs.bitz-itc.com`);
        if (!uri) throw new Error("Invalid SIP URI");

        const config = {
          uri,
          authorizationUsername: this.extension,
          authorizationPassword: "23kdefrtgos09812100",
          displayName: this.extension,
          transportOptions: {
            server: "wss://demo-openchs.bitz-itc.com:8089/ws",
            traceSip: true,
          },
          log: { level: "log" },
          delegate: {
            onInvite: this.myinvitefunction
          }
        };

        console.log("Starting SIP agent with config:", config);
        this.ua = new SIP.UserAgent(config);

        // Detect connection
        this.ua.transport.onConnect = () => {
          console.log("[SIP Agent] Transport connected");
          this.connected = true;
        };

        // Detect disconnection
        this.ua.transport.onDisconnect = (error) => {
          console.warn("[SIP Agent] Transport disconnected", error);
          this.connected = false;
          this.registered = false;
        };

        this.ua.start()
          .then(() => {
            console.log("SIP Agent started");

            // Create and track registerer
            this.registerer = new SIP.Registerer(this.ua);

            this.registerer.stateChange.addListener((state) => {
              if (state === SIP.RegistererState.Registered) {
                console.log("[SIP Agent] Registered");
                this.registered = true;
              } else if (state === SIP.RegistererState.Unregistered) {
                console.log("[SIP Agent] Unregistered");
                this.registered = false;
              }
            });

            this.registerer.register();
          })
          .catch(err => console.error("Failed to start SIP agent:", err))
          .finally(() => this.starting = false);

      } catch (err) {
        console.error("Error starting SIP agent:", err);
        this.starting = false;
      }
    },

    stopAgent() {
      if (!this.registerer || !this.ua) return;
      this.stopping = true;
      this.registerer.unregister()
        .then(() => {
          console.log("[SIP Agent] Unregistered manually");
          return this.ua.stop();
        })
        .then(() => {
          this.connected = false;
          this.registered = false;
          this.ua = null;
          this.registerer = null;
        })
        .catch(err => console.error("Error stopping SIP agent:", err))
        .finally(() => this.stopping = false);
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