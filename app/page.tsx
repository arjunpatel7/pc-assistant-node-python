'use client'

import { useState, useEffect, FormEvent } from 'react'
import Image from 'next/image'

interface Message {
  role: 'user' | 'assistant'
  content: string
}

export default function Home() {
  const [loading, setLoading] = useState(true)
  const [assistantExists, setAssistantExists] = useState(false)
  const [error, setError] = useState('')
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')

  useEffect(() => {
    checkAssistant()
  }, [])

  const checkAssistant = async () => {
    try {
      const response = await fetch('/api/check_assistant')
      const data = await response.json()
      
      setLoading(false)
      setAssistantExists(data.exists)
      if (!data.exists) {
        setError('Please create an Assistant')
      }
    } catch (error) {
      setLoading(false)
      setError('Error connecting to the Assistant')
    }
  }

  const sendMessage = async (e: FormEvent) => {
    e.preventDefault()
    if (!input.trim()) return

    const newMessage: Message = { role: 'user', content: input }
    setMessages([...messages, newMessage])
    setInput('')

    // TODO: Implement API call to send message to assistant
    // For now, we'll just simulate a response
    setTimeout(() => {
      const assistantMessage: Message = { role: 'assistant', content: 'This is a simulated response.' }
      setMessages(prevMessages => [...prevMessages, assistantMessage])
    }, 1000)
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      {loading ? (
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mb-4"></div>
          <p>Connecting to your Assistant...</p>
        </div>
      ) : assistantExists ? (
        <div className="w-full max-w-2xl">
          <h1 className="text-2xl font-bold mb-4">Chat with Assistant</h1>
          <div className="bg-gray-100 p-4 rounded-lg mb-4 h-96 overflow-y-auto">
            {messages.map((message, index) => (
              <div key={index} className={`mb-2 ${message.role === 'user' ? 'text-right' : 'text-left'}`}>
                <span className={`inline-block p-2 rounded-lg ${message.role === 'user' ? 'bg-blue-500 text-white' : 'bg-gray-300'}`}>
                  {message.content}
                </span>
              </div>
            ))}
          </div>
          <form onSubmit={sendMessage} className="flex">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              className="flex-grow p-2 border rounded-l-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Type your message..."
            />
            <button
              type="submit"
              className="bg-blue-500 text-white p-2 rounded-r-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              Send
            </button>
          </form>
        </div>
      ) : (
        <div className="text-center text-red-500">
          <p>{error}</p>
        </div>
      )}
    </main>
  )
}
