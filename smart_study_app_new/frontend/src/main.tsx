import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import './index.css'
import { Toaster } from 'sonner'
import { ThemeProvider } from '@/components/theme/ThemeProvider'
import ErrorBoundary from '@/components/common/ErrorBoundary'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ThemeProvider>
      <BrowserRouter>
        <ErrorBoundary>
          <App />
        </ErrorBoundary>
        <Toaster richColors position="top-right" />
      </BrowserRouter>
    </ThemeProvider>
  </React.StrictMode>
)
