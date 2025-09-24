<template>
  <div class="counsellors-section">
    <div class="section-header">
      <h2 class="section-title">Counsellors Online: {{ count }}</h2>
    </div>
    <div class="counsellors-table">
      <div class="table-header">
        <div class="col-ext">Ext.</div>
        <div class="col-name">Name</div>
        <div class="col-caller">Caller</div>
        <div class="col-answered">Answered</div>
        <div class="col-missed">Missed</div>
        <div class="col-talk-time">Talk Time</div>
        <div class="col-queue-status">Queue Status</div>
        <div class="col-duration">Duration</div>
      </div>
      <div class="table-body">
        <div v-if="counsellors.length === 0" class="no-counsellors-row">
          <div class="no-counsellors-text">No counsellors currently online</div>
        </div>
        <div v-for="c in counsellors" :key="c.id" class="table-row">
          <div class="col-ext">{{ c.extension }}</div>
          <div class="col-name">{{ c.name }}</div>
          <div class="col-caller">{{ c.caller || "--" }}</div>
          <div class="col-answered">{{ c.answered || "0" }}</div>
          <div class="col-missed">{{ c.missed || "0" }}</div>
          <div class="col-talk-time">{{ c.talkTime || "--" }}</div>
          <div :class="['col-queue-status', statusClass(c.queueStatus)]">
            {{ c.queueStatus || "Offline" }}
          </div>
          <div class="col-duration">{{ c.duration || "--" }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
  defineProps({
    counsellors: {
      type: Array,
      default: () => [],   // ensure empty array
    },
    count: {
      type: Number,
      default: 0,
    },
    statusClass: {
      type: Function,
      default: () => () => "status-neutral",
    },
  });
</script>

