// src/utils/__tests__/theme.test.js
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { applyTheme, getCurrentTheme } from '../theme.js'

// Mock document.documentElement
const mockDocumentElement = {
  style: { setProperty: vi.fn() },
  setAttribute: vi.fn(),
  getAttribute: vi.fn()
}

Object.defineProperty(document, 'documentElement', {
  value: mockDocumentElement,
  writable: true
})

describe('Theme Utilities', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('applies light theme correctly', () => {
    applyTheme('light')

    expect(mockDocumentElement.style.setProperty).toHaveBeenCalledWith('--background-color', '#f5f5f5')
    expect(mockDocumentElement.style.setProperty).toHaveBeenCalledWith('--text-color', '#222')
    expect(mockDocumentElement.setAttribute).toHaveBeenCalledWith('data-theme', 'light')
  })

  it('applies dark theme correctly', () => {
    applyTheme('dark')

    expect(mockDocumentElement.style.setProperty).toHaveBeenCalledWith('--background-color', '#000')
    expect(mockDocumentElement.style.setProperty).toHaveBeenCalledWith('--text-color', '#fff')
    expect(mockDocumentElement.setAttribute).toHaveBeenCalledWith('data-theme', 'dark')
  })

  it('defaults to dark theme for invalid values', () => {
    applyTheme('invalid')
    expect(mockDocumentElement.setAttribute).toHaveBeenCalledWith('data-theme', 'dark')
  })

  it('gets current theme or defaults to dark', () => {
    mockDocumentElement.getAttribute.mockReturnValue('light')
    expect(getCurrentTheme()).toBe('light')

    mockDocumentElement.getAttribute.mockReturnValue(null)
    expect(getCurrentTheme()).toBe('dark')
  })
})