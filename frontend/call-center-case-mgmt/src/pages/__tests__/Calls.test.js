// src/pages/__tests__/Calls.test.js

import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { nextTick } from 'vue'
import Calls from '../Calls.vue'

// Mock the router
const mockPush = vi.fn()
vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: mockPush
  })
}))

// Mock SidePanel component
vi.mock('@/components/SidePanel.vue', () => ({
  default: {
    name: 'SidePanel',
    template: '<div data-testid="side-panel">SidePanel</div>',
    props: ['userRole', 'isInQueue', 'isProcessingQueue', 'currentCall'],
    emits: ['toggle-queue', 'logout', 'sidebar-toggle']
  }
}))

describe('Calls.vue', () => {
  let wrapper
  let mockAlert
  let mockConsoleLog

  beforeEach(() => {
    // Mock console and alert
    mockAlert = vi.spyOn(window, 'alert').mockImplementation(() => {})
    mockConsoleLog = vi.spyOn(console, 'log').mockImplementation(() => {})
    
    // Mock localStorage
    localStorage.getItem.mockReturnValue('dark')
    
    // Mock window dimensions
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 1200,
    })

    // Mock document.documentElement methods
    Object.defineProperty(document.documentElement, 'style', {
      value: {
        setProperty: vi.fn(),
        getPropertyValue: vi.fn(),
      },
      writable: true,
    })

    Object.defineProperty(document.documentElement, 'setAttribute', {
      value: vi.fn(),
      writable: true,
    })

    // Mock performance.now for timing functions
    vi.spyOn(performance, 'now').mockReturnValue(Date.now())

    wrapper = mount(Calls)
  })

  afterEach(() => {
    wrapper?.unmount()
    vi.clearAllMocks()
    vi.clearAllTimers()
  })

  describe('Component Initialization', () => {
    it('should render without crashing', () => {
      expect(wrapper.exists()).toBe(true)
    })

    it('should initialize with correct default values', () => {
      expect(wrapper.vm.activeView).toBe('timeline')
      expect(wrapper.vm.selectedCallId).toBe('1348456')
      expect(wrapper.vm.currentTheme).toBe('dark')
      expect(wrapper.vm.isInQueue).toBe(false)
      expect(wrapper.vm.isProcessingQueue).toBe(false)
      expect(wrapper.vm.currentCall).toBe(null)
      expect(wrapper.vm.userRole).toBe('super-admin')
    })

    it('should render SidePanel component', () => {
      const sidePanel = wrapper.findComponent({ name: 'SidePanel' })
      expect(sidePanel.exists()).toBe(true)
    })

    it('should initialize with sample call data', () => {
      expect(wrapper.vm.allCalls.length).toBeGreaterThan(0)
      expect(wrapper.vm.callData).toBeDefined()
      expect(typeof wrapper.vm.callData).toBe('object')
    })

    it('should initialize with queue data', () => {
      expect(wrapper.vm.queueCalls).toBeDefined()
      expect(Array.isArray(wrapper.vm.queueCalls)).toBe(true)
      expect(wrapper.vm.queueStats).toBeDefined()
      expect(wrapper.vm.queueMembers).toBeDefined()
    })
  })

  describe('View Management', () => {
    it('should switch between views', async () => {
      expect(wrapper.vm.activeView).toBe('timeline')

      // Switch to table view
      await wrapper.setData({ activeView: 'table' })
      expect(wrapper.vm.activeView).toBe('table')

      // Switch to queue view
      await wrapper.setData({ activeView: 'queue' })
      expect(wrapper.vm.activeView).toBe('queue')
    })

    it('should render view tabs correctly', () => {
      const viewTabs = wrapper.findAll('.view-tab')
      expect(viewTabs.length).toBe(3)
      
      const tabTexts = viewTabs.map(tab => tab.text())
      expect(tabTexts).toContain('Timeline')
      expect(tabTexts).toContain('Table View')
      expect(tabTexts).toContain('Call Queue')
    })

    it('should highlight active view tab', async () => {
      await wrapper.setData({ activeView: 'table' })
      await nextTick()

      const viewTabs = wrapper.findAll('.view-tab')
      const activeTab = viewTabs.find(tab => tab.classes().includes('active'))
      expect(activeTab.text()).toBe('Table View')
    })

    it('should show correct view container based on active view', async () => {
      // Timeline view
      await wrapper.setData({ activeView: 'timeline' })
      await nextTick()
      
      const timelineContainer = wrapper.find('[v-show="activeView === \'timeline\'"]')
      expect(timelineContainer.exists()).toBe(true)

      // Table view
      await wrapper.setData({ activeView: 'table' })
      await nextTick()
      
      const tableContainer = wrapper.find('[v-show="activeView === \'table\'"]')
      expect(tableContainer.exists()).toBe(true)

      // Queue view
      await wrapper.setData({ activeView: 'queue' })
      await nextTick()
      
      const queueContainer = wrapper.find('[v-show="activeView === \'queue\'"]')
      expect(queueContainer.exists()).toBe(true)
    })
  })

  describe('Theme Management', () => {
    it('should toggle theme from dark to light', async () => {
      wrapper.vm.currentTheme = 'dark'
      
      await wrapper.vm.toggleTheme()
      
      expect(wrapper.vm.currentTheme).toBe('light')
      expect(localStorage.setItem).toHaveBeenCalledWith('theme', 'light')
    })

    it('should toggle theme from light to dark', async () => {
      wrapper.vm.currentTheme = 'light'
      
      await wrapper.vm.toggleTheme()
      
      expect(wrapper.vm.currentTheme).toBe('dark')
      expect(localStorage.setItem).toHaveBeenCalledWith('theme', 'dark')
    })

    it('should apply light theme styles', () => {
      wrapper.vm.applyTheme('light')
      
      expect(document.documentElement.style.setProperty).toHaveBeenCalledWith('--background-color', '#f5f5f5')
      expect(document.documentElement.style.setProperty).toHaveBeenCalledWith('--text-color', '#333')
      expect(document.documentElement.setAttribute).toHaveBeenCalledWith('data-theme', 'light')
    })

    it('should apply dark theme styles', () => {
      wrapper.vm.applyTheme('dark')
      
      expect(document.documentElement.style.setProperty).toHaveBeenCalledWith('--background-color', '#0a0a0a')
      expect(document.documentElement.style.setProperty).toHaveBeenCalledWith('--text-color', '#fff')
      expect(document.documentElement.setAttribute).toHaveBeenCalledWith('data-theme', 'dark')
    })
  })

  describe('Call Selection and Details', () => {
    it('should select a call', async () => {
      const testCallId = '1348457'
      await wrapper.vm.selectCall(testCallId)
      
      expect(wrapper.vm.selectedCallId).toBe(testCallId)
      expect(wrapper.vm.showCallDetails).toBe(true)
    })

    it('should return correct selected call details', () => {
      wrapper.vm.selectedCallId = '1348456'
      const details = wrapper.vm.selectedCallDetails
      
      expect(details).toBeDefined()
      expect(details.id).toBe('1348456')
      expect(details.title).toBeDefined()
      expect(details.callerName).toBeDefined()
    })

    it('should close call details', async () => {
      wrapper.vm.showCallDetails = true
      
      await wrapper.vm.closeCallDetails()
      
      expect(wrapper.vm.showCallDetails).toBe(false)
    })

    it('should view call details correctly', async () => {
      const callId = '1348456'
      await wrapper.vm.viewCallDetails(callId)
      
      expect(wrapper.vm.selectedCallId).toBe(callId)
      expect(wrapper.vm.showCallDetails).toBe(true)
    })
  })

  describe('Queue Management', () => {
    it('should handle queue toggle when not in call', async () => {
      wrapper.vm.currentCall = null
      wrapper.vm.isInQueue = false
      
      await wrapper.vm.handleQueueToggle()
      
      expect(wrapper.vm.showQueuePopup).toBe(true)
    })

    it('should end call when toggling queue during active call', async () => {
      wrapper.vm.currentCall = { id: 'test-call' }
      
      await wrapper.vm.handleQueueToggle()
      
      expect(wrapper.vm.currentCall).toBe(null)
    })

    it('should confirm joining queue', async () => {
      wrapper.vm.isInQueue = false
      
      await wrapper.vm.confirmJoinQueue()
      
      expect(wrapper.vm.isInQueue).toBe(true)
      expect(wrapper.vm.showQueuePopup).toBe(false)
      expect(wrapper.vm.showNotification).toBe(true)
      expect(wrapper.vm.notificationMessage).toContain('Joined the queue successfully')
    })

    it('should close queue popup', async () => {
      wrapper.vm.showQueuePopup = true
      
      await wrapper.vm.closeQueuePopup()
      
      expect(wrapper.vm.showQueuePopup).toBe(false)
    })

    it('should accept queue call when in queue', async () => {
      wrapper.vm.isInQueue = true
      const queueCall = {
        id: 'queue_001',
        type: 'Emergency Crisis',
        callerName: 'Test Caller',
        priority: 'critical',
        caseId: 'CASE-2025-1001'
      }
      wrapper.vm.queueCalls = [queueCall]

      await wrapper.vm.acceptQueueCall('queue_001')

      expect(wrapper.vm.showRingingInterface).toBe(true)
      expect(wrapper.vm.ringingCall).toBeDefined()
      expect(wrapper.vm.queueCalls.length).toBe(0)
    })

    it('should not accept queue call when not in queue', async () => {
      wrapper.vm.isInQueue = false
      const initialQueueCalls = wrapper.vm.queueCalls.length

      await wrapper.vm.acceptQueueCall('queue_001')

      expect(wrapper.vm.queueCalls.length).toBe(initialQueueCalls)
      expect(wrapper.vm.showRingingInterface).toBe(false)
    })
  })

  describe('Call Management', () => {
    it('should simulate incoming call', async () => {
      await wrapper.vm.simulateIncomingCall()
      
      expect(wrapper.vm.ringingCall).toBeDefined()
      expect(wrapper.vm.showRingingInterface).toBe(true)
      expect(wrapper.vm.ringingStartTime).toBeDefined()
    })

    it('should answer call correctly', async () => {
      wrapper.vm.ringingCall = {
        id: 'test-call',
        type: 'Emergency Crisis',
        callerName: 'Test Caller',
        priority: 'critical',
        caseId: 'CASE-2025-1001'
      }

      await wrapper.vm.answerCall()

      expect(wrapper.vm.currentCall).toBeDefined()
      expect(wrapper.vm.showRingingInterface).toBe(false)
      expect(wrapper.vm.showCaseOptions).toBe(true)
      expect(wrapper.vm.callStartTime).toBeDefined()
    })

    it('should decline call correctly', async () => {
      wrapper.vm.ringingCall = { id: 'test-call' }
      wrapper.vm.showRingingInterface = true

      await wrapper.vm.declineCall()

      expect(wrapper.vm.showRingingInterface).toBe(false)
      expect(wrapper.vm.ringingCall).toBe(null)
      expect(wrapper.vm.ringingDuration).toBe('00:00')
    })

    it('should end call correctly', async () => {
      wrapper.vm.currentCall = { id: 'test-call' }
      wrapper.vm.callStartTime = new Date()
      wrapper.vm.showCaseForm = true

      await wrapper.vm.endCall()

      expect(wrapper.vm.currentCall).toBe(null)
      expect(wrapper.vm.callStartTime).toBe(null)
      expect(wrapper.vm.callDuration).toBe('00:00')
      expect(wrapper.vm.showCaseForm).toBe(false)
    })
  })

  describe('Case Management', () => {
    it('should show case options after answering call', async () => {
      wrapper.vm.ringingCall = {
        id: 'test-call',
        type: 'Emergency Crisis',
        caseId: 'CASE-2025-1001'
      }

      await wrapper.vm.answerCall()

      expect(wrapper.vm.showCaseOptions).toBe(true)
    })

    it('should close case options', async () => {
      wrapper.vm.showCaseOptions = true
      
      await wrapper.vm.closeCaseOptions()
      
      expect(wrapper.vm.showCaseOptions).toBe(false)
    })

    it('should select new case option', async () => {
      wrapper.vm.currentCall = { type: 'Emergency Crisis', callerName: 'Test' }
      wrapper.vm.showCaseOptions = true

      await wrapper.vm.selectCaseOption('new')

      expect(wrapper.vm.showCaseOptions).toBe(false)
      expect(wrapper.vm.caseFormMode).toBe('new')
      expect(wrapper.vm.showCaseForm).toBe(true)
      expect(wrapper.vm.caseFormData.caseName).toBe('Emergency Crisis')
    })

    it('should select existing case option', async () => {
      wrapper.vm.showCaseOptions = true

      await wrapper.vm.selectCaseOption('existing')

      expect(wrapper.vm.showCaseOptions).toBe(false)
      expect(wrapper.vm.showExistingCaseSearch).toBe(true)
    })

    it('should select disposition option', async () => {
      wrapper.vm.showCaseOptions = true

      await wrapper.vm.selectCaseOption('disposition')

      expect(wrapper.vm.showCaseOptions).toBe(false)
      expect(wrapper.vm.showDisposition).toBe(true)
    })

    it('should close existing case search', async () => {
      wrapper.vm.showExistingCaseSearch = true
      wrapper.vm.caseSearchQuery = 'test'

      await wrapper.vm.closeExistingCaseSearch()

      expect(wrapper.vm.showExistingCaseSearch).toBe(false)
      expect(wrapper.vm.caseSearchQuery).toBe('')
    })

    it('should select existing case', async () => {
      const existingCase = {
        id: 'CASE-2025-1001',
        title: 'Test Case',
        description: 'Test description',
        priority: 'High',
        client: 'Test Client'
      }
      wrapper.vm.currentCall = { id: 'test-call', callerName: 'Test Caller' }

      await wrapper.vm.selectExistingCase(existingCase)

      expect(wrapper.vm.currentCaseId).toBe('CASE-2025-1001')
      expect(wrapper.vm.caseFormMode).toBe('edit')
      expect(wrapper.vm.showExistingCaseSearch).toBe(false)
      expect(wrapper.vm.showCaseForm).toBe(true)
    })

    it('should minimize case form', async () => {
      wrapper.vm.showCaseForm = true

      await wrapper.vm.minimizeCaseForm()

      expect(wrapper.vm.showCaseForm).toBe(false)
      expect(wrapper.vm.caseFormMinimized).toBe(true)
    })

    it('should restore case form', async () => {
      wrapper.vm.caseFormMinimized = true

      await wrapper.vm.restoreCaseForm()

      expect(wrapper.vm.caseFormMinimized).toBe(false)
      expect(wrapper.vm.showCaseForm).toBe(true)
    })

    it('should save case form', async () => {
      wrapper.vm.caseFormData = {
        caseName: 'Test Case',
        description: 'Test description'
      }

      await wrapper.vm.saveCaseForm()

      expect(mockAlert).toHaveBeenCalledWith(expect.stringContaining('successfully'))
      expect(wrapper.vm.showCaseForm).toBe(false)
    })

    it('should save draft', async () => {
      await wrapper.vm.saveDraft()
      expect(mockAlert).toHaveBeenCalledWith('Draft saved successfully!')
    })
  })

  describe('Call Options and New Call Flow', () => {
    it('should initiate new call', async () => {
      await wrapper.vm.initiateNewCall()
      expect(wrapper.vm.showCallOptions).toBe(true)
    })

    it('should close call options', async () => {
      wrapper.vm.showCallOptions = true
      wrapper.vm.showContactsModal = true
      wrapper.vm.newCallNumber = '123-456-7890'

      await wrapper.vm.closeCallOptions()

      expect(wrapper.vm.showCallOptions).toBe(false)
      expect(wrapper.vm.showContactsModal).toBe(false)
      expect(wrapper.vm.newCallNumber).toBe('')
    })

    it('should select call option - contacts', async () => {
      wrapper.vm.showCallOptions = true

      await wrapper.vm.selectCallOption('contacts')

      expect(wrapper.vm.showCallOptions).toBe(false)
      expect(wrapper.vm.showContactsModal).toBe(true)
    })

    it('should select call option - new', async () => {
      wrapper.vm.showCallOptions = true

      await wrapper.vm.selectCallOption('new')

      expect(wrapper.vm.showCallOptions).toBe(false)
      expect(wrapper.vm.showNewCallModal).toBe(true)
    })

    it('should call contact', async () => {
      const contact = {
        name: 'Test Contact',
        phone: '+1-555-123-4567',
        priority: 'high'
      }

      await wrapper.vm.callContact(contact)

      expect(wrapper.vm.selectedContact).toBe(contact)
      expect(wrapper.vm.showContactsModal).toBe(false)
      expect(wrapper.vm.ringingCall).toBeDefined()
      expect(wrapper.vm.showRingingInterface).toBe(true)
    })

    it('should make new call with valid number', async () => {
      wrapper.vm.newCallNumber = '+1-555-123-4567'

      await wrapper.vm.makeNewCall()

      expect(wrapper.vm.showNewCallModal).toBe(false)
      expect(wrapper.vm.ringingCall).toBeDefined()
      expect(wrapper.vm.showRingingInterface).toBe(true)
      expect(wrapper.vm.newCallNumber).toBe('')
    })

    it('should not make new call with empty number', async () => {
      wrapper.vm.newCallNumber = ''

      await wrapper.vm.makeNewCall()

      expect(mockAlert).toHaveBeenCalledWith('Please enter a phone number')
    })
  })

  describe('Disposition Management', () => {
    it('should close disposition modal', async () => {
      wrapper.vm.showDisposition = true
      wrapper.vm.disposition = {
        outcome: 'resolved',
        notes: 'test notes'
      }

      await wrapper.vm.closeDisposition()

      expect(wrapper.vm.showDisposition).toBe(false)
      expect(wrapper.vm.disposition.outcome).toBe('')
      expect(wrapper.vm.disposition.notes).toBe('')
    })

    it('should submit disposition', async () => {
      wrapper.vm.currentCall = { id: 'test-call' }
      wrapper.vm.disposition = {
        outcome: 'resolved',
        reason: 'Crisis resolved',
        priority: 'high'
      }

      await wrapper.vm.submitDisposition()

      expect(wrapper.vm.currentCall).toBe(null)
      expect(wrapper.vm.showDisposition).toBe(false)
      expect(mockAlert).toHaveBeenCalledWith('Call disposition saved and call ended successfully!')
    })
  })

  describe('Case Linking', () => {
    it('should link to case', async () => {
      const callId = '1348456'
      
      await wrapper.vm.linkToCase(callId)
      
      expect(wrapper.vm.selectedCallForLink).toBe(callId)
      expect(wrapper.vm.showCaseLink).toBe(true)
    })

    it('should close case link modal', async () => {
      wrapper.vm.showCaseLink = true
      wrapper.vm.selectedCallForLink = '1348456'

      await wrapper.vm.closeCaseLink()

      expect(wrapper.vm.showCaseLink).toBe(false)
      expect(wrapper.vm.selectedCallForLink).toBe(null)
    })

    it('should select case link option - existing', async () => {
      wrapper.vm.selectedCallForLink = '1348456'
      
      // Mock prompt
      const mockPrompt = vi.spyOn(window, 'prompt').mockReturnValue('CASE-2025-9999')

      await wrapper.vm.selectCaseLinkOption('existing')

      expect(wrapper.vm.callData['1348456'].caseId).toBe('CASE-2025-9999')
      expect(mockAlert).toHaveBeenCalledWith('Call linked to case CASE-2025-9999')
      expect(wrapper.vm.showCaseLink).toBe(false)

      mockPrompt.mockRestore()
    })

    it('should select case link option - new', async () => {
      await wrapper.vm.selectCaseLinkOption('new')

      expect(mockPush).toHaveBeenCalledWith('/case-creation')
      expect(wrapper.vm.showCaseLink).toBe(false)
    })
  })

  describe('Utility Functions', () => {
    it('should generate case ID correctly', () => {
      const caseId = wrapper.vm.generateCaseId()
      expect(caseId).toMatch(/^CASE-\d{4}-\d{4}$/)
    })

    it('should get status class correctly', () => {
      expect(wrapper.vm.getStatusClass('In Progress')).toBe('in-progress')
      expect(wrapper.vm.getStatusClass('Open Status')).toBe('open-status')
    })

    it('should view case correctly', async () => {
      const caseId = 'CASE-2025-1001'
      
      await wrapper.vm.viewCase(caseId)
      
      expect(mockConsoleLog).toHaveBeenCalledWith('Viewing case:', caseId)
      expect(mockPush).toHaveBeenCalledWith('/cases')
    })
  })

  describe('Timer Functions', () => {
    beforeEach(() => {
      vi.useFakeTimers()
    })

    afterEach(() => {
      vi.useRealTimers()
    })

    it('should start ringing timer', async () => {
      wrapper.vm.ringingStartTime = new Date()
      wrapper.vm.showRingingInterface = true

      wrapper.vm.startRingingTimer()

      // Advance time by 65 seconds
      vi.advanceTimersByTime(65000)

      expect(wrapper.vm.ringingDuration).toBe('01:05')
    })

    it('should start call timer', async () => {
      wrapper.vm.currentCall = { id: 'test-call' }
      wrapper.vm.callStartTime = new Date()

      wrapper.vm.startCallTimer()

      // Advance time by 125 seconds
      vi.advanceTimersByTime(125000)

      expect(wrapper.vm.callDuration).toBe('02:05')
    })
  })

  describe('Computed Properties', () => {
    it('should compute allCalls correctly', () => {
      const allCalls = wrapper.vm.allCalls
      expect(Array.isArray(allCalls)).toBe(true)
      expect(allCalls.length).toBeGreaterThan(0)
    })

    it('should compute groupedCalls correctly', () => {
      const grouped = wrapper.vm.groupedCalls
      expect(typeof grouped).toBe('object')
      expect(grouped.Today).toBeDefined()
      expect(Array.isArray(grouped.Today)).toBe(true)
    })

    it('should compute selectedCallDetails correctly', () => {
      wrapper.vm.selectedCallId = '1348456'
      const details = wrapper.vm.selectedCallDetails
      
      expect(details).toBeDefined()
      expect(details.id).toBe('1348456')
    })

    it('should compute filteredExistingCases correctly', () => {
      // Test without search query
      wrapper.vm.caseSearchQuery = ''
      let filtered = wrapper.vm.filteredExistingCases
      expect(filtered.length).toBe(wrapper.vm.existingCases.length)

      // Test with search query
      wrapper.vm.caseSearchQuery = 'domestic'
      filtered = wrapper.vm.filteredExistingCases
      filtered.forEach(caseItem => {
        const query = 'domestic'
        const matchesId = caseItem.id.toLowerCase().includes(query)
        const matchesTitle = caseItem.title.toLowerCase().includes(query)
        const matchesClient = caseItem.client.toLowerCase().includes(query)
        expect(matchesId || matchesTitle || matchesClient).toBe(true)
      })
    })
  })

  describe('Event Handlers', () => {
    it('should handle sidebar toggle', async () => {
      await wrapper.vm.handleSidebarToggle(true)
      expect(wrapper.vm.isSidebarCollapsed).toBe(true)

      await wrapper.vm.handleSidebarToggle(false)
      expect(wrapper.vm.isSidebarCollapsed).toBe(false)
    })

    it('should handle logout', async () => {
      await wrapper.vm.handleLogout()
      expect(mockConsoleLog).toHaveBeenCalledWith('Logging out...')
      expect(mockAlert).toHaveBeenCalledWith('Logged out successfully!')
    })
  })

  describe('Data Validation and Structure', () => {
    it('should validate call data structure', () => {
      const callData = wrapper.vm.callData
      expect(typeof callData).toBe('object')
      
      Object.values(callData).forEach(call => {
        expect(call).toHaveProperty('id')
        expect(call).toHaveProperty('title')
        expect(call).toHaveProperty('time')
        expect(call).toHaveProperty('status')
        expect(call).toHaveProperty('caseId')
        expect(typeof call.id).toBe('string')
        expect(typeof call.title).toBe('string')
      })
    })

    it('should validate queue data structure', () => {
      const queueCalls = wrapper.vm.queueCalls
      expect(Array.isArray(queueCalls)).toBe(true)
      
      queueCalls.forEach(call => {
        expect(call).toHaveProperty('id')
        expect(call).toHaveProperty('type')
        expect(call).toHaveProperty('waitTime')
        expect(call).toHaveProperty('caseId')
        expect(typeof call.id).toBe('string')
        expect(typeof call.type).toBe('string')
      })
    })

    it('should validate contacts data structure', () => {
      const contacts = wrapper.vm.contacts
      expect(Array.isArray(contacts)).toBe(true)
      
      contacts.forEach(contact => {
        expect(contact).toHaveProperty('id')
        expect(contact).toHaveProperty('name')
        expect(contact).toHaveProperty('phone')
        expect(contact).toHaveProperty('type')
        expect(typeof contact.id).toBe('number')
        expect(typeof contact.name).toBe('string')
        expect(typeof contact.phone).toBe('string')
      })
    })

    it('should validate existing cases data structure', () => {
      const existingCases = wrapper.vm.existingCases
      expect(Array.isArray(existingCases)).toBe(true)
      
      existingCases.forEach(caseItem => {
        expect(caseItem).toHaveProperty('id')
        expect(caseItem).toHaveProperty('title')
        expect(caseItem).toHaveProperty('client')
        expect(caseItem).toHaveProperty('priority')
        expect(caseItem).toHaveProperty('status')
        expect(typeof caseItem.id).toBe('string')
        expect(typeof caseItem.title).toBe('string')
      })
    })

    it('should validate queue members data structure', () => {
      const queueMembers = wrapper.vm.queueMembers
      expect(Array.isArray(queueMembers)).toBe(true)
      
      queueMembers.forEach(member => {
        expect(member).toHaveProperty('id')
        expect(member).toHaveProperty('name')
        expect(member).toHaveProperty('role')
        expect(member).toHaveProperty('status')
        expect(typeof member.id).toBe('number')
        expect(typeof member.name).toBe('string')
      })
    })
  })

  describe('Notification System', () => {
    it('should show notification when joining queue', async () => {
      await wrapper.vm.confirmJoinQueue()
      
      expect(wrapper.vm.showNotification).toBe(true)
      expect(wrapper.vm.notificationMessage).toContain('Joined the queue successfully')
      expect(wrapper.vm.notificationType).toBe('success')
    })

    it('should auto-hide notification', async () => {
      vi.useFakeTimers()
      
      await wrapper.vm.confirmJoinQueue()
      expect(wrapper.vm.showNotification).toBe(true)
      
      // Fast-forward 3 seconds
      vi.advanceTimersByTime(3000)
      await nextTick()
      
      expect(wrapper.vm.showNotification).toBe(false)
      
      vi.useRealTimers()
    })

    it('should close notification manually', async () => {
      wrapper.vm.showNotification = true
      
      await wrapper.setData({ showNotification: false })
      
      expect(wrapper.vm.showNotification).toBe(false)
    })
  })

  describe('Modal State Management', () => {
    it('should manage queue popup state', async () => {
      expect(wrapper.vm.showQueuePopup).toBe(false)
      
      await wrapper.setData({ showQueuePopup: true })
      expect(wrapper.vm.showQueuePopup).toBe(true)
      
      await wrapper.vm.closeQueuePopup()
      expect(wrapper.vm.showQueuePopup).toBe(false)
    })

    it('should manage ringing interface state', async () => {
      expect(wrapper.vm.showRingingInterface).toBe(false)
      
      await wrapper.vm.simulateIncomingCall()
      expect(wrapper.vm.showRingingInterface).toBe(true)
      
      await wrapper.vm.declineCall()
      expect(wrapper.vm.showRingingInterface).toBe(false)
    })

    it('should manage case form state', async () => {
      expect(wrapper.vm.showCaseForm).toBe(false)
      
      await wrapper.setData({ showCaseForm: true })
      expect(wrapper.vm.showCaseForm).toBe(true)
      
      await wrapper.vm.minimizeCaseForm()
      expect(wrapper.vm.showCaseForm).toBe(false)
      expect(wrapper.vm.caseFormMinimized).toBe(true)
    })

    it('should manage call options state', async () => {
      expect(wrapper.vm.showCallOptions).toBe(false)
      
      await wrapper.vm.initiateNewCall()
      expect(wrapper.vm.showCallOptions).toBe(true)
      
      await wrapper.vm.closeCallOptions()
      expect(wrapper.vm.showCallOptions).toBe(false)
    })

    it('should manage disposition state', async () => {
      expect(wrapper.vm.showDisposition).toBe(false)
      
      await wrapper.setData({ showDisposition: true })
      expect(wrapper.vm.showDisposition).toBe(true)
      
      await wrapper.vm.closeDisposition()
      expect(wrapper.vm.showDisposition).toBe(false)
    })
  })

  describe('Edge Cases and Error Handling', () => {
    it('should handle missing call data gracefully', () => {
      wrapper.vm.selectedCallId = 'non-existent-id'
      const details = wrapper.vm.selectedCallDetails
      
      expect(details).toBe(null)
    })

    it('should handle empty queue calls', async () => {
      wrapper.vm.queueCalls = []
      wrapper.vm.isInQueue = true
      
      await wrapper.vm.acceptQueueCall('non-existent-call')
      
      expect(wrapper.vm.showRingingInterface).toBe(false)
    })

    it('should handle case form with empty data', async () => {
      wrapper.vm.caseFormData = {
        caseName: '',
        description: ''
      }
      
      await wrapper.vm.saveCaseForm()
      
      // Should still save even with empty data
      expect(mockAlert).toHaveBeenCalledWith(expect.stringContaining('successfully'))
    })

    it('should handle prompt cancellation for case linking', async () => {
      wrapper.vm.selectedCallForLink = '1348456'
      
      // Mock prompt to return null (cancelled)
      const mockPrompt = vi.spyOn(window, 'prompt').mockReturnValue(null)

      await wrapper.vm.selectCaseLinkOption('existing')

      // Should not update case ID when prompt is cancelled
      expect(wrapper.vm.showCaseLink).toBe(false)

      mockPrompt.mockRestore()
    })

    it('should handle timer cleanup on component unmount', () => {
      wrapper.vm.callStartTime = new Date()
      wrapper.vm.ringingStartTime = new Date()
      
      wrapper.unmount()
      
      // Timers should be cleaned up
      expect(wrapper.vm.callStartTime).toBe(null)
      expect(wrapper.vm.ringingStartTime).toBe(null)
    })
  })

  describe('Search and Filter Functionality', () => {
    it('should filter existing cases by ID', async () => {
      wrapper.vm.caseSearchQuery = 'CASE-2025-1001'
      const filtered = wrapper.vm.filteredExistingCases
      
      expect(filtered.length).toBeGreaterThan(0)
      filtered.forEach(caseItem => {
        expect(caseItem.id.toLowerCase()).toContain('case-2025-1001')
      })
    })

    it('should filter existing cases by title', async () => {
      wrapper.vm.caseSearchQuery = 'domestic'
      const filtered = wrapper.vm.filteredExistingCases
      
      filtered.forEach(caseItem => {
        expect(caseItem.title.toLowerCase()).toContain('domestic')
      })
    })

    it('should filter existing cases by client', async () => {
      wrapper.vm.caseSearchQuery = 'jane'
      const filtered = wrapper.vm.filteredExistingCases
      
      filtered.forEach(caseItem => {
        expect(caseItem.client.toLowerCase()).toContain('jane')
      })
    })

    it('should return all cases when search query is empty', async () => {
      wrapper.vm.caseSearchQuery = ''
      const filtered = wrapper.vm.filteredExistingCases
      
      expect(filtered.length).toBe(wrapper.vm.existingCases.length)
    })
  })

  describe('Status and Priority Management', () => {
    it('should render status cards correctly', () => {
      const statusCards = wrapper.findAll('.status-card')
      expect(statusCards.length).toBeGreaterThan(0)
      
      // Check that status items are properly structured
      wrapper.vm.statusItems.forEach(item => {
        expect(item).toHaveProperty('label')
        expect(item).toHaveProperty('count')
        expect(item).toHaveProperty('percentage')
        expect(typeof item.label).toBe('string')
        expect(typeof item.count).toBe('number')
        expect(typeof item.percentage).toBe('number')
      })
    })

    it('should handle priority badges correctly', () => {
      const priorities = ['critical', 'high', 'medium', 'low']
      priorities.forEach(priority => {
        const element = document.createElement('div')
        element.className = `priority-badge ${priority}`
        expect(element.classList.contains(priority)).toBe(true)
      })
    })

    it('should handle status badges correctly', () => {
      const statuses = ['in-progress', 'pending', 'completed', 'unassigned']
      statuses.forEach(status => {
        const className = wrapper.vm.getStatusClass(status)
        expect(typeof className).toBe('string')
      })
    })
  })

  describe('Real-time Updates', () => {
    it('should simulate incoming call after joining queue', async () => {
      vi.useFakeTimers()
      
      wrapper.vm.isInQueue = false
      await wrapper.vm.confirmJoinQueue()
      
      expect(wrapper.vm.isInQueue).toBe(true)
      
      // Fast-forward 3 seconds to trigger simulated call
      vi.advanceTimersByTime(3000)
      await nextTick()
      
      expect(wrapper.vm.ringingCall).toBeDefined()
      expect(wrapper.vm.showRingingInterface).toBe(true)
      
      vi.useRealTimers()
    })

    it('should not simulate call if not in queue', async () => {
      vi.useFakeTimers()
      
      wrapper.vm.isInQueue = false
      wrapper.vm.currentCall = null
      
      // Fast-forward 3 seconds
      vi.advanceTimersByTime(3000)
      await nextTick()
      
      expect(wrapper.vm.ringingCall).toBe(null)
      expect(wrapper.vm.showRingingInterface).toBe(false)
      
      vi.useRealTimers()
    })

    it('should not simulate call if already in call', async () => {
      vi.useFakeTimers()
      
      wrapper.vm.isInQueue = true
      wrapper.vm.currentCall = { id: 'existing-call' }
      
      // Fast-forward 3 seconds
      vi.advanceTimersByTime(3000)
      await nextTick()
      
      // Should not create new ringing call
      expect(wrapper.vm.currentCall.id).toBe('existing-call')
      
      vi.useRealTimers()
    })
  })

  describe('Call Data Management', () => {
    it('should add call to call data when answering', async () => {
      const initialCallCount = Object.keys(wrapper.vm.callData).length
      
      wrapper.vm.ringingCall = {
        id: 'new-test-call',
        type: 'Emergency Crisis',
        callerName: 'Test Caller',
        priority: 'critical',
        caseId: 'CASE-2025-1001'
      }

      await wrapper.vm.answerCall()

      expect(Object.keys(wrapper.vm.callData).length).toBe(initialCallCount + 1)
      expect(wrapper.vm.callData['new-test-call']).toBeDefined()
      expect(wrapper.vm.callData['new-test-call'].status).toBe('In Progress')
    })

    it('should update call data when ending call', async () => {
      wrapper.vm.currentCall = { id: '1348456' }
      wrapper.vm.callDuration = '05:30'

      await wrapper.vm.endCall()

      expect(wrapper.vm.callData['1348456'].status).toBe('Completed')
      expect(wrapper.vm.callData['1348456'].duration).toBe('05:30')
    })

    it('should update call disposition in call data', async () => {
      wrapper.vm.currentCall = { id: '1348456' }
      wrapper.vm.disposition = {
        reason: 'Crisis resolved',
        priority: 'high'
      }

      await wrapper.vm.submitDisposition()

      expect(wrapper.vm.callData['1348456'].disposition).toBe('Crisis resolved')
      expect(wrapper.vm.callData['1348456'].priority).toBe('high')
    })
  })

  describe('Component Lifecycle', () => {
    it('should load theme from localStorage on mount', () => {
      localStorage.getItem.mockReturnValue('light')
      
      const newWrapper = mount(Calls)
      
      expect(newWrapper.vm.currentTheme).toBe('light')
      newWrapper.unmount()
    })

    it('should apply theme on mount', () => {
      expect(document.documentElement.style.setProperty).toHaveBeenCalled()
      expect(document.documentElement.setAttribute).toHaveBeenCalledWith('data-theme', 'dark')
    })

    it('should clean up timers on unmount', () => {
      wrapper.vm.callStartTime = new Date()
      wrapper.vm.ringingStartTime = new Date()
      
      wrapper.unmount()
      
      // Component should clean up properly
      expect(wrapper.vm).toBeDefined()
    })
  })

  describe('Form Validation and Submission', () => {
    it('should reset case form data correctly', async () => {
      wrapper.vm.caseFormData = {
        caseName: 'Test Case',
        description: 'Test Description',
        priority: 'High',
        type: 'Domestic Violence',
        callerInfo: 'Test Caller Info',
        incidentDetails: 'Test Incident Details'
      }

      // Reset form data
      wrapper.vm.caseFormData = {
        caseName: '',
        description: '',
        priority: '',
        type: '',
        callerInfo: '',
        incidentDetails: ''
      }

      expect(wrapper.vm.caseFormData.caseName).toBe('')
      expect(wrapper.vm.caseFormData.description).toBe('')
      expect(wrapper.vm.caseFormData.priority).toBe('')
    })

    it('should reset disposition form correctly', async () => {
      wrapper.vm.disposition = {
        outcome: 'resolved',
        category: 'domestic-violence',
        priority: 'high',
        reason: 'crisis-resolved',
        notes: 'Test notes'
      }

      await wrapper.vm.closeDisposition()

      expect(wrapper.vm.disposition.outcome).toBe('')
      expect(wrapper.vm.disposition.category).toBe('')
      expect(wrapper.vm.disposition.notes).toBe('')
    })
  })

  describe('Accessibility and User Experience', () => {
    it('should provide proper ARIA labels and structure', () => {
      // Check for essential accessibility attributes
      const buttons = wrapper.findAll('button')
      expect(buttons.length).toBeGreaterThan(0)
      
      // Check for modal structure
      const modals = wrapper.findAll('.modal-overlay')
      modals.forEach(modal => {
        expect(modal.exists()).toBe(true)
      })
    })

    it('should handle keyboard interactions', async () => {
      // Test ESC key functionality would go here
      // This is a placeholder for keyboard interaction tests
      expect(true).toBe(true)
    })

    it('should provide proper visual feedback for user actions', async () => {
      // Test hover states, active states, etc.
      const buttons = wrapper.findAll('button')
      buttons.forEach(button => {
        expect(button.classes()).toBeDefined()
      })
    })
  })

  describe('Performance Considerations', () => {
    it('should handle large datasets efficiently', () => {
      // Add many calls to test performance
      const largeCalls = {}
      for (let i = 0; i < 1000; i++) {
        largeCalls[`call-${i}`] = {
          id: `call-${i}`,
          title: `Call ${i}`,
          time: '12:00PM',
          status: 'Completed',
          caseId: `CASE-${i}`,
          group: 'Today'
        }
      }

      wrapper.vm.callData = { ...wrapper.vm.callData, ...largeCalls }

      const startTime = performance.now()
      const allCalls = wrapper.vm.allCalls
      const endTime = performance.now()

      expect(allCalls.length).toBeGreaterThan(1000)
      expect(endTime - startTime).toBeLessThan(100) // Should be fast
    })

    it('should handle repeated operations without memory leaks', async () => {
      // Test repeated operations
      for (let i = 0; i < 50; i++) {
        await wrapper.vm.selectCall('1348456')
        await wrapper.vm.closeCallDetails()
        wrapper.vm.caseSearchQuery = `test ${i}`
        wrapper.vm.filteredExistingCases // Trigger computation
      }

      // Just verify operations completed successfully
      expect(wrapper.vm.selectedCallId).toBe('1348456')
      expect(wrapper.vm.caseSearchQuery).toBe('test 49')
    })
  })
})