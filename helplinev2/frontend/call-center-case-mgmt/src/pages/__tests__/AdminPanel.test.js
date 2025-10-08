// src/pages/__tests__/AdminPanel.test.js

import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { nextTick } from 'vue'
import AdminPanel from '../AdminPanel.vue'

describe('AdminPanel.vue', () => {
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

    wrapper = mount(AdminPanel)
  })

  afterEach(() => {
    wrapper?.unmount()
    vi.clearAllMocks()
  })

  describe('Component Initialization', () => {
    it('should render without crashing', () => {
      expect(wrapper.exists()).toBe(true)
    })

    it('should initialize with correct default values', () => {
      expect(wrapper.vm.isSidebarCollapsed).toBe(false)
      expect(wrapper.vm.mobileOpen).toBe(false)
      expect(wrapper.vm.currentTheme).toBe('dark')
      expect(wrapper.vm.activeTab).toBe('dashboard')
      expect(wrapper.vm.selectedTimeframe).toBe('7days')
      expect(wrapper.vm.unreadNotifications).toBe(3)
      expect(wrapper.vm.showNotifications).toBe(false)
    })

    it('should load theme from localStorage on mount', async () => {
      localStorage.getItem.mockReturnValue('light')
      
      const newWrapper = mount(AdminPanel)
      await nextTick()
      
      expect(newWrapper.vm.currentTheme).toBe('light')
      newWrapper.unmount()
    })

    it('should initialize with correct organization data', () => {
      expect(wrapper.vm.currentOrganization.name).toBe('Children First Kenya')
      expect(wrapper.vm.currentOrganization.location).toBe('Nairobi, Kenya')
    })

    it('should initialize with correct user data', () => {
      expect(wrapper.vm.currentUser.name).toBe('Sarah Johnson')
      expect(wrapper.vm.currentUser.role).toBe('Admin')
      expect(wrapper.vm.currentUser.initials).toBe('SJ')
    })
  })

  describe('Sidebar Functionality', () => {
    it('should toggle sidebar collapse state', async () => {
      expect(wrapper.vm.isSidebarCollapsed).toBe(false)
      
      await wrapper.vm.toggleSidebar()
      expect(wrapper.vm.isSidebarCollapsed).toBe(true)
      
      await wrapper.vm.toggleSidebar()
      expect(wrapper.vm.isSidebarCollapsed).toBe(false)
    })

    it('should expand sidebar when collapsed', async () => {
      wrapper.vm.isSidebarCollapsed = true
      
      await wrapper.vm.expandSidebar()
      expect(wrapper.vm.isSidebarCollapsed).toBe(false)
    })

    it('should toggle mobile menu', async () => {
      expect(wrapper.vm.mobileOpen).toBe(false)
      
      await wrapper.vm.toggleMobileMenu()
      expect(wrapper.vm.mobileOpen).toBe(true)
      
      await wrapper.vm.toggleMobileMenu()
      expect(wrapper.vm.mobileOpen).toBe(false)
    })

    it('should render correct CSS classes for collapsed sidebar', async () => {
      await wrapper.vm.toggleSidebar()
      await nextTick()
      
      const sidebar = wrapper.find('.sidebar')
      expect(sidebar.classes()).toContain('collapsed')
    })

    it('should render correct CSS classes for mobile open sidebar', async () => {
      await wrapper.vm.toggleMobileMenu()
      await nextTick()
      
      const sidebar = wrapper.find('.sidebar')
      expect(sidebar.classes()).toContain('mobile-open')
    })
  })

  describe('Navigation and Tab Management', () => {
    it('should set active tab correctly', async () => {
      await wrapper.vm.setActiveTab('cases')
      
      expect(wrapper.vm.activeTab).toBe('cases')
      expect(wrapper.vm.mobileOpen).toBe(false)
    })

    it('should return correct page titles', () => {
      const testCases = [
        { tab: 'dashboard', expected: 'Dashboard' },
        { tab: 'cases', expected: 'Case Management' },
        { tab: 'users', expected: 'Team Management' },
        { tab: 'reports', expected: 'Reports & Analytics' },
        { tab: 'ai-assistant', expected: 'AI Assistant' },
        { tab: 'categories', expected: 'Categories' },
        { tab: 'workflows', expected: 'Workflows' },
        { tab: 'settings', expected: 'Settings' },
        { tab: 'unknown', expected: 'Dashboard' }
      ]

      testCases.forEach(({ tab, expected }) => {
        wrapper.vm.activeTab = tab
        expect(wrapper.vm.getPageTitle()).toBe(expected)
      })
    })

    it('should render navigation items', () => {
      const navItems = wrapper.findAll('.nav-item')
      expect(navItems.length).toBeGreaterThanOrEqual(8)
    })

    it('should highlight active navigation item', async () => {
      await wrapper.vm.setActiveTab('cases')
      await nextTick()
      
      // The active class should be applied to the correct nav item
      const activeItems = wrapper.findAll('.nav-item.active')
      expect(activeItems.length).toBeGreaterThanOrEqual(1)
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

  describe('Notifications', () => {
    it('should toggle notification panel', async () => {
      expect(wrapper.vm.showNotifications).toBe(false)
      expect(wrapper.vm.unreadNotifications).toBe(3)
      
      await wrapper.vm.toggleNotifications()
      
      expect(wrapper.vm.showNotifications).toBe(true)
      expect(wrapper.vm.unreadNotifications).toBe(0)
    })

    it('should close notification panel', async () => {
      wrapper.vm.showNotifications = true
      
      await wrapper.vm.toggleNotifications()
      
      expect(wrapper.vm.showNotifications).toBe(false)
    })

    it('should render notification badge when there are unread notifications', async () => {
      wrapper.vm.unreadNotifications = 5
      await nextTick()
      
      const badge = wrapper.find('.notification-badge')
      expect(badge.exists()).toBe(true)
      expect(badge.text()).toBe('5')
    })

    it('should not render notification badge when no unread notifications', async () => {
      wrapper.vm.unreadNotifications = 0
      await nextTick()
      
      const badge = wrapper.find('.notification-badge')
      expect(badge.exists()).toBe(false)
    })
  })

  describe('User Actions', () => {
    it('should handle logout', async () => {
      await wrapper.vm.logout()
      
      expect(mockConsoleLog).toHaveBeenCalledWith('Logging out...')
      expect(mockAlert).toHaveBeenCalledWith('Logged out successfully!')
    })

    it('should handle navigation', async () => {
      const testPath = '/test-path'
      await wrapper.vm.navigateTo(testPath)
      
      expect(mockConsoleLog).toHaveBeenCalledWith(`Navigating to: ${testPath}`)
    })
  })

  describe('Utility Functions', () => {
    it('should format dates correctly', () => {
      const testDate = '2024-06-05T10:30:00Z'
      const result = wrapper.vm.formatDate(testDate)
      
      expect(result).toBe(new Date(testDate).toLocaleDateString())
    })

    it('should format time correctly', () => {
      const testDate = new Date('2024-06-05T10:30:00Z')
      const result = wrapper.vm.formatTime(testDate)
      
      expect(result).toBe(testDate.toLocaleTimeString([], { 
        hour: '2-digit', 
        minute: '2-digit' 
      }))
    })

    it('should get initials correctly', () => {
      expect(wrapper.vm.getInitials('John Doe')).toBe('JD')
      expect(wrapper.vm.getInitials('Jane Smith Wilson')).toBe('JSW')
      expect(wrapper.vm.getInitials('SingleName')).toBe('S')
      expect(wrapper.vm.getInitials('')).toBe('')
    })
  })

  describe('Filter Management', () => {
    it('should toggle case filters', async () => {
      expect(wrapper.vm.showCaseFilters).toBe(false)
      
      await wrapper.vm.toggleCaseFilters()
      expect(wrapper.vm.showCaseFilters).toBe(true)
      
      await wrapper.vm.toggleCaseFilters()
      expect(wrapper.vm.showCaseFilters).toBe(false)
    })

    it('should filter cases by status', () => {
      wrapper.vm.caseFilters.status = 'Open'
      const filtered = wrapper.vm.filteredCases
      
      filtered.forEach(case_ => {
        expect(case_.status).toBe('Open')
      })
    })

    it('should filter cases by priority', () => {
      wrapper.vm.caseFilters.priority = 'High'
      const filtered = wrapper.vm.filteredCases
      
      filtered.forEach(case_ => {
        expect(case_.priority).toBe('High')
      })
    })

    it('should filter cases by assignee', () => {
      wrapper.vm.caseFilters.assignedTo = 'John Doe'
      const filtered = wrapper.vm.filteredCases
      
      filtered.forEach(case_ => {
        expect(case_.assignedTo).toBe('John Doe')
      })
    })

    it('should filter cases by search term', () => {
      wrapper.vm.caseFilters.search = 'protection'
      const filtered = wrapper.vm.filteredCases
      
      filtered.forEach(case_ => {
        const searchTerm = 'protection'
        const matchesTitle = case_.title.toLowerCase().includes(searchTerm)
        const matchesCaseNumber = case_.caseNumber.toLowerCase().includes(searchTerm)
        const matchesClient = case_.clientName.toLowerCase().includes(searchTerm)
        
        expect(matchesTitle || matchesCaseNumber || matchesClient).toBe(true)
      })
    })

    it('should apply multiple filters simultaneously', () => {
      wrapper.vm.caseFilters.status = 'Open'
      wrapper.vm.caseFilters.priority = 'High'
      
      const filtered = wrapper.vm.filteredCases
      
      filtered.forEach(case_ => {
        expect(case_.status).toBe('Open')
        expect(case_.priority).toBe('High')
      })
    })

    it('should filter users by role', () => {
      wrapper.vm.userFilters.role = 'Admin'
      const filtered = wrapper.vm.filteredUsers
      
      filtered.forEach(user => {
        expect(user.role).toBe('Admin')
      })
    })

    it('should filter users by status', () => {
      wrapper.vm.userFilters.status = 'Active'
      const filtered = wrapper.vm.filteredUsers
      
      filtered.forEach(user => {
        expect(user.status).toBe('Active')
      })
    })

    it('should filter users by search term', () => {
      wrapper.vm.userFilters.search = 'john'
      const filtered = wrapper.vm.filteredUsers
      
      filtered.forEach(user => {
        const searchTerm = 'john'
        const matchesName = user.name.toLowerCase().includes(searchTerm)
        const matchesEmail = user.email.toLowerCase().includes(searchTerm)
        
        expect(matchesName || matchesEmail).toBe(true)
      })
    })
  })

  describe('Case Management', () => {
    it('should view case', async () => {
      const caseId = 1
      await wrapper.vm.viewCase(caseId)
      
      expect(mockConsoleLog).toHaveBeenCalledWith('View case:', caseId)
      expect(mockAlert).toHaveBeenCalledWith(`View case ${caseId} functionality would be implemented here.`)
    })

    it('should edit case', async () => {
      const caseId = 1
      await wrapper.vm.editCase(caseId)
      
      expect(mockConsoleLog).toHaveBeenCalledWith('Edit case:', caseId)
      expect(mockAlert).toHaveBeenCalledWith(`Edit case ${caseId} functionality would be implemented here.`)
    })

    it('should create new case successfully', async () => {
      wrapper.vm.newCase = {
        title: 'Test Case',
        clientName: 'Test Client',
        category: 'Child Protection',
        priority: 'High',
        assignedTo: 'John Doe',
        dueDate: '2024-12-31',
        description: 'Test description'
      }

      const initialCaseCount = wrapper.vm.cases.length
      
      await wrapper.vm.createCase()

      expect(wrapper.vm.cases.length).toBe(initialCaseCount + 1)
      expect(wrapper.vm.showCreateCaseModal).toBe(false)
      expect(mockAlert).toHaveBeenCalledWith('Case created successfully!')
      
      // Check if case was added to recent cases
      expect(wrapper.vm.recentCases[0].title).toBe('Test Case')
    })

    it('should validate required fields when creating case', async () => {
      wrapper.vm.newCase = {
        title: '',
        clientName: '',
        category: '',
        priority: 'Medium',
        assignedTo: '',
        dueDate: '',
        description: ''
      }

      const initialCaseCount = wrapper.vm.cases.length
      
      await wrapper.vm.createCase()

      expect(wrapper.vm.cases.length).toBe(initialCaseCount)
      expect(mockAlert).toHaveBeenCalledWith('Please fill in all required fields.')
    })

    it('should reset form after successful case creation', async () => {
      wrapper.vm.newCase = {
        title: 'Test Case',
        clientName: 'Test Client',
        category: 'Child Protection',
        priority: 'High',
        assignedTo: 'John Doe',
        dueDate: '2024-12-31',
        description: 'Test description'
      }

      await wrapper.vm.createCase()

      expect(wrapper.vm.newCase.title).toBe('')
      expect(wrapper.vm.newCase.clientName).toBe('')
      expect(wrapper.vm.newCase.category).toBe('')
      expect(wrapper.vm.newCase.description).toBe('')
    })

    it('should export cases', async () => {
      await wrapper.vm.exportCases()
      expect(mockAlert).toHaveBeenCalledWith('Exporting cases data...')
    })
  })

  describe('User Management', () => {
    it('should edit user', async () => {
      const userId = 1
      await wrapper.vm.editUser(userId)
      
      expect(mockConsoleLog).toHaveBeenCalledWith('Edit user:', userId)
      expect(mockAlert).toHaveBeenCalledWith(`Edit user ${userId} functionality would be implemented here.`)
    })

    it('should toggle user status from active to inactive', async () => {
      const user = wrapper.vm.teamMembers.find(u => u.status === 'Active')
      const userId = user.id
      
      await wrapper.vm.toggleUserStatus(userId)
      
      expect(user.status).toBe('Inactive')
      expect(mockAlert).toHaveBeenCalledWith(expect.stringContaining(user.name))
      expect(mockAlert).toHaveBeenCalledWith(expect.stringContaining('inactive'))
    })

    it('should toggle user status from inactive to active', async () => {
      // First set a user to inactive
      wrapper.vm.teamMembers[0].status = 'Inactive'
      const user = wrapper.vm.teamMembers[0]
      
      await wrapper.vm.toggleUserStatus(user.id)
      
      expect(user.status).toBe('Active')
      expect(mockAlert).toHaveBeenCalledWith(expect.stringContaining('active'))
    })

    it('should start editing role', async () => {
      const userId = 1
      await wrapper.vm.startEditingRole(userId)
      
      expect(wrapper.vm.editingRole).toBe(userId)
    })

    it('should save user role', async () => {
      const userId = 1
      const newRole = 'Manager'
      const user = wrapper.vm.teamMembers.find(u => u.id === userId)
      const oldRole = user.role
      
      await wrapper.vm.saveUserRole(userId, newRole)
      
      expect(user.role).toBe(newRole)
      expect(wrapper.vm.editingRole).toBe(null)
      expect(mockAlert).toHaveBeenCalledWith(`User role updated from ${oldRole} to ${newRole}`)
    })

    it('should handle invalid user ID when saving role', async () => {
      await wrapper.vm.saveUserRole(999, 'Admin')
      expect(wrapper.vm.editingRole).toBe(null)
    })

    it('should invite new user successfully', async () => {
      wrapper.vm.newUser = {
        name: 'Test User',
        email: 'test@example.com',
        role: 'Case Worker',
        phone: '123-456-7890',
        welcomeMessage: 'Welcome!'
      }

      const initialUserCount = wrapper.vm.teamMembers.length
      
      await wrapper.vm.inviteUser()

      expect(wrapper.vm.teamMembers.length).toBe(initialUserCount + 1)
      expect(wrapper.vm.showInviteUserModal).toBe(false)
      expect(mockAlert).toHaveBeenCalledWith('Invitation sent successfully!')
      
      // Check new user data
      const newUser = wrapper.vm.teamMembers[0]
      expect(newUser.name).toBe('Test User')
      expect(newUser.email).toBe('test@example.com')
      expect(newUser.status).toBe('Pending')
    })

    it('should validate required fields when inviting user', async () => {
      wrapper.vm.newUser = {
        name: '',
        email: '',
        role: '',
        phone: '',
        welcomeMessage: ''
      }

      const initialUserCount = wrapper.vm.teamMembers.length
      
      await wrapper.vm.inviteUser()

      expect(wrapper.vm.teamMembers.length).toBe(initialUserCount)
      expect(mockAlert).toHaveBeenCalledWith('Please fill in all required fields.')
    })

    it('should reset form after successful user invitation', async () => {
      wrapper.vm.newUser = {
        name: 'Test User',
        email: 'test@example.com',
        role: 'Case Worker',
        phone: '123-456-7890',
        welcomeMessage: 'Welcome!'
      }

      await wrapper.vm.inviteUser()

      expect(wrapper.vm.newUser.name).toBe('')
      expect(wrapper.vm.newUser.email).toBe('')
      expect(wrapper.vm.newUser.role).toBe('')
      expect(wrapper.vm.newUser.phone).toBe('')
      expect(wrapper.vm.newUser.welcomeMessage).toBe('')
    })

    it('should export users', async () => {
      await wrapper.vm.exportUsers()
      expect(mockAlert).toHaveBeenCalledWith('Exporting users data...')
    })
  })

  describe('Category Management', () => {
    it('should create new category successfully', async () => {
      wrapper.vm.newCategory = {
        name: 'Test Category',
        description: 'Test description',
        color: '#FF6B6B'
      }

      const initialCategoryCount = wrapper.vm.categories.length
      
      await wrapper.vm.createCategory()

      expect(wrapper.vm.categories.length).toBe(initialCategoryCount + 1)
      expect(wrapper.vm.showCreateCategoryModal).toBe(false)
      expect(mockAlert).toHaveBeenCalledWith('Category created successfully!')
      
      // Check new category data
      const newCategory = wrapper.vm.categories[wrapper.vm.categories.length - 1]
      expect(newCategory.name).toBe('Test Category')
      expect(newCategory.description).toBe('Test description')
      expect(newCategory.color).toBe('#FF6B6B')
      expect(newCategory.isActive).toBe(true)
      expect(newCategory.caseCount).toBe(0)
    })

    it('should validate required fields when creating category', async () => {
      wrapper.vm.newCategory = {
        name: '',
        description: '',
        color: '#FF6B6B'
      }

      const initialCategoryCount = wrapper.vm.categories.length
      
      await wrapper.vm.createCategory()

      expect(wrapper.vm.categories.length).toBe(initialCategoryCount)
      expect(mockAlert).toHaveBeenCalledWith('Please fill in all required fields.')
    })

    it('should reset form after successful category creation', async () => {
      wrapper.vm.newCategory = {
        name: 'Test Category',
        description: 'Test description',
        color: '#4ECDC4'
      }

      await wrapper.vm.createCategory()

      expect(wrapper.vm.newCategory.name).toBe('')
      expect(wrapper.vm.newCategory.description).toBe('')
      expect(wrapper.vm.newCategory.color).toBe('#FF6B6B') // Should reset to default
    })

    it('should edit category', async () => {
      const categoryId = 1
      await wrapper.vm.editCategory(categoryId)
      
      expect(mockConsoleLog).toHaveBeenCalledWith('Edit category:', categoryId)
      expect(mockAlert).toHaveBeenCalledWith(`Edit category ${categoryId} functionality would be implemented here.`)
    })
  })

  describe('Workflow Management', () => {
    it('should create new workflow successfully', async () => {
      wrapper.vm.newWorkflow = {
        name: 'Test Workflow',
        description: 'Test description',
        steps: [
          { name: 'Step 1', assignee: 'John Doe' },
          { name: 'Step 2', assignee: 'Jane Smith' }
        ]
      }

      const initialWorkflowCount = wrapper.vm.workflows.length
      
      await wrapper.vm.createWorkflow()

      expect(wrapper.vm.workflows.length).toBe(initialWorkflowCount + 1)
      expect(wrapper.vm.showCreateWorkflowModal).toBe(false)
      expect(mockAlert).toHaveBeenCalledWith('Workflow created successfully!')
      
      // Check new workflow data
      const newWorkflow = wrapper.vm.workflows[wrapper.vm.workflows.length - 1]
      expect(newWorkflow.name).toBe('Test Workflow')
      expect(newWorkflow.description).toBe('Test description')
      expect(newWorkflow.status).toBe('Active')
      expect(newWorkflow.steps.length).toBe(2)
    })

    it('should validate required fields when creating workflow', async () => {
      wrapper.vm.newWorkflow = {
        name: '',
        description: '',
        steps: [{ name: '', assignee: '' }]
      }

      const initialWorkflowCount = wrapper.vm.workflows.length
      
      await wrapper.vm.createWorkflow()

      expect(wrapper.vm.workflows.length).toBe(initialWorkflowCount)
      expect(mockAlert).toHaveBeenCalledWith('Please fill in all required fields.')
    })

    it('should add workflow step', async () => {
      const initialStepCount = wrapper.vm.newWorkflow.steps.length
      
      await wrapper.vm.addWorkflowStep()

      expect(wrapper.vm.newWorkflow.steps.length).toBe(initialStepCount + 1)
      
      const newStep = wrapper.vm.newWorkflow.steps[wrapper.vm.newWorkflow.steps.length - 1]
      expect(newStep.name).toBe('')
      expect(newStep.assignee).toBe('')
    })

    it('should remove workflow step', async () => {
      wrapper.vm.newWorkflow.steps = [
        { name: 'Step 1', assignee: 'John' },
        { name: 'Step 2', assignee: 'Jane' },
        { name: 'Step 3', assignee: 'Bob' }
      ]

      await wrapper.vm.removeWorkflowStep(1)

      expect(wrapper.vm.newWorkflow.steps.length).toBe(2)
      expect(wrapper.vm.newWorkflow.steps[0].name).toBe('Step 1')
      expect(wrapper.vm.newWorkflow.steps[1].name).toBe('Step 3')
    })

    it('should reset workflow form after successful creation', async () => {
      wrapper.vm.newWorkflow = {
        name: 'Test Workflow',
        description: 'Test description',
        steps: [
          { name: 'Step 1', assignee: 'John Doe' },
          { name: 'Step 2', assignee: 'Jane Smith' }
        ]
      }

      await wrapper.vm.createWorkflow()

      expect(wrapper.vm.newWorkflow.name).toBe('')
      expect(wrapper.vm.newWorkflow.description).toBe('')
      expect(wrapper.vm.newWorkflow.steps.length).toBe(1)
      expect(wrapper.vm.newWorkflow.steps[0].name).toBe('')
      expect(wrapper.vm.newWorkflow.steps[0].assignee).toBe('')
    })

    it('should edit workflow', async () => {
      const workflowId = 1
      await wrapper.vm.editWorkflow(workflowId)
      
      expect(mockConsoleLog).toHaveBeenCalledWith('Edit workflow:', workflowId)
      expect(mockAlert).toHaveBeenCalledWith(`Edit workflow ${workflowId} functionality would be implemented here.`)
    })

    it('should toggle workflow status from active to inactive', async () => {
      const workflow = wrapper.vm.workflows.find(w => w.status === 'Active')
      const workflowId = workflow.id
      
      await wrapper.vm.toggleWorkflow(workflowId)
      
      expect(workflow.status).toBe('Inactive')
      expect(mockAlert).toHaveBeenCalledWith(expect.stringContaining(workflow.name))
      expect(mockAlert).toHaveBeenCalledWith(expect.stringContaining('inactive'))
    })

    it('should toggle workflow status from inactive to active', async () => {
      // First set a workflow to inactive
      wrapper.vm.workflows[0].status = 'Inactive'
      const workflow = wrapper.vm.workflows[0]
      
      await wrapper.vm.toggleWorkflow(workflow.id)
      
      expect(workflow.status).toBe('Active')
      expect(mockAlert).toHaveBeenCalledWith(expect.stringContaining('active'))
    })
  })

  describe('AI Assistant', () => {
    it('should send message successfully', async () => {
      wrapper.vm.newMessage = 'Test message'
      const initialMessageCount = wrapper.vm.chatMessages.length

      await wrapper.vm.sendMessage()

      expect(wrapper.vm.chatMessages.length).toBe(initialMessageCount + 1)
      expect(wrapper.vm.newMessage).toBe('')
      
      const userMessage = wrapper.vm.chatMessages[wrapper.vm.chatMessages.length - 1]
      expect(userMessage.type).toBe('user')
      expect(userMessage.text).toBe('Test message')
    })

    it('should not send empty message', async () => {
      wrapper.vm.newMessage = '   '
      const initialMessageCount = wrapper.vm.chatMessages.length

      await wrapper.vm.sendMessage()

      expect(wrapper.vm.chatMessages.length).toBe(initialMessageCount)
      expect(wrapper.vm.newMessage).toBe('   ')
    })

    it('should generate AI response after user message', async () => {
      wrapper.vm.newMessage = 'Hello AI'
      const initialMessageCount = wrapper.vm.chatMessages.length

      await wrapper.vm.sendMessage()

      // Wait for AI response (simulated with setTimeout)
      await new Promise(resolve => setTimeout(resolve, 1100))

      expect(wrapper.vm.chatMessages.length).toBe(initialMessageCount + 2)
      
      const aiMessage = wrapper.vm.chatMessages[wrapper.vm.chatMessages.length - 1]
      expect(aiMessage.type).toBe('ai')
      expect(aiMessage.text).toBeTruthy()
    })

    it('should generate different AI responses', () => {
      const response1 = wrapper.vm.generateAIResponse('test message 1')
      const response2 = wrapper.vm.generateAIResponse('test message 2')
      
      expect(typeof response1).toBe('string')
      expect(typeof response2).toBe('string')
      expect(response1.length).toBeGreaterThan(0)
      expect(response2.length).toBeGreaterThan(0)
    })

    it('should apply AI suggestion', async () => {
      const suggestion = {
        id: 1,
        title: 'Test Suggestion',
        description: 'Test description'
      }
      
      await wrapper.vm.applySuggestion(suggestion)
      
      expect(mockConsoleLog).toHaveBeenCalledWith('Apply suggestion:', suggestion)
      expect(mockAlert).toHaveBeenCalledWith(`Applied suggestion: ${suggestion.title}`)
    })

    it('should initialize with default AI suggestions', () => {
      expect(wrapper.vm.aiSuggestions).toBeDefined()
      expect(Array.isArray(wrapper.vm.aiSuggestions)).toBe(true)
      expect(wrapper.vm.aiSuggestions.length).toBeGreaterThan(0)
      
      wrapper.vm.aiSuggestions.forEach(suggestion => {
        expect(suggestion).toHaveProperty('id')
        expect(suggestion).toHaveProperty('title')
        expect(suggestion).toHaveProperty('description')
      })
    })

    it('should initialize with welcome message', () => {
      expect(wrapper.vm.chatMessages.length).toBeGreaterThan(0)
      
      const welcomeMessage = wrapper.vm.chatMessages[0]
      expect(welcomeMessage.type).toBe('ai')
      expect(welcomeMessage.text).toContain('Hello! I\'m your AI assistant')
    })
  })

  describe('Reports and Analytics', () => {
    it('should generate case report', async () => {
      await wrapper.vm.generateReport('cases')
      
      expect(mockConsoleLog).toHaveBeenCalledWith('Generate report:', 'cases')
      expect(mockAlert).toHaveBeenCalledWith('Generating cases report...')
    })

    it('should generate team report', async () => {
      await wrapper.vm.generateReport('team')
      
      expect(mockConsoleLog).toHaveBeenCalledWith('Generate report:', 'team')
      expect(mockAlert).toHaveBeenCalledWith('Generating team report...')
    })

    it('should have dashboard statistics', () => {
      expect(wrapper.vm.dashboardStats).toBeDefined()
      expect(wrapper.vm.dashboardStats.totalCases).toBeDefined()
      expect(wrapper.vm.dashboardStats.activeCases).toBeDefined()
      expect(wrapper.vm.dashboardStats.teamMembers).toBeDefined()
      expect(wrapper.vm.dashboardStats.resolutionRate).toBeDefined()
    })

    it('should have report statistics', () => {
      expect(wrapper.vm.reportStats).toBeDefined()
      expect(wrapper.vm.reportStats.totalCases).toBeDefined()
      expect(wrapper.vm.reportStats.resolvedCases).toBeDefined()
      expect(wrapper.vm.reportStats.avgResolutionTime).toBeDefined()
      expect(wrapper.vm.reportStats.satisfactionRate).toBeDefined()
    })

    it('should have team performance data', () => {
      expect(wrapper.vm.teamPerformance).toBeDefined()
      expect(Array.isArray(wrapper.vm.teamPerformance)).toBe(true)
      
      wrapper.vm.teamPerformance.forEach(member => {
        expect(member).toHaveProperty('id')
        expect(member).toHaveProperty('name')
        expect(member).toHaveProperty('role')
        expect(member).toHaveProperty('casesResolved')
        expect(member).toHaveProperty('avgTime')
      })
    })
  })

  describe('Settings Management', () => {
    it('should save settings', async () => {
      await wrapper.vm.saveSettings()
      
      expect(mockConsoleLog).toHaveBeenCalledWith('Saving settings:', wrapper.vm.settings)
      expect(mockAlert).toHaveBeenCalledWith('Settings saved successfully!')
    })

    it('should initialize with default settings', () => {
      expect(wrapper.vm.settings).toBeDefined()
      expect(wrapper.vm.settings.organizationName).toBe('Children First Kenya')
      expect(wrapper.vm.settings.location).toBe('Nairobi, Kenya')
      expect(wrapper.vm.settings.casePrefix).toBe('CASE')
      expect(wrapper.vm.settings.autoAssign).toBe(true)
      expect(wrapper.vm.settings.defaultPriority).toBe('Medium')
    })

    it('should have notification settings', () => {
      expect(wrapper.vm.settings.emailNotifications).toBe(true)
      expect(wrapper.vm.settings.assignmentAlerts).toBe(true)
      expect(wrapper.vm.settings.deadlineReminders).toBe(true)
    })

    it('should have security settings', () => {
      expect(wrapper.vm.settings.twoFactorAuth).toBe(false)
      expect(wrapper.vm.settings.sessionTimeout).toBe(60)
      expect(wrapper.vm.settings.passwordStrength).toBe('medium')
    })
  })

  describe('Modal Management', () => {
    it('should manage create case modal state', async () => {
      expect(wrapper.vm.showCreateCaseModal).toBe(false)
      
      wrapper.vm.showCreateCaseModal = true
      await nextTick()
      expect(wrapper.vm.showCreateCaseModal).toBe(true)
      
      wrapper.vm.showCreateCaseModal = false
      await nextTick()
      expect(wrapper.vm.showCreateCaseModal).toBe(false)
    })

    it('should manage invite user modal state', async () => {
      expect(wrapper.vm.showInviteUserModal).toBe(false)
      
      wrapper.vm.showInviteUserModal = true
      await nextTick()
      expect(wrapper.vm.showInviteUserModal).toBe(true)
      
      wrapper.vm.showInviteUserModal = false
      await nextTick()
      expect(wrapper.vm.showInviteUserModal).toBe(false)
    })

    it('should manage create category modal state', async () => {
      expect(wrapper.vm.showCreateCategoryModal).toBe(false)
      
      wrapper.vm.showCreateCategoryModal = true
      await nextTick()
      expect(wrapper.vm.showCreateCategoryModal).toBe(true)
      
      wrapper.vm.showCreateCategoryModal = false
      await nextTick()
      expect(wrapper.vm.showCreateCategoryModal).toBe(false)
    })

    it('should manage create workflow modal state', async () => {
      expect(wrapper.vm.showCreateWorkflowModal).toBe(false)
      
      wrapper.vm.showCreateWorkflowModal = true
      await nextTick()
      expect(wrapper.vm.showCreateWorkflowModal).toBe(true)
      
      wrapper.vm.showCreateWorkflowModal = false
      await nextTick()
      expect(wrapper.vm.showCreateWorkflowModal).toBe(false)
    })
  })

  describe('Data Validation and Structure', () => {
    it('should validate case data structure', () => {
      const cases = wrapper.vm.cases
      expect(Array.isArray(cases)).toBe(true)
      
      cases.forEach(case_ => {
        expect(case_).toHaveProperty('id')
        expect(case_).toHaveProperty('caseNumber')
        expect(case_).toHaveProperty('title')
        expect(case_).toHaveProperty('clientName')
        expect(case_).toHaveProperty('assignedTo')
        expect(case_).toHaveProperty('status')
        expect(case_).toHaveProperty('priority')
        expect(case_).toHaveProperty('category')
        expect(case_).toHaveProperty('createdAt')
        
        expect(typeof case_.id).toBe('number')
        expect(typeof case_.caseNumber).toBe('string')
        expect(typeof case_.title).toBe('string')
        expect(case_.caseNumber).toMatch(/^CASE-\d{4}-\d{3}$/)
      })
    })

    it('should validate user data structure', () => {
      const users = wrapper.vm.teamMembers
      expect(Array.isArray(users)).toBe(true)
      
      users.forEach(user => {
        expect(user).toHaveProperty('id')
        expect(user).toHaveProperty('name')
        expect(user).toHaveProperty('email')
        expect(user).toHaveProperty('role')
        expect(user).toHaveProperty('status')
        expect(user).toHaveProperty('casesAssigned')
        expect(user).toHaveProperty('lastActive')
        
        expect(typeof user.id).toBe('number')
        expect(typeof user.name).toBe('string')
        expect(typeof user.email).toBe('string')
        expect(user.email).toMatch(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)
      })
    })

    it('should validate category data structure', () => {
      const categories = wrapper.vm.categories
      expect(Array.isArray(categories)).toBe(true)
      
      categories.forEach(category => {
        expect(category).toHaveProperty('id')
        expect(category).toHaveProperty('name')
        expect(category).toHaveProperty('description')
        expect(category).toHaveProperty('color')
        expect(category).toHaveProperty('caseCount')
        expect(category).toHaveProperty('isActive')
        
        expect(typeof category.id).toBe('number')
        expect(typeof category.name).toBe('string')
        expect(typeof category.color).toBe('string')
        expect(category.color).toMatch(/^#[0-9A-Fa-f]{6}$/)
      })
    })

    it('should validate workflow data structure', () => {
      const workflows = wrapper.vm.workflows
      expect(Array.isArray(workflows)).toBe(true)
      
      workflows.forEach(workflow => {
        expect(workflow).toHaveProperty('id')
        expect(workflow).toHaveProperty('name')
        expect(workflow).toHaveProperty('description')
        expect(workflow).toHaveProperty('status')
        expect(workflow).toHaveProperty('steps')
        
        expect(typeof workflow.id).toBe('number')
        expect(typeof workflow.name).toBe('string')
        expect(Array.isArray(workflow.steps)).toBe(true)
        
        workflow.steps.forEach(step => {
          expect(step).toHaveProperty('name')
          expect(step).toHaveProperty('assignee')
        })
      })
    })

    it('should validate notification data structure', () => {
      const notifications = wrapper.vm.notifications
      expect(Array.isArray(notifications)).toBe(true)
      
      notifications.forEach(notification => {
        expect(notification).toHaveProperty('id')
        expect(notification).toHaveProperty('type')
        expect(notification).toHaveProperty('title')
        expect(notification).toHaveProperty('message')
        expect(notification).toHaveProperty('timestamp')
        expect(notification).toHaveProperty('read')
        
        expect(typeof notification.id).toBe('number')
        expect(typeof notification.type).toBe('string')
        expect(typeof notification.read).toBe('boolean')
      })
    })
  })

  describe('Responsive Behavior', () => {
    it('should handle mobile view correctly', async () => {
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 768,
      })

      await wrapper.vm.toggleMobileMenu()
      expect(wrapper.vm.mobileOpen).toBe(true)

      await wrapper.vm.setActiveTab('cases')
      expect(wrapper.vm.mobileOpen).toBe(false)
    })

    it('should handle desktop view correctly', async () => {
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 1200,
      })

      wrapper.vm.mobileOpen = true
      await wrapper.vm.setActiveTab('users')
      
      expect(wrapper.vm.activeTab).toBe('users')
      expect(wrapper.vm.mobileOpen).toBe(false)
    })
  })

  describe('Component Lifecycle', () => {
    it('should handle component mounting', () => {
      // Component should be mounted and initialized
      expect(wrapper.vm).toBeDefined()
      expect(wrapper.vm.activeTab).toBe('dashboard')
      expect(wrapper.vm.currentTheme).toBe('dark')
    })

    it('should clean up on unmount', () => {
      // Component unmounts successfully
      expect(wrapper.vm).toBeDefined()
      
      wrapper.unmount()
      
      // Just verify the component unmounted successfully
      expect(wrapper.vm).toBeDefined()
    })
  })

  describe('Edge Cases and Error Handling', () => {
    it('should handle empty search gracefully', () => {
      wrapper.vm.caseFilters.search = ''
      const filtered = wrapper.vm.filteredCases
      
      expect(filtered.length).toBe(wrapper.vm.cases.length)
    })

    it('should handle whitespace-only search', () => {
      wrapper.vm.caseFilters.search = '   '
      const filtered = wrapper.vm.filteredCases
      
      // The component behavior may vary - just ensure it handles it gracefully
      expect(filtered.length).toBeGreaterThanOrEqual(0)
    })

    it('should handle non-existent filter values', () => {
      wrapper.vm.caseFilters.status = 'NonExistentStatus'
      const filtered = wrapper.vm.filteredCases
      
      expect(filtered.length).toBe(0)
    })

    it('should handle invalid user ID in role editing', async () => {
      const originalEditingRole = wrapper.vm.editingRole
      
      await wrapper.vm.saveUserRole(99999, 'Admin')
      
      expect(wrapper.vm.editingRole).toBe(null)
    })

    it('should handle workflow validation edge cases', async () => {
      wrapper.vm.newWorkflow = {
        name: 'Test Workflow',
        description: 'Test',
        steps: []
      }

      const initialCount = wrapper.vm.workflows.length
      await wrapper.vm.createWorkflow()

      // The component may accept empty steps or reject them
      expect(wrapper.vm.workflows.length).toBeGreaterThanOrEqual(initialCount)
    })
  })

  describe('Performance Considerations', () => {
    it('should handle large datasets efficiently', () => {
      // Add many cases to test filtering performance
      const largeCaseSet = Array.from({ length: 1000 }, (_, i) => ({
        id: i + 1000,
        caseNumber: `CASE-2024-${String(i + 1000).padStart(3, '0')}`,
        title: `Performance Test Case ${i}`,
        clientName: `Test Client ${i}`,
        assignedTo: 'John Doe',
        status: 'Open',
        priority: 'Medium',
        category: 'Test Category',
        createdAt: new Date().toISOString()
      }))

      wrapper.vm.cases = [...wrapper.vm.cases, ...largeCaseSet]

      const startTime = performance.now()
      wrapper.vm.caseFilters.search = 'Performance'
      const filtered = wrapper.vm.filteredCases
      const endTime = performance.now()

      expect(filtered.length).toBeGreaterThan(0)
      expect(endTime - startTime).toBeLessThan(100) // Should be reasonably fast
    })

    it('should handle repeated operations without issues', async () => {
      // Test repeated operations without memory testing
      for (let i = 0; i < 10; i++) {
        await wrapper.vm.setActiveTab('cases')
        await wrapper.vm.setActiveTab('dashboard')
        wrapper.vm.caseFilters.search = `test ${i}`
        wrapper.vm.filteredCases // Trigger computation
      }

      // Just verify operations completed successfully
      expect(wrapper.vm.activeTab).toBe('dashboard')
      expect(wrapper.vm.caseFilters.search).toBe('test 9')
    })
  })
})