// T035: useAuth hook for easy auth state access

'use client';

import { useAuthContext } from '@/lib/auth';

export function useAuth() {
  return useAuthContext();
}
