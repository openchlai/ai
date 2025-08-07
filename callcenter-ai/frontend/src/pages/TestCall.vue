<script>
    import { ref, computed, onMounted, onBeforeUnmount } from 'vue';
    import {
        initSIP,
        joinQueue,
        leaveQueue,
        answerCall,
        rejectCall,
        hangupCall,
        transferCall,
        muteCall,
        sendDTMF,
        on,
        off,
        cleanup,
        getCallStatus
    } from '@/utils/sipClient';

    export default {
        setup() {
            // Component state
            const sipStatus = ref({
                isRegistered: false,
                isInQueue: false,
                hasActiveCall: false,
                hasIncomingCall: false,
                callDuration: '00:00:00'
            });

            const callInfo = ref({
                active: null,
                incoming: null
            });

            const isMuted = ref(false);

            // Computed properties
            const callButtonsDisabled = computed(() => !sipStatus.value.isRegistered);
            const callDurationFormatted = computed(() => {
                // Format call duration for display
                return sipStatus.value.callDuration;
            });

            // Initialize SIP client
            const initializeSip = async () => {
                try {
                    const sipDetails = JSON.parse(localStorage.getItem(''));

                    if (!sipDetails?.uri || !sipDetails?.password || !sipDetails?.websocketURL) {
                        throw new Error('Missing SIP connection details');
                    }

                    await initSIP({
                        sipUri: sipDetails.uri,
                        password: sipDetails.password,
                        websocketURL: sipDetails.websocketURL,
                        debug: true
                    });

                    setupEventListeners();

                } catch (error) {
                    console.error('SIP initialization failed:', error);
                }
            };

            // Set up all event listeners
            const setupEventListeners = () => {
                on('onRegistered', () => {
                    sipStatus.value.isRegistered = true;
                    console.log('SIP registered successfully');
                });

                on('onRegistrationFailed', (error) => {
                    sipStatus.value.isRegistered = false;
                    console.error('Registration failed:', error);
                });

                on('onIncomingCall', (session) => {
                    callInfo.value.incoming = {
                        session,
                        callerId: session.remote_identity.uri.user,
                        callerName: session.remote_identity.display_name || session.remote_identity.uri.user
                    };
                    sipStatus.value.hasIncomingCall = true;
                });

                // ... other event listeners
            };

            // Call control functions
            const answerIncomingCall = async () => {
                try {
                    await answerCall();
                    startCallTimer();
                } catch (error) {
                    console.error('Failed to answer call:', error);
                }
            };

            const transferActiveCall = (extension) => {
                try {
                    transferCall(extension);
                } catch (error) {
                    console.error('Transfer failed:', error);
                }
            };

            // Clean up on component unmount
            onBeforeUnmount(() => {
                cleanup();
                // Remove all event listeners
                off('onRegistered');
                off('onRegistrationFailed');
                off('onIncomingCall');
                // ... other event listeners
            });

            onMounted(() => {
                initializeSip();
            });

            return {
                sipStatus,
                callInfo,
                isMuted,
                callButtonsDisabled,
                callDurationFormatted,
                initSIP,
                joinQueue,
                leaveQueue,
                answerCall,
                rejectCall,
                hangupCall,
                transferCall,
                muteCall,
                sendDTMF,
                on,
                off,
                cleanup,
            };
        }
    }
</script>

<template>
    <div class="sip-phone">
        <!-- Status display -->
        <div class="status">
            <span :class="['indicator', sipStatus.isRegistered ? 'connected' : 'disconnected']"></span>
            {{ sipStatus.isRegistered ? 'Connected' : 'Disconnected' }}
        </div>

        <!-- Queue control -->
        <button @click="toggleQueue" :disabled="!sipStatus.isRegistered">
            {{ sipStatus.isInQueue ? 'Leave Queue' : 'Join Queue' }}
        </button>

        <!-- Incoming call UI -->
        <div v-if="sipStatus.hasIncomingCall" class="incoming-call">
            <h3>Incoming Call</h3>
            <p>{{ callInfo.incoming.callerName }} ({{ callInfo.incoming.callerId }})</p>
            <button @click="answerIncomingCall">Answer</button>
            <button @click="rejectCall">Reject</button>
        </div>

        <!-- Active call UI -->
        <div v-if="sipStatus.hasActiveCall" class="active-call">
            <h3>Active Call</h3>
            <p>{{ callInfo.active.callerName }} ({{ callInfo.active.callerId }})</p>
            <p>Duration: {{ callDurationFormatted }}</p>

            <div class="call-controls">
                <button @click="toggleMute">
                    {{ isMuted ? 'Unmute' : 'Mute' }}
                </button>
                <button @click="hangupCall">Hang Up</button>

                <!-- DTMF pad -->
                <div class="dtmf-pad">
                    <button v-for="num in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '*', '0', '#']" :key="num"
                        @click="sendDTMF(num)">
                        {{ num }}
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
    .sip-phone {
        max-width: 400px;
        margin: 20px auto;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        background-color: #ffffff;
    }

    .status {
        display: flex;
        align-items: center;
        margin-bottom: 20px;
        padding: 10px;
        background-color: #f5f5f5;
        border-radius: 4px;
    }

    .indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 5px;
    }

    .indicator.connected {
        background-color: #4CAF50;
    }

    .indicator.disconnected {
        background-color: #f44336;
    }

    button {
        padding: 10px 20px;
        margin: 5px;
        border: none;
        border-radius: 4px;
        background-color: #2196F3;
        color: white;
        cursor: pointer;
        transition: background-color 0.3s;
    }

    button:hover {
        background-color: #1976D2;
    }

    button:disabled {
        background-color: #BDBDBD;
        cursor: not-allowed;
    }

    .incoming-call, .active-call {
        margin-top: 20px;
        padding: 15px;
        border: 1px solid #E0E0E0;
        border-radius: 4px;
    }

    h3 {
        margin: 0 0 10px 0;
        color: #333;
    }

    .call-controls {
        margin-top: 15px;
    }

    .dtmf-pad {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 8px;
        margin-top: 15px;
        padding: 10px;
        background-color: #f5f5f5;
        border-radius: 4px;
    }

    .dtmf-pad button {
        padding: 15px;
        font-size: 1.2em;
        background-color: #ffffff;
        color: #333;
        border: 1px solid #E0E0E0;
    }

    .dtmf-pad button:hover {
        background-color: #f0f0f0;
    }

    p {
        margin: 8px 0;
        color: #666;
    }
</style>