import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import axios from 'axios'
import RepoList from './RepoList'

// Mock axios
vi.mock('axios')
const mockedAxios = vi.mocked(axios)

describe('RepoList', () => {
  const mockSetSelectedRepos = vi.fn()
  const mockRepos = [
    { id: 1, name: 'repo1', owner: 'owner1' },
    { id: 2, name: 'repo2', owner: 'owner2' },
    { id: 3, name: 'repo3', owner: 'owner1' }
  ]

  beforeEach(() => {
    vi.clearAllMocks()
    mockedAxios.get.mockResolvedValue({ data: mockRepos })
  })

  it('renders loading state initially', () => {
    render(<RepoList selectedRepos={[]} setSelectedRepos={mockSetSelectedRepos} />)
    expect(screen.getByText('Loading repositories...')).toBeInTheDocument()
  })

  it('renders repository list after loading', async () => {
    render(<RepoList selectedRepos={[]} setSelectedRepos={mockSetSelectedRepos} />)

    await waitFor(() => {
      expect(screen.getByText('Select Repositories')).toBeInTheDocument()
    })

    // Check all repositories are rendered
    expect(screen.getByText('owner1/repo1')).toBeInTheDocument()
    expect(screen.getByText('owner2/repo2')).toBeInTheDocument()
    expect(screen.getByText('owner1/repo3')).toBeInTheDocument()
  })

  it('shows selected count', async () => {
    render(<RepoList selectedRepos={[1, 3]} setSelectedRepos={mockSetSelectedRepos} />)

    await waitFor(() => {
      expect(screen.getByText('Selected: 2 repositories')).toBeInTheDocument()
    })
  })

  it('handles checkbox selection', async () => {
    const user = userEvent.setup()
    render(<RepoList selectedRepos={[]} setSelectedRepos={mockSetSelectedRepos} />)

    await waitFor(() => {
      expect(screen.getByText('owner1/repo1')).toBeInTheDocument()
    })

    const checkbox = screen.getByRole('checkbox', { name: /owner1\/repo1/i })
    await user.click(checkbox)

    expect(mockSetSelectedRepos).toHaveBeenCalledTimes(1)
    // The function is called with a callback, so we verify it was called
    expect(mockSetSelectedRepos).toHaveBeenCalledWith(expect.any(Function))
  })

  it('handles checkbox deselection', async () => {
    const user = userEvent.setup()
    render(<RepoList selectedRepos={[1]} setSelectedRepos={mockSetSelectedRepos} />)

    await waitFor(() => {
      expect(screen.getByText('owner1/repo1')).toBeInTheDocument()
    })

    const checkbox = screen.getByRole('checkbox', { name: /owner1\/repo1/i })
    expect(checkbox).toBeChecked()

    await user.click(checkbox)

    expect(mockSetSelectedRepos).toHaveBeenCalledTimes(1)
    expect(mockSetSelectedRepos).toHaveBeenCalledWith(expect.any(Function))
  })

  it('maintains multiple selections', async () => {
    const user = userEvent.setup()
    render(<RepoList selectedRepos={[1]} setSelectedRepos={mockSetSelectedRepos} />)

    await waitFor(() => {
      expect(screen.getByText('owner1/repo1')).toBeInTheDocument()
    })

    // Select another repo
    const checkbox2 = screen.getByRole('checkbox', { name: /owner2\/repo2/i })
    await user.click(checkbox2)

    expect(mockSetSelectedRepos).toHaveBeenCalledTimes(1)
    expect(mockSetSelectedRepos).toHaveBeenCalledWith(expect.any(Function))
  })

  it('handles API error gracefully', async () => {
    mockedAxios.get.mockRejectedValue(new Error('API Error'))

    render(<RepoList selectedRepos={[]} setSelectedRepos={mockSetSelectedRepos} />)

    await waitFor(() => {
      expect(screen.getByText('Failed to load repositories. Please check your login.')).toBeInTheDocument()
    })
  })

  it('calls API on mount', () => {
    render(<RepoList selectedRepos={[]} setSelectedRepos={mockSetSelectedRepos} />)
    expect(mockedAxios.get).toHaveBeenCalledWith('/api/repos/')
  })

  it('applies correct CSS classes', async () => {
    render(<RepoList selectedRepos={[]} setSelectedRepos={mockSetSelectedRepos} />)

    await waitFor(() => {
      const container = screen.getByRole('heading', { name: /select repositories/i }).closest('.repo-list')
      expect(container).toBeInTheDocument()
    })
  })
})