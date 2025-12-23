import { createSupabaseServerClient } from '@/lib/supabaseClient';
import { ROLE_DEFINITIONS, type Permission, type UserRole } from '@/types/auth';

export async function getCurrentUserRole(): Promise<UserRole | null> {
  const supabase = await createSupabaseServerClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return null;
  // Basit yaklaşım: kullanıcı metadata.role veya clinic_members.role
  const roleMeta = (user.user_metadata as any)?.role as UserRole | undefined;
  if (roleMeta) return roleMeta;
  const { data: cm } = await supabase
    .from('clinic_members')
    .select('role')
    .eq('user_id', user.id)
    .eq('status', 'active')
    .maybeSingle();
  return (cm?.role as UserRole) || 'clinician';
}

export function roleHasPermission(role: UserRole, permission: Permission): boolean {
  const def = ROLE_DEFINITIONS.find(r => r.role === role);
  return !!def?.permissions.includes(permission);
}

export async function requirePermission(permission: Permission) {
  const role = await getCurrentUserRole();
  if (!role || !roleHasPermission(role, permission)) {
    throw new Error('forbidden');
  }
}



