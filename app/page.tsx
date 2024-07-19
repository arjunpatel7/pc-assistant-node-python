'use client'

import { useState, useEffect, FormEvent, useRef } from 'react'
import AssistantFiles from './components/AssistantFiles'

interface Reference {
  name: string;
  url: string;
}

interface Message {
  role: 'user' | 'assistant'
  content: string
  references?: Reference[]
}

export default function Home() {
  const [loading, setLoading] = useState(true)
  const [assistantExists, setAssistantExists] = useState(false)
  const [error, setError] = useState('')
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [assistantName, setAssistantName] = useState('')
  const [isStreaming, setIsStreaming] = useState(false)
  const streamRef = useRef<ReadableStreamDefaultReader | null>(null)

  useEffect(() => {
    checkAssistant()
  }, [])

  useEffect(() => {
    return () => {
      if (streamRef.current) {
        streamRef.current.cancel()
      }
    }
  }, [])

  const checkAssistant = async () => {
    try {
      const response = await fetch('/api/check_assistant')
      const data = await response.json()
      
      setLoading(false)
      setAssistantExists(data.exists)
      setAssistantName(data.assistant_name)
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
    if (!input.trim() || isStreaming) return

    const newMessage: Message = { role: 'user', content: input }
    setMessages(prevMessages => [...prevMessages, newMessage])
    setInput('')
    setIsStreaming(true)

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: input,
          history: messages,
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to get response from assistant')
      }

      const reader = response.body?.getReader()
      if (!reader) {
        throw new Error('Failed to get response reader')
      }

      streamRef.current = reader

      let assistantMessage: Message = { role: 'assistant', content: '' }
      setMessages(prevMessages => [...prevMessages, assistantMessage])

      const decoder = new TextDecoder()
      let accumulatedContent = ''
      let references: Reference[] = []

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value)
        const lines = chunk.split('\n')
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const content = line.slice(6)
            if (content === '[DONE]') {
              setIsStreaming(false)
              break
            }
            const parsedContent = JSON.parse(content)
            if (parsedContent.references) {
              references = parsedContent.references
            } else if (!parsedContent.isReference) {
              accumulatedContent += parsedContent.content
              setMessages(prevMessages => {
                const newMessages = [...prevMessages]
                newMessages[newMessages.length - 1] = { role: 'assistant', content: accumulatedContent, references: references }
                return newMessages
              })
            }
          }
        }
      }
    } catch (error) {
      setError('Failed to communicate with the assistant')
      setIsStreaming(false)
    }
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-4 sm:p-8">
      {loading ? (
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mb-4"></div>
          <p>Connecting to your Assistant...</p>
        </div>
      ) : assistantExists ? (
        <div className="w-full max-w-6xl xl:max-w-7xl">
          <h1 className="text-2xl font-bold mb-4">Chat with Pinecone Assistant: {assistantName}</h1>
          <div className="flex flex-col gap-4">
            <div className="w-full">
              <div className="bg-gray-100 p-4 rounded-lg mb-4 h-[calc(100vh-500px)] overflow-y-auto">
                {messages.map((message, index) => (
                  <div key={index} className={`mb-2 ${message.role === 'user' ? 'text-right' : 'text-left'}`}>
                    <span className={`inline-block p-2 rounded-lg ${
                      message.role === 'user' ? 'bg-blue-500 text-white' : 'bg-gray-300'
                    } max-w-[80%] break-words`}>
                      {message.content}
                      {message.references && (
                        <div className="mt-2">
                          <strong>References:</strong>
                          <ul>
                            {message.references.map((ref, i) => (
                              <li key={i}>
                                <a href={ref.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                                  {ref.name}
                                </a>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </span>
                  </div>
                ))}
              </div>
              <form onSubmit={sendMessage} className="flex mb-4">
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
                  disabled={isStreaming}
                >
                  {isStreaming ? 'Streaming...' : 'Send'}
                </button>
              </form>
              {error && (
                <div className="text-red-500 mb-4">
                  <p>{error}</p>
                </div>
              )}
            </div>
            <div className="w-full">
              <AssistantFiles />
            </div>
          </div>
        </div>
      ) : (
        <div className="text-center text-red-500">
          <p>{error}</p>
        </div>
      )}
    </main>
  )
}
