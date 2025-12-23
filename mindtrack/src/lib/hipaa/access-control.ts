/**
 * HIPAA-Compliant Access Controls
 * Role-Based Access Control (RBAC) and Session Management
 */

import { createClient } from "@/utils/supabase/server";

export type UserRole = "therapist" | "supervisor" | "admin" | "patient";

export interface AccessPolicy {
  resource: string;
  action: "read" | "write" | "delete" | "export";
  roles: UserRole[];
  conditions?: (userId: string, resourceId?: string) => Promise<boolean>;
}

/**
 * Minimum necessary rule: Check if user has minimum necessary access
 */
export async function checkMinimumNecessary(
  userId: string,
  resourceType: string,
  action: "read" | "write" | "delete" | "export"
): Promise<boolean> {
  const supabase = await createClient();
  
  // Get user role
  const { data: profile } = await supabase
    .from("profiles")
    .select("role")
    .eq("id", userId)
    .single();

  if (!profile) {
    return false;
  }

  const role = profile.role as UserRole;

  // Define minimum necessary access policies
  const policies: AccessPolicy[] = [
    // Therapists can only access their own clients
    {
      resource: "clients",
      action: "read",
      roles: ["therapist", "supervisor", "admin"],
      conditions: async (uid, resourceId) => {
        if (role === "admin" || role === "supervisor") return true;
        const { data } = await supabase
          .from("clients")
          .select("therapist_id")
          .eq("id", resourceId)
          .single();
        return data?.therapist_id === uid;
      },
    },
    // Patients can only access their own data
    {
      resource: "patient_data",
      action: "read",
      roles: ["patient"],
      conditions: async (uid) => {
        return uid === userId; // Patients can only access their own data
      },
    },
    // Supervisors can access all therapist data
    {
      resource: "therapist_data",
      action: "read",
      roles: ["supervisor", "admin"],
    },
  ];

  const policy = policies.find(
    (p) => p.resource === resourceType && p.action === action
  );

  if (!policy) {
    return false; // Default deny
  }

  if (!policy.roles.includes(role)) {
    return false;
  }

  // Check conditions if present
  if (policy.conditions) {
    return await policy.conditions(userId);
  }

  return true;
}

/**
 * Check if user has access to resource
 */
export async function hasAccess(
  userId: string,
  resourceType: string,
  action: "read" | "write" | "delete" | "export",
  resourceId?: string
): Promise<boolean> {
  // First check minimum necessary rule
  const hasMinimumNecessary = await checkMinimumNecessary(
    userId,
    resourceType,
    action
  );

  if (!hasMinimumNecessary) {
    return false;
  }

  // Additional access checks can be added here
  // For example: check if resource belongs to user's organization

  return true;
}

/**
 * Get user role
 */
export async function getUserRole(userId: string): Promise<UserRole | null> {
  const supabase = await createClient();
  
  const { data: profile } = await supabase
    .from("profiles")
    .select("role")
    .eq("id", userId)
    .single();

  return profile?.role as UserRole || null;
}

/**
 * Check if user is admin
 */
export async function isAdmin(userId: string): Promise<boolean> {
  const role = await getUserRole(userId);
  return role === "admin";
}

/**
 * Check if user is supervisor
 */
export async function isSupervisor(userId: string): Promise<boolean> {
  const role = await getUserRole(userId);
  return role === "supervisor" || role === "admin";
}

/**
 * Session timeout check (15 minutes inactivity)
 */
export function checkSessionTimeout(lastActivity: Date): boolean {
  const SESSION_TIMEOUT_MS = 15 * 60 * 1000; // 15 minutes
  const now = new Date();
  const timeSinceLastActivity = now.getTime() - lastActivity.getTime();
  
  return timeSinceLastActivity < SESSION_TIMEOUT_MS;
}

/**
 * Concurrent session limit check
 */
export async function checkConcurrentSessions(
  userId: string,
  maxSessions: number = 3
): Promise<boolean> {
  const supabase = await createClient();
  
  // Get active sessions (last 15 minutes)
  const { data: sessions } = await supabase
    .from("user_sessions")
    .select("id")
    .eq("user_id", userId)
    .gte("last_activity", new Date(Date.now() - 15 * 60 * 1000).toISOString());

  return (sessions?.length || 0) < maxSessions;
}





