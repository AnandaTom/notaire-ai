import { supabase } from '@/lib/supabase'

/**
 * Recupere l'etude_id du notaire connecte via Supabase Auth.
 * Utilisee par les pages dossiers et clients pour filtrer par etude.
 */
export async function getUserEtudeId(): Promise<string | null> {
  try {
    const { data: { user } } = await supabase.auth.getUser()
    if (!user) return null

    const { data } = await supabase
      .from('notaire_users')
      .select('etude_id')
      .eq('auth_user_id', user.id)
      .single()

    return data?.etude_id ?? null
  } catch {
    return null
  }
}
