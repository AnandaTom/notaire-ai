import { NextRequest, NextResponse } from 'next/server'

/**
 * Proxy vers le backend Modal (FastAPI).
 *
 * Remplace l'appel direct Anthropic par un proxy qui route tout
 * vers le /chat endpoint de Modal, ou l'agent LLM (Anthropic + 9 tools)
 * gere la conversation intelligemment.
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://notomai--notaire-ai-fastapi-app.modal.run'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    }

    // Forward API key si configuree
    const apiKey = process.env.NEXT_PUBLIC_API_KEY
    if (apiKey) {
      headers['X-API-Key'] = apiKey
    }

    const response = await fetch(`${API_URL}/chat/`, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        message: body.message || body.messages?.[body.messages.length - 1]?.content || '',
        conversation_id: body.conversation_id,
        history: body.messages || body.history || [],
        context: { format: body.format || 'docx' },
        user_id: body.user_id || '',
        etude_id: body.etude_id || '',
      }),
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Erreur serveur' }))
      return NextResponse.json(error, { status: response.status })
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('Proxy error:', error)
    return NextResponse.json(
      { content: 'Erreur de communication avec le serveur. Veuillez reessayer.', suggestions: [] },
      { status: 502 }
    )
  }
}
