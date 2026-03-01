import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import axios from 'axios'
import Form from './Form'

// Mock axios
vi.mock('axios')
const mockedAxios = vi.mocked(axios)

describe('Form', () => {
  const mockOnSubmit = vi.fn()
  const defaultProps = {
    selectedRepos: [1, 2, 3],
    onSubmit: mockOnSubmit
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders form with required fields', () => {
    render(<Form {...defaultProps} />)

    expect(screen.getByText('Configure Pull Request')).toBeInTheDocument()
    expect(screen.getByLabelText(/source branch/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/destination branch/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/pr title/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/pr body/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /create prs for 3 repos/i })).toBeInTheDocument()
  })

  it('shows default source branch value', () => {
    render(<Form {...defaultProps} />)

    const sourceInput = screen.getByLabelText(/source branch/i) as HTMLInputElement
    expect(sourceInput.value).toBe('main')
  })

  it('validates required destination branch', async () => {
    const user = userEvent.setup()
    render(<Form {...defaultProps} />)

    const submitButton = screen.getByRole('button', { name: /create prs for 3 repos/i })
    await user.click(submitButton)

    // Check that error message is displayed (may be styled but should be in DOM)
    const errorElement = document.querySelector('.error-message') || screen.getByText('Destination branch is required')
    expect(errorElement).toBeInTheDocument()
    expect(mockOnSubmit).not.toHaveBeenCalled()
  })

  it('validates branch name format', async () => {
    const user = userEvent.setup()
    render(<Form {...defaultProps} />)

    const destInput = screen.getByLabelText(/destination branch/i)
    await user.type(destInput, 'invalid branch name!')

    const submitButton = screen.getByRole('button', { name: /create prs for 3 repos/i })
    await user.click(submitButton)

    expect(screen.getByText('Branch name contains invalid characters')).toBeInTheDocument()
  })

  it('validates different source and destination branches', async () => {
    const user = userEvent.setup()
    render(<Form {...defaultProps} />)

    const destInput = screen.getByLabelText(/destination branch/i)
    await user.type(destInput, 'main') // Same as source

    const submitButton = screen.getByRole('button', { name: /create prs for 3 repos/i })
    await user.click(submitButton)

    expect(screen.getByText('Source and destination branches must be different')).toBeInTheDocument()
  })

  it('clears validation errors when user types', async () => {
    const user = userEvent.setup()
    render(<Form {...defaultProps} />)

    // First submit to trigger validation
    const submitButton = screen.getByRole('button', { name: /create prs for 3 repos/i })
    await user.click(submitButton)

    // Check that error exists (may be in span with error-message class)
    const errorBefore = document.querySelector('.error-message') || screen.queryByText('Destination branch is required')
    expect(errorBefore).toBeInTheDocument()

    // Type in destination branch
    const destInput = screen.getByLabelText(/destination branch/i)
    await user.type(destInput, 'develop')

    // Error should be cleared
    const errorAfter = document.querySelector('.error-message') || screen.queryByText('Destination branch is required')
    expect(errorAfter).not.toBeInTheDocument()
  })

  it('generates default PR title when none provided', async () => {
    const user = userEvent.setup()
    render(<Form {...defaultProps} />)

    const destInput = screen.getByLabelText(/destination branch/i)
    await user.type(destInput, 'develop')

    const submitButton = screen.getByRole('button', { name: /create prs for 3 repos/i })
    await user.click(submitButton)

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith({
        sourceBranch: 'main',
        destBranch: 'develop',
        prTitle: 'main -> develop',
        prBody: ''
      })
    })
  })

  it('uses custom PR title when provided', async () => {
    const user = userEvent.setup()
    render(<Form {...defaultProps} />)

    const destInput = screen.getByLabelText(/destination branch/i)
    await user.type(destInput, 'develop')

    const titleInput = screen.getByLabelText(/pr title/i)
    await user.type(titleInput, 'Custom PR Title')

    const submitButton = screen.getByRole('button', { name: /create prs for 3 repos/i })
    await user.click(submitButton)

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith({
        sourceBranch: 'main',
        destBranch: 'develop',
        prTitle: 'Custom PR Title',
        prBody: ''
      })
    })
  })

  it('trims whitespace from inputs', async () => {
    const user = userEvent.setup()
    render(<Form {...defaultProps} />)

    const destInput = screen.getByLabelText(/destination branch/i)
    await user.type(destInput, '  develop  ')

    const titleInput = screen.getByLabelText(/pr title/i)
    await user.type(titleInput, '  My PR  ')

    const bodyTextarea = screen.getByLabelText(/pr body/i)
    await user.type(bodyTextarea, '  Description  ')

    const submitButton = screen.getByRole('button', { name: /create prs for 3 repos/i })
    await user.click(submitButton)

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith({
        sourceBranch: 'main',
        destBranch: 'develop',
        prTitle: 'My PR',
        prBody: 'Description'
      })
    })
  })

  it('shows submitting state during form submission', async () => {
    // Mock a slow onSubmit that doesn't resolve immediately
    mockOnSubmit.mockImplementation(() => new Promise(() => {})) // Never resolves

    const user = userEvent.setup()
    render(<Form {...defaultProps} />)

    const destInput = screen.getByLabelText(/destination branch/i)
    await user.type(destInput, 'develop')

    const submitButton = screen.getByRole('button', { name: /create prs for 3 repos/i })
    await user.click(submitButton)

    // Button should be disabled during submission
    expect(screen.getByRole('button')).toBeDisabled()
  })

  it('disables submit when no repos selected', () => {
    render(<Form {...defaultProps} selectedRepos={[]} />)

    const submitButton = screen.getByRole('button', { name: /create prs for 0 repos/i })
    expect(submitButton).toBeDisabled()
  })

  it('updates button text based on selected repo count', () => {
    const { rerender } = render(<Form {...defaultProps} selectedRepos={[1]} />)
    expect(screen.getByRole('button', { name: /create prs for 1 repos/i })).toBeInTheDocument()

    rerender(<Form {...defaultProps} selectedRepos={[1, 2, 3, 4, 5]} />)
    expect(screen.getByRole('button', { name: /create prs for 5 repos/i })).toBeInTheDocument()
  })
})