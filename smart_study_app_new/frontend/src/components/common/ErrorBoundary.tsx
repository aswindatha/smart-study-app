import React from 'react'
import { toast } from 'sonner'

type State = { hasError: boolean }

export default class ErrorBoundary extends React.Component<{ children: React.ReactNode }, State> {
  state: State = { hasError: false }

  static getDerivedStateFromError() {
    return { hasError: true }
  }

  componentDidCatch(error: any) {
    console.error('UI Error:', error)
    toast.error('Something went wrong. Please try again.')
  }

  render() {
    if (this.state.hasError) {
      return <div className="p-6 text-sm text-red-600">An unexpected error occurred.</div>
    }
    return this.props.children
  }
}
