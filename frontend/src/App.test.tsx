import { describe, expect, it } from 'vitest'
import { render, screen, within } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import App from './App'

describe('App routing', () => {
  it.each([
    ['/', 'Chat'],
    ['/dashboard', 'Dashboard'],
    ['/settings', 'Configurações'],
  ])('renders the page content for %s', (path, expectedText) => {
    render(
      <MemoryRouter initialEntries={[path]}>
        <App />
      </MemoryRouter>,
    )
    const pageContent = screen.getByTestId('page-content')
    expect(within(pageContent).getByText(expectedText)).toBeInTheDocument()
  })

  it('renders the three sidebar nav links (Logs & Testes are embedded, not routed)', () => {
    render(
      <MemoryRouter initialEntries={['/']}>
        <App />
      </MemoryRouter>,
    )
    for (const label of ['Chat', 'Dashboard', 'Configurações']) {
      expect(screen.getByRole('link', { name: new RegExp(label) })).toBeInTheDocument()
    }
    expect(screen.queryByRole('link', { name: /Logs & Observabilidade/ })).not.toBeInTheDocument()
    expect(screen.queryByRole('link', { name: /^Testes$/ })).not.toBeInTheDocument()
  })
})
