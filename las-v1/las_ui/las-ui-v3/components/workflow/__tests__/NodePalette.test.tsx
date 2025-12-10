import { render, screen, fireEvent } from '@testing-library/react'
import { NodePalette } from '../NodePalette'
import { describe, it, expect, vi } from 'vitest'

describe('NodePalette', () => {
  it('renders all categories', () => {
    render(<NodePalette />)
    expect(screen.getByText('Triggers')).toBeInTheDocument()
    expect(screen.getByText('Actions')).toBeInTheDocument()
    expect(screen.getByText('Logic')).toBeInTheDocument()
    expect(screen.getByText('Outputs')).toBeInTheDocument()
  })

  it('filters nodes based on search input', () => {
    render(<NodePalette />)
    const searchInput = screen.getByPlaceholderText('Search nodes...')
    
    // Initial state: "User Input" should be visible
    expect(screen.getByText('User Input')).toBeInTheDocument()
    
    // Search for "Webhook"
    fireEvent.change(searchInput, { target: { value: 'Webhook' } })
    
    expect(screen.getByText('Webhook')).toBeInTheDocument()
    expect(screen.queryByText('User Input')).not.toBeInTheDocument()
  })

  it('sets dataTransfer on drag start', () => {
    render(<NodePalette />)
    const nodeItem = screen.getByText('User Input').closest('div[draggable="true"]')
    expect(nodeItem).toBeInTheDocument()

    const dataTransfer = {
      setData: vi.fn(),
      effectAllowed: 'none',
    }

    fireEvent.dragStart(nodeItem!, { dataTransfer })

    expect(dataTransfer.setData).toHaveBeenCalledWith('application/reactflow/type', 'trigger')
    expect(dataTransfer.setData).toHaveBeenCalledWith('application/reactflow/label', 'User Input')
    expect(dataTransfer.effectAllowed).toBe('move')
  })
})
