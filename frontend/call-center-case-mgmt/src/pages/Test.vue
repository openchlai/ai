<script setup>
import { onMounted, ref } from 'vue'

const ws = ref(null)
const localStream = ref(null)
const peerConnection = ref(null)
const remoteAudio = ref(null)

const username = prompt("Enter your username:")
const targetUser = ref('') // Call recipient

const servers = { iceServers: [{ urls: 'stun:stun.l.google.com:19302' }] }

onMounted(async () => {
  ws.value = new WebSocket('ws://localhost:3001')
  ws.value.onopen = () => ws.value.send(JSON.stringify({ type: 'register', name: username }))
  ws.value.onmessage = handleSignalingData

  localStream.value = await navigator.mediaDevices.getUserMedia({ audio: true })
})

function handleSignalingData({ data }) {
  const msg = JSON.parse(data)

  switch (msg.type) {
    case 'offer':
      receiveOffer(msg)
      break
    case 'answer':
      peerConnection.value.setRemoteDescription(new RTCSessionDescription(msg.answer))
      break
    case 'ice-candidate':
      peerConnection.value.addIceCandidate(new RTCIceCandidate(msg.candidate))
      break
    case 'call':
      alert(`Incoming call from ${msg.from}`)
      targetUser.value = msg.from
      start(true)
      break
  }
}

function send(msg) {
  msg.name = username
  msg.target = targetUser.value
  ws.value.send(JSON.stringify(msg))
}

async function start(isReceiving = false) {
  peerConnection.value = new RTCPeerConnection(servers)

  peerConnection.value.onicecandidate = e => {
    if (e.candidate) send({ type: 'ice-candidate', candidate: e.candidate })
  }

  peerConnection.value.ontrack = e => {
    if (remoteAudio.value) remoteAudio.value.srcObject = e.streams[0]
  }

  localStream.value.getTracks().forEach(track => {
    peerConnection.value.addTrack(track, localStream.value)
  })

  if (!isReceiving) {
    const offer = await peerConnection.value.createOffer()
    await peerConnection.value.setLocalDescription(offer)
    send({ type: 'offer', offer })
    send({ type: 'call', from: username })
  }
}

async function receiveOffer(msg) {
  await start(true)
  await peerConnection.value.setRemoteDescription(new RTCSessionDescription(msg.offer))
  const answer = await peerConnection.value.createAnswer()
  await peerConnection.value.setLocalDescription(answer)
  send({ type: 'answer', answer })
}
</script>

<template>
  <div class="p-4">
    <h2 class="text-xl">Call Interface - {{ username }}</h2>
    <input v-model="targetUser" placeholder="Target user" class="border p-2 my-2" />
    <button @click="start()">Start Call</button>
    <br /><br />
    <audio ref="remoteAudio" autoplay controls />
  </div>
</template>
