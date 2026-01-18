import Anthropic from '@anthropic-ai/sdk'
import { NextRequest, NextResponse } from 'next/server'

const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
})

const SYSTEM_PROMPT = `Tu es NotaireAI, un assistant juridique spécialisé dans la création et la modification d'actes notariaux pour l'étude de Maître Charlotte Diaz.

## Ton rôle
Tu assistes les notaires dans la rédaction d'actes de vente et de promesses de vente de lots de copropriété, conformément au droit français.

## Principes de fonctionnement
1. **Collecte progressive** : Pose des questions une par une pour collecter les informations nécessaires
2. **Validation** : Vérifie toujours la cohérence des données (quotités = 100%, dates logiques, etc.)
3. **Références légales** : Cite les articles de loi pertinents (Code civil, CCH, etc.)
4. **Format** : L'utilisateur a choisi le format d'export (PDF ou DOCX)

## Sections d'un acte de vente
1. Identification des parties (vendeurs, acquéreurs)
2. Situation matrimoniale
3. Désignation du bien (lots, tantièmes, cadastre)
4. Origine de propriété
5. Prix et paiement
6. Prêts (si financement)
7. Diagnostics techniques
8. Charges et conditions

## Style de communication
- Professionnel mais accessible
- Précis et structuré
- Toujours en français
- Utilise le vouvoiement

## Format de réponse
Quand tu poses des questions, indique la section en cours entre crochets, ex: [Identification du vendeur]
`

export async function POST(request: NextRequest) {
  try {
    const { messages, format } = await request.json()

    const response = await anthropic.messages.create({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 2048,
      system: SYSTEM_PROMPT + `\n\nFormat d'export choisi par l'utilisateur: ${format.toUpperCase()}`,
      messages: messages.map((m: { role: string; content: string }) => ({
        role: m.role as 'user' | 'assistant',
        content: m.content,
      })),
    })

    const content = response.content[0]
    if (content.type !== 'text') {
      throw new Error('Unexpected response type')
    }

    // Extract section from response if present
    const sectionMatch = content.text.match(/\[([^\]]+)\]/)
    const section = sectionMatch ? sectionMatch[1] : undefined

    // Remove section tag from content
    const cleanContent = content.text.replace(/\[[^\]]+\]\s*/, '')

    return NextResponse.json({
      content: cleanContent,
      section,
    })
  } catch (error) {
    console.error('Error:', error)
    return NextResponse.json(
      { error: 'Erreur de communication avec l\'assistant' },
      { status: 500 }
    )
  }
}
