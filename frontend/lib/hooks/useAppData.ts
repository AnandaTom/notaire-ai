'use client'

import { useState, useEffect, useCallback } from 'react'
import { supabase } from '@/lib/supabase'
import {
  loadConversations as apiLoadConversations,
  loadConversation as apiLoadConversation,
} from '@/lib/api'
import type { ConversationSummary, Message } from '@/types'

interface UserInfo {
  nom: string
  prenom: string
}

interface AppData {
  userId: string
  etudeId: string
  userInfo: UserInfo | null
  conversations: ConversationSummary[]
  activeConversationId: string
  loadConversations: () => Promise<void>
  loadConversation: (convId: string) => Promise<{
    messages: { role: string; content: string; suggestions?: string[] }[]
    context?: { progress_pct?: number }
  } | null>
  selectConversation: (convId: string) => void
  startNewConversation: () => string
}

function getOrCreateUserId(): string {
  if (typeof window === 'undefined') return ''
  let userId = localStorage.getItem('notaire_user_id')
  if (!userId) {
    userId = crypto.randomUUID()
    localStorage.setItem('notaire_user_id', userId)
  }
  return userId
}

export function useAppData(): AppData {
  const [userId, setUserId] = useState('')
  const [etudeId, setEtudeId] = useState('')
  const [userInfo, setUserInfo] = useState<UserInfo | null>(null)
  const [conversations, setConversations] = useState<ConversationSummary[]>([])
  const [activeConversationId, setActiveConversationId] = useState('')

  // Init: load userId + conversationId from localStorage + user info
  useEffect(() => {
    const uid = getOrCreateUserId()
    setUserId(uid)

    const savedConvId = localStorage.getItem('notaire_active_conversation')
    if (savedConvId) {
      setActiveConversationId(savedConvId)
    } else {
      const newId = crypto.randomUUID()
      setActiveConversationId(newId)
      localStorage.setItem('notaire_active_conversation', newId)
    }

    loadConversationsInternal()

    // Charger les infos utilisateur depuis Supabase
    const loadUserInfo = async () => {
      const { data: { user } } = await supabase.auth.getUser()
      if (user) {
        setUserId(user.id)
        const { data } = await supabase
          .from('notaire_users')
          .select('nom, prenom, etude_id')
          .eq('auth_user_id', user.id)
          .single()
        if (data) {
          setUserInfo(data)
          if (data.etude_id) setEtudeId(data.etude_id)
        }
      }
    }
    loadUserInfo()
  }, [])

  const loadConversationsInternal = async () => {
    try {
      const data = await apiLoadConversations()
      setConversations(data.conversations || [])
    } catch {
      // Silently fail — toast will be handled by caller if needed
    }
  }

  const loadConversations = useCallback(async () => {
    await loadConversationsInternal()
  }, [])

  const loadConversation = useCallback(async (convId: string) => {
    try {
      return await apiLoadConversation(convId)
    } catch {
      return null
    }
  }, [])

  const selectConversation = useCallback((convId: string) => {
    setActiveConversationId(convId)
    localStorage.setItem('notaire_active_conversation', convId)
  }, [])

  const startNewConversation = useCallback(() => {
    const newId = crypto.randomUUID()
    setActiveConversationId(newId)
    localStorage.setItem('notaire_active_conversation', newId)
    return newId
  }, [])

  return {
    userId,
    etudeId,
    userInfo,
    conversations,
    activeConversationId,
    loadConversations,
    loadConversation,
    selectConversation,
    startNewConversation,
  }
}
