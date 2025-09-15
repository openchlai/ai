<template>
  <div class="container">
    <!-- Header -->
    <div class="header">
      <h1>Sauti Helpline Wallboard</h1>
      <p>Real-time counselling and support</p>
    </div>

    <!-- Cases Grid Row (Highly visible) -->
    <div class="cases-grid">
      <div 
        v-for="item in casesTiles" 
        :key="item.id" 
        :class="['case-card', item.variant]"
      >
        <div class="case-inner">
          <div v-if="item.value" class="case-value">{{ item.value }}</div>
          <div class="case-label">{{ item.label }}</div>
        </div>
      </div>
    </div>

    

    <!-- Top Statistics Row -->
    <div class="top-stats-row">
      <div 
        v-for="stat in stats" 
        :key="stat.id" 
        :class="['stat-card', stat.variant]"
      >
        <div class="stat-content">
          <div class="stat-label">{{ stat.title.toUpperCase() }}</div>
          <div class="stat-value">{{ stat.value }}</div>
        </div>
      </div>
    </div>

    
    <!-- Counsellors Section Only -->
    <div class="counsellors-section">
      <div class="section-header">
        <h2 class="section-title">Counsellors Online: {{ filteredCounsellors.length }}</h2>
        <div class="filter-buttons">
          <button 
            v-for="f in filters" 
            :key="f.id"
            :class="['filter-btn', { active: activeFilter === f.id }]"
            @click="setActiveFilter(f.id)"
          >
            {{ f.label }}
          </button>
        </div>
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
          <div v-if="filteredCounsellors.length === 0" class="no-counsellors-row">
            <div class="no-counsellors-text">No counsellors currently online</div>
          </div>
          <div 
            v-for="counsellor in filteredCounsellors" 
            :key="counsellor.id"
            class="table-row"
          >
            <div class="col-ext">{{ counsellor.extension }}</div>
            <div class="col-name">{{ counsellor.name }}</div>
            <div class="col-caller">{{ counsellor.caller || '--' }}</div>
            <div class="col-answered">{{ counsellor.answered || '0' }}</div>
            <div class="col-missed">{{ counsellor.missed || '0' }}</div>
            <div class="col-talk-time">{{ counsellor.talkTime || '--' }}</div>
            <div :class="['col-queue-status', statusClass(counsellor.queueStatus)]">{{ counsellor.queueStatus || 'Available' }}</div>
            <div class="col-duration">{{ counsellor.duration || '--' }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'

export default {
  name: 'App',
  setup() {
    const searchQuery = ref('')
    
    // Real data for counsellors (currently 0 online)
    const counsellors = ref([
      {
        id: 1,
        extension: '201',
        name: 'Asha N.',
        phone: '+255713000111',
        caller: '+255713000111',
        answered: '23',
        missed: '2',
        talkTime: '01:12:33',
        queueStatus: 'On Call',
        duration: '07:42',
        timeOnline: '2h 15m'
      },
      {
        id: 2,
        extension: '202',
        name: 'Brian K.',
        phone: '+255762555222',
        caller: '--',
        answered: '18',
        missed: '1',
        talkTime: '00:58:21',
        queueStatus: 'Available',
        duration: '--',
        timeOnline: '1h 48m'
      },
      {
        id: 3,
        extension: '203',
        name: 'Catherine O.',
        phone: '+255768123333',
        caller: '+255768123333',
        answered: '30',
        missed: '4',
        talkTime: '01:45:10',
        queueStatus: 'Ringing',
        duration: '00:03',
        timeOnline: '3h 02m'
      },
      {
        id: 4,
        extension: '204',
        name: 'Daniel M.',
        phone: '+255719444444',
        caller: '--',
        answered: '12',
        missed: '3',
        talkTime: '00:31:04',
        queueStatus: 'In Queue',
        duration: '--',
        timeOnline: '54m'
      },
      {
        id: 5,
        extension: '205',
        name: 'Elena T.',
        phone: '+255788555555',
        caller: '+255788555555',
        answered: '27',
        missed: '0',
        talkTime: '01:05:40',
        queueStatus: 'On Call',
        duration: '02:19',
        timeOnline: '2h 41m'
      },
      {
        id: 6,
        extension: '206',
        name: 'Faisal R.',
        phone: '+255750666666',
        caller: '--',
        answered: '7',
        missed: '1',
        talkTime: '00:14:02',
        queueStatus: 'Available',
        duration: '--',
        timeOnline: '22m'
      }
      ,{
        id: 7,
        extension: '207',
        name: 'Grace P.',
        phone: '+255710777777',
        caller: '+255710777777',
        answered: '15',
        missed: '2',
        talkTime: '00:42:50',
        queueStatus: 'On Call',
        duration: '01:12',
        timeOnline: '1h 05m'
      }
      ,{
        id: 8,
        extension: '208',
        name: 'Hassan J.',
        phone: '+255720888888',
        caller: '--',
        answered: '19',
        missed: '3',
        talkTime: '00:52:31',
        queueStatus: 'In Queue',
        duration: '--',
        timeOnline: '2h 10m'
      }
      ,{
        id: 9,
        extension: '209',
        name: 'Irene L.',
        phone: '+255730999999',
        caller: '+255730999999',
        answered: '11',
        missed: '1',
        talkTime: '00:27:44',
        queueStatus: 'Ringing',
        duration: '00:05',
        timeOnline: '38m'
      }
      ,{
        id: 10,
        extension: '210',
        name: 'Jonas C.',
        phone: '+255740101010',
        caller: '--',
        answered: '9',
        missed: '0',
        talkTime: '00:19:12',
        queueStatus: 'Available',
        duration: '--',
        timeOnline: '1h 22m'
      }
      ,{
        id: 11,
        extension: '211',
        name: 'Khadija S.',
        phone: '+255750111111',
        caller: '+255750111111',
        answered: '21',
        missed: '2',
        talkTime: '01:03:02',
        queueStatus: 'On Call',
        duration: '03:45',
        timeOnline: '3h 15m'
      }
      ,{
        id: 12,
        extension: '212',
        name: 'Lukas V.',
        phone: '+255760121212',
        caller: '--',
        answered: '5',
        missed: '1',
        talkTime: '00:09:54',
        queueStatus: 'In Queue',
        duration: '--',
        timeOnline: '15m'
      }
    ])

    // Top statistics tiles
    const stats = ref([
      { id: 1, title: 'Total', value: '3628', variant: 'total' },
      { id: 2, title: 'Answered', value: '154', variant: 'answered' },
      { id: 3, title: 'Abandoned', value: '1437', variant: 'abandoned' },
      { id: 4, title: 'Discarded', value: '9', variant: 'discarded' },
      { id: 5, title: 'Missed', value: '10', variant: 'missed' },
      { id: 6, title: 'IVR', value: '1750', variant: 'ivr' },
      { id: 7, title: 'Beep', value: '268', variant: 'beep' }
    ])

    // Highly-visible cases tiles (dummy data)
    const casesTiles = ref([
      { id: 'ct1', label: "TODAY'S RESPONSIVE CALLS", value: null, variant: 'c-blue' },
      { id: 'ct2', label: "TODAY'S CASES", value: '29', variant: 'c-amber' },
      { id: 'ct3', label: 'ONGOING CASES', value: '2425', variant: 'c-red' },
      { id: 'ct4', label: 'MONTH CLOSED CASES', value: '60897', variant: 'c-green' },
      { id: 'ct5', label: 'RESPONSIVE CALLS', value: null, variant: 'c-black' },
      { id: 'ct6', label: 'NON RESPONSIVE CALLS', value: null, variant: 'c-black' }
    ])

    // Filters
    const filters = ref([
      { id: 'all', label: 'All' },
      { id: 'missed', label: 'Missed Call' },
      { id: 'on_call', label: 'On Call' },
      { id: 'in_queue', label: 'In Queue' },
      { id: 'available', label: 'Available' },
      { id: 'ringing', label: 'Ringing' }
    ])
    const activeFilter = ref('all')

    const matchesFilter = (c) => {
      const status = (c.queueStatus || '').toString().toLowerCase()
      switch (activeFilter.value) {
        case 'missed':
          return parseInt(c.missed || '0', 10) > 0
        case 'on_call':
          return status.includes('on call')
        case 'in_queue':
          return status.includes('queue')
        case 'available':
          return status.includes('avail')
        case 'ringing':
          return status.includes('ring')
        default:
          return true
      }
    }

    // Computed properties for filtered data
    const filteredCounsellors = computed(() => {
      return counsellors.value.filter(matchesFilter)
    })

    // Methods
    const handleSearch = () => {}

    const setActiveFilter = (id) => {
      activeFilter.value = id
    }

    const statusClass = (status) => {
      const s = (status || 'Available').toString().toLowerCase()
      if (s.includes('on call')) return 'status-oncall'
      if (s.includes('ring')) return 'status-ringing'
      if (s.includes('queue')) return 'status-inqueue'
      if (s.includes('avail')) return 'status-available'
      return 'status-neutral'
    }

    return {
      counsellors,
      stats,
      filters,
      activeFilter,
      casesTiles,
      filteredCounsellors,
      handleSearch,
      setActiveFilter,
      statusClass
    }
  }
}
</script>
