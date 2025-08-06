import { describe, it, expect } from 'vitest'
import { loadVitePressConfig } from './config-loader'
import { MARKDOWN_FILES, AIDOCS_FILES } from '../utils/docs'

describe('Basic Setup Verification', () => {
  it('should load VitePress config successfully', () => {
    const config = loadVitePressConfig()
    expect(config).toBeDefined()
    expect(config.title).toBe('OpenCHS Docs')
  })

  it('should have markdown files list', () => {
    expect(MARKDOWN_FILES).toBeDefined()
    expect(Array.isArray(MARKDOWN_FILES)).toBe(true)
    expect(MARKDOWN_FILES.length).toBeGreaterThan(0)
  })

  it('should have aidocs files list', () => {
    expect(AIDOCS_FILES).toBeDefined()
    expect(Array.isArray(AIDOCS_FILES)).toBe(true)
    expect(AIDOCS_FILES.length).toBeGreaterThan(0)
  })

  it('should have critical files in the list', () => {
    expect(MARKDOWN_FILES).toContain('index.md')
    expect(MARKDOWN_FILES).toContain('install.md')
    expect(MARKDOWN_FILES).toContain('features.md')
  })

  it('should have proper test environment', () => {
    expect(typeof window).toBe('object')
    expect(typeof document).toBe('object')
    expect(process.env.NODE_ENV).toBe('test')
  })
})