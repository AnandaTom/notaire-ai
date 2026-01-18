'use client'

import { useState } from 'react'
import Sidebar from '@/components/Sidebar'
import ChatArea from '@/components/ChatArea'
import Header from '@/components/Header'

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  section?: string
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: `Bonjour Maître Diaz,

Je suis votre assistant pour la rédaction d'actes notariaux. Je vous accompagne dans la création d'actes de vente et de promesses de vente conformes aux dispositions légales en vigueur.

Comment puis-je vous assister aujourd'hui ?`,
      timestamp: new Date(),
    },
  ])
  const [isLoading, setIsLoading] = useState(false)
  const [selectedFormat, setSelectedFormat] = useState<'pdf' | 'docx'>('pdf')

  const sendMessage = async (content: string) => {
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setIsLoading(true)

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: [...messages, userMessage].map((m) => ({
            role: m.role,
            content: m.content,
          })),
          format: selectedFormat,
        }),
      })

      if (!response.ok) throw new Error('Erreur de communication')

      const data = await response.json()

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.content,
        timestamp: new Date(),
        section: data.section,
      }

      setMessages((prev) => [...prev, assistantMessage])
    } catch (error) {
      console.error('Erreur:', error)
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Désolé, une erreur est survenue. Veuillez réessayer.',
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex items-center justify-center min-h-screen p-5">
      <div className="w-full max-w-[1100px] h-[92vh] max-h-[850px] bg-ivory rounded-[20px] shadow-lg grid grid-cols-[280px_1fr] overflow-hidden border border-gold/10">
        <Sidebar />
        <main className="flex flex-col bg-ivory">
          <Header />
          <ChatArea
            messages={messages}
            isLoading={isLoading}
            onSendMessage={sendMessage}
            selectedFormat={selectedFormat}
            onFormatChange={setSelectedFormat}
          />
        </main>
      </div>
    </div>
  )
}
