import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import Login from './Login'

// Mock window.location
const mockLocation = {
  href: ''
}
Object.defineProperty(window, 'location', {
  value: mockLocation,
  writable: true
})

describe('Login', () => {
  beforeEach(() => {
    mockLocation.href = ''
  })

  it('renders login button with correct text', () => {
    render(<Login />)
    expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument()
  })

  it('renders login heading', () => {
    render(<Login />)
    expect(screen.getByRole('heading', { name: /login with github/i })).toBeInTheDocument()
  })

  it('redirects to GitHub OAuth URL when login button is clicked', () => {
    render(<Login />)

    const loginButton = screen.getByRole('button', { name: /login/i })
    fireEvent.click(loginButton)

    expect(window.location.href).toBe('/api/auth/github/login/')
  })

  it('has proper button accessibility', () => {
    render(<Login />)

    const loginButton = screen.getByRole('button', { name: /login/i })
    expect(loginButton).toBeEnabled()

    // Check that the button is inside the login container
    const loginContainer = loginButton.closest('.login')
    expect(loginContainer).toBeInTheDocument()
  })
})