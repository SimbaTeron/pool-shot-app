import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.EXPO_PUBLIC_SUPABASE_URL || '';
const supabaseAnonKey = process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY || '';

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

export type SubscriptionTier = 'free' | 'pro' | 'pool_hall';

export interface UserProfile {
  id: string;
  email: string;
  subscription_tier: SubscriptionTier;
  shots_used_today: number;
  created_at: string;
}
