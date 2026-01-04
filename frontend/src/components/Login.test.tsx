import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import Login from './Login'

describe('Login', () => {
  it('renders login button', () => {
    render(<Login />)
    expect(screen.getByText('Login')).toBeInTheDocument()
  })
})