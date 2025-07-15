// src/utils/__tests__/sipClient.test.js
import { describe, it, expect, beforeEach, vi } from 'vitest'
import {
  on,
  off,
  updateIceServers
} from '../sipClient.js'

// Mock JsSIP to avoid complex initialization issues
vi.mock('jssip', () => ({
  default: {
    UA: vi.fn(() => ({
      on: vi.fn(),
      register: vi.fn(),
      unregister: vi.fn(),
      call: vi.fn(),
      isRegistered: vi.fn(() => false),
      registrationState: 'unregistered',
      connectionState: 'disconnected',
      configuration: { uri: 'sip:test@domain.com' },
      stop: vi.fn()
    })),
    WebSocketInterface: vi.fn()
  }
}))

describe('SIP Client', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Event Management', () => {
    it('registers event listeners correctly', () => {
      const callback = vi.fn()
      
      expect(() => on('testEvent', callback)).not.toThrow()
    })

    it('validates callback is a function', () => {
      expect(() => on('test', 'not-a-function')).toThrow('Callback must be a function')
      expect(() => on('test', null)).toThrow('Callback must be a function')
      expect(() => on('test', undefined)).toThrow('Callback must be a function')
    })

    it('unregisters event listeners', () => {
      const callback = vi.fn()
      on('testEvent', callback)
      
      expect(() => off('testEvent')).not.toThrow()
    })

    it('handles unregistering non-existent events', () => {
      expect(() => off('nonExistentEvent')).not.toThrow()
    })
  })

  describe('ICE Server Management', () => {
    it('updates ICE servers with valid array', () => {
      const servers = [
        { urls: 'stun:stun.example.com:19302' },
        { urls: 'turn:turn.example.com:3478', username: 'user', credential: 'pass' }
      ]
      
      expect(() => updateIceServers(servers)).not.toThrow()
    })

    it('accepts empty array', () => {
      expect(() => updateIceServers([])).not.toThrow()
    })

    it('throws error for non-array input', () => {
      expect(() => updateIceServers('not-an-array')).toThrow('ICE servers must be an array')
      expect(() => updateIceServers({})).toThrow('ICE servers must be an array')
      expect(() => updateIceServers(null)).toThrow('ICE servers must be an array')
      expect(() => updateIceServers(undefined)).toThrow('ICE servers must be an array')
      expect(() => updateIceServers(123)).toThrow('ICE servers must be an array')
    })
  })

  describe('Configuration Validation', () => {
    it('validates required SIP parameters', async () => {
      const { initSIP } = await import('../sipClient.js')
      
      expect(() => initSIP({})).toThrow('Missing required SIP connection parameters')
      expect(() => initSIP({ sipUri: 'test' })).toThrow('Missing required SIP connection parameters')
      expect(() => initSIP({ password: 'test' })).toThrow('Missing required SIP connection parameters')
      expect(() => initSIP({ websocketURL: 'test' })).toThrow('Missing required SIP connection parameters')
    })

    it('accepts valid configuration', async () => {
      const { initSIP } = await import('../sipClient.js')
      
      const validConfig = {
        sipUri: 'sip:test@domain.com',
        password: 'password123',
        websocketURL: 'wss://sip.domain.com'
      }
      
      expect(() => initSIP(validConfig)).not.toThrow()
    })
  })

  describe('Utility Functions', () => {
    it('validates cleanup function exists', () => {
      // Test that cleanup function can be called without errors in isolated context
      expect(() => {
        // Test the function exists and is callable
        const { cleanup } = require('../sipClient.js')
        expect(typeof cleanup).toBe('function')
      }).not.toThrow()
    })

    it('gets call status when not initialized', async () => {
      const { getCallStatus } = await import('../sipClient.js')
      
      const status = getCallStatus()
      
      expect(status).toHaveProperty('isInCall')
      expect(status).toHaveProperty('hasIncomingCall')
      expect(status).toHaveProperty('isInQueue')
      expect(status.isInCall).toBe(false)
      expect(status.hasIncomingCall).toBe(false)
    })
  })
})