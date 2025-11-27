import { describe, it, expect } from 'vitest'
import { render } from '@testing-library/react'
import PDFViewer from './PDFViewer'

// Smoke test: renders container without crashing (document load mocked by react-pdf)
describe('PDFViewer', () => {
  it('renders without crashing', () => {
    const { container } = render(<PDFViewer url="/uploads/sample.pdf" />)
    expect(container).toBeTruthy()
  })
})
