import { supabase, type SubscriptionTier } from './supabase';
import type { UserProfile } from './supabase';

// --- Auth Operations ---

export async function signUp(email: string, password: string): Promise<{ user: any; error: string | null }> {
  const { data, error } = await supabase.auth.signUp({ email, password });
  if (error) return { user: null, error: error.message };

  // Create user profile row
  if (data.user) {
    await supabase.from('profiles').upsert({
      id: data.user.id,
      email,
      subscription_tier: 'free',
      shots_used_today: 0,
    });
  }

  return { user: data.user, error: null };
}

export async function signIn(email: string, password: string): Promise<{ user: any; error: string | null }> {
  const { data, error } = await supabase.auth.signInWithPassword({ email, password });
  if (error) return { user: null, error: error.message };
  return { user: data.user, error: null };
}

export async function signOut(): Promise<void> {
  await supabase.auth.signOut();
}

export async function getCurrentUser(): Promise<any> {
  const { data } = await supabase.auth.getUser();
  return data?.user ?? null;
}

export async function getSession(): Promise<any> {
  const { data } = await supabase.auth.getSession();
  return data?.session ?? null;
}

// --- Profile Operations ---

export async function getProfile(userId: string): Promise<{ profile: UserProfile | null; error: string | null }> {
  const { data, error } = await supabase
    .from('profiles')
    .select('*')
    .eq('id', userId)
    .single();

  if (error) return { profile: null, error: error.message };
  return { profile: data as UserProfile, error: null };
}

export async function updateProfile(userId: string, updates: Partial<UserProfile>): Promise<{ error: string | null }> {
  const { error } = await supabase
    .from('profiles')
    .update(updates)
    .eq('id', userId);

  return { error: error?.message ?? null };
}

// --- Shot Quota (Free tier = 3/day) ---

const FREE_DAILY_LIMIT = 3;

export function isQuotaExceeded(profile: UserProfile | null): boolean {
  if (!profile) return true; // not logged in
  if (profile.subscription_tier !== 'free') return false;
  return profile.shots_used_today >= FREE_DAILY_LIMIT;
}

export function getQuotaRemaining(profile: UserProfile | null): number {
  if (!profile) return 0;
  if (profile.subscription_tier !== 'free') return Infinity;
  return Math.max(0, FREE_DAILY_LIMIT - profile.shots_used_today);
}

export async function incrementShotCount(userId: string): Promise<void> {
  const { data } = await supabase
    .from('profiles')
    .select('shots_used_today')
    .eq('id', userId)
    .single();

  await supabase
    .from('profiles')
    .update({ shots_used_today: (data?.shots_used_today ?? 0) + 1 })
    .eq('id', userId);
}
