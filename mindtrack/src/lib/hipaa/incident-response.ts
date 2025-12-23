/**
 * Security Incident Response System
 * HIPAA Requirement: §164.308(a)(6) - Security Incident Procedures
 */

import { createClient } from "@/utils/supabase/server";
import { logDataAccess, logDataModification } from "./audit-log";
import { sendEmail } from "@/lib/email";
import { isAdmin } from "./access-control";

export type IncidentSeverity = "low" | "medium" | "high" | "critical";
export type IncidentStatus = "detected" | "assigned" | "investigating" | "contained" | "resolved" | "closed";
export type IncidentType = 
  | "unauthorized_access"
  | "data_breach"
  | "malware"
  | "phishing"
  | "ddos"
  | "insider_threat"
  | "physical_security"
  | "other";

export interface SecurityIncident {
  id: string;
  type: IncidentType;
  severity: IncidentSeverity;
  title: string;
  description: string;
  detectedAt: string;
  detectedBy: string;
  assignedTo?: string;
  status: IncidentStatus;
  affectedSystems?: string[];
  affectedUsers?: string[];
  impact?: string;
  rootCause?: string;
  remediation?: string;
  lessonsLearned?: string;
  resolvedAt?: string;
  closedAt?: string;
  metadata?: Record<string, unknown>;
}

export interface IncidentResponse {
  incidentId: string;
  responseActions: string[];
  containmentActions: string[];
  eradicationActions: string[];
  recoveryActions: string[];
  postIncidentActions: string[];
}

/**
 * Create security incident
 */
export async function createSecurityIncident(
  incident: Omit<SecurityIncident, "id" | "detectedAt" | "status">,
  detectedBy: string
): Promise<{ success: boolean; incidentId?: string; error?: string }> {
  try {
    const supabase = await createClient();

    const { data, error } = await supabase
      .from("security_incidents")
      .insert({
        incident_type: incident.type,
        severity: incident.severity,
        title: incident.title,
        description: incident.description,
        detected_by: detectedBy,
        status: "detected",
        affected_systems: incident.affectedSystems || null,
        affected_users: incident.affectedUsers || null,
        impact: incident.impact || null,
        metadata: incident.metadata || null,
      })
      .select("id")
      .single();

    if (error) {
      throw new Error(`Failed to create security incident: ${error.message}`);
    }

    // Log incident creation
    await logDataModification(
      detectedBy,
      "create",
      "security_incident",
      data.id,
      undefined,
      undefined,
      true,
      {
        type: incident.type,
        severity: incident.severity,
      }
    );

    // Auto-assign based on severity
    if (incident.severity === "critical" || incident.severity === "high") {
      // Notify admins immediately
      await notifyIncidentStakeholders(data.id, incident.severity);
    }

    return {
      success: true,
      incidentId: data.id,
    };
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : "Unknown error";
    console.error("Create security incident error:", error);
    return {
      success: false,
      error: errorMessage,
    };
  }
}

/**
 * Assign incident to responder
 */
export async function assignIncident(
  incidentId: string,
  assignedTo: string,
  assignedBy: string
): Promise<{ success: boolean; error?: string }> {
  try {
    const supabase = await createClient();

    const { error } = await supabase
      .from("security_incidents")
      .update({
        assigned_to: assignedTo,
        status: "assigned",
        assigned_at: new Date().toISOString(),
      })
      .eq("id", incidentId);

    if (error) {
      throw new Error(`Failed to assign incident: ${error.message}`);
    }

    // Log assignment
    await logDataModification(
      assignedBy,
      "update",
      "incident_assign",
      incidentId,
      undefined,
      undefined,
      true,
      {
        assignedTo,
      }
    );

    return { success: true };
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : "Unknown error";
    console.error("Assign incident error:", error);
    return {
      success: false,
      error: errorMessage,
    };
  }
}

/**
 * Update incident status
 */
export async function updateIncidentStatus(
  incidentId: string,
  status: IncidentStatus,
  updatedBy: string,
  notes?: string
): Promise<{ success: boolean; error?: string }> {
  try {
    const supabase = await createClient();

    const updateData: Record<string, unknown> = {
      status,
      updated_by: updatedBy,
      updated_at: new Date().toISOString(),
    };

    if (status === "resolved") {
      updateData.resolved_at = new Date().toISOString();
    } else if (status === "closed") {
      updateData.closed_at = new Date().toISOString();
    }

    if (notes) {
      updateData.status_notes = notes;
    }

    const { error } = await supabase
      .from("security_incidents")
      .update(updateData)
      .eq("id", incidentId);

    if (error) {
      throw new Error(`Failed to update incident status: ${error.message}`);
    }

    // Log status update
    await logDataModification(
      updatedBy,
      "update",
      "incident_status",
      incidentId,
      undefined,
      undefined,
      true,
      {
        status,
        notes,
      }
    );

    return { success: true };
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : "Unknown error";
    console.error("Update incident status error:", error);
    return {
      success: false,
      error: errorMessage,
    };
  }
}

/**
 * Add incident response actions
 */
export async function addIncidentResponse(
  incidentId: string,
  response: IncidentResponse,
  addedBy: string
): Promise<{ success: boolean; error?: string }> {
  try {
    const supabase = await createClient();

    const { error } = await supabase
      .from("incident_responses")
      .insert({
        incident_id: incidentId,
        response_actions: response.responseActions,
        containment_actions: response.containmentActions,
        eradication_actions: response.eradicationActions,
        recovery_actions: response.recoveryActions,
        post_incident_actions: response.postIncidentActions,
        created_by: addedBy,
      });

    if (error) {
      throw new Error(`Failed to add incident response: ${error.message}`);
    }

    // Log response addition
    await logDataModification(
      addedBy,
      "create",
      "incident_response",
      incidentId,
      undefined,
      undefined,
      true,
      {
        responseActions: response.responseActions.length,
      }
    );

    return { success: true };
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : "Unknown error";
    console.error("Add incident response error:", error);
    return {
      success: false,
      error: errorMessage,
    };
  }
}

/**
 * Update incident with root cause and remediation
 */
export async function updateIncidentResolution(
  incidentId: string,
  rootCause: string,
  remediation: string,
  lessonsLearned?: string,
  updatedBy?: string
): Promise<{ success: boolean; error?: string }> {
  try {
    const supabase = await createClient();

    const { error } = await supabase
      .from("security_incidents")
      .update({
        root_cause: rootCause,
        remediation: remediation,
        lessons_learned: lessonsLearned || null,
        resolved_at: new Date().toISOString(),
        status: "resolved",
        updated_by: updatedBy || null,
      })
      .eq("id", incidentId);

    if (error) {
      throw new Error(`Failed to update incident resolution: ${error.message}`);
    }

    // Log resolution
    if (updatedBy) {
      await logDataModification(
        updatedBy,
        "update",
        "incident_resolution",
        incidentId,
        undefined,
        undefined,
        true,
        {
          rootCause,
          remediation,
        }
      );
    }

    return { success: true };
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : "Unknown error";
    console.error("Update incident resolution error:", error);
    return {
      success: false,
      error: errorMessage,
    };
  }
}

/**
 * Get incident by ID
 */
export async function getIncident(incidentId: string): Promise<SecurityIncident | null> {
  try {
    const supabase = await createClient();

    const { data, error } = await supabase
      .from("security_incidents")
      .select("*")
      .eq("id", incidentId)
      .single();

    if (error || !data) {
      return null;
    }

    return {
      id: data.id,
      type: data.incident_type as IncidentType,
      severity: data.severity as IncidentSeverity,
      title: data.title,
      description: data.description,
      detectedAt: data.detected_at,
      detectedBy: data.detected_by,
      assignedTo: data.assigned_to || undefined,
      status: data.status as IncidentStatus,
      affectedSystems: data.affected_systems || undefined,
      affectedUsers: data.affected_users || undefined,
      impact: data.impact || undefined,
      rootCause: data.root_cause || undefined,
      remediation: data.remediation || undefined,
      lessonsLearned: data.lessons_learned || undefined,
      resolvedAt: data.resolved_at || undefined,
      closedAt: data.closed_at || undefined,
      metadata: data.metadata as Record<string, unknown> | undefined,
    };
  } catch (error) {
    console.error("Get incident error:", error);
    return null;
  }
}

/**
 * Get incidents (with filters)
 */
export async function getIncidents(
  filters?: {
    status?: IncidentStatus;
    severity?: IncidentSeverity;
    type?: IncidentType;
    assignedTo?: string;
  }
): Promise<SecurityIncident[]> {
  try {
    const supabase = await createClient();

    let query = supabase.from("security_incidents").select("*");

    if (filters?.status) {
      query = query.eq("status", filters.status);
    }
    if (filters?.severity) {
      query = query.eq("severity", filters.severity);
    }
    if (filters?.type) {
      query = query.eq("incident_type", filters.type);
    }
    if (filters?.assignedTo) {
      query = query.eq("assigned_to", filters.assignedTo);
    }

    const { data, error } = await query.order("detected_at", { ascending: false });

    if (error) {
      console.error("Get incidents error:", error);
      return [];
    }

    return (data || []).map((incident) => ({
      id: incident.id,
      type: incident.incident_type as IncidentType,
      severity: incident.severity as IncidentSeverity,
      title: incident.title,
      description: incident.description,
      detectedAt: incident.detected_at,
      detectedBy: incident.detected_by,
      assignedTo: incident.assigned_to || undefined,
      status: incident.status as IncidentStatus,
      affectedSystems: incident.affected_systems || undefined,
      affectedUsers: incident.affected_users || undefined,
      impact: incident.impact || undefined,
      rootCause: incident.root_cause || undefined,
      remediation: incident.remediation || undefined,
      lessonsLearned: incident.lessons_learned || undefined,
      resolvedAt: incident.resolved_at || undefined,
      closedAt: incident.closed_at || undefined,
      metadata: incident.metadata as Record<string, unknown> | undefined,
    }));
  } catch (error) {
    console.error("Get incidents error:", error);
    return [];
  }
}

/**
 * Notify incident stakeholders
 */
async function notifyIncidentStakeholders(
  incidentId: string,
  severity: IncidentSeverity
): Promise<void> {
  try {
    const supabase = await createClient();

    // Get admin emails
    const { data: admins } = await supabase
      .from("profiles")
      .select("email")
      .eq("role", "admin");

    if (!admins || admins.length === 0) {
      return;
    }

    const adminEmails = admins.map((admin) => admin.email).filter(Boolean) as string[];

    // Send notification email
    await sendEmail({
      to: adminEmails,
      subject: `🚨 Security Incident Alert - ${severity.toUpperCase()}`,
      html: `
        <div style="font-family: Arial, sans-serif; padding: 20px;">
          <h2 style="color: #dc2626;">Security Incident Detected</h2>
          <p><strong>Severity:</strong> ${severity.toUpperCase()}</p>
          <p><strong>Incident ID:</strong> ${incidentId}</p>
          <p>Please review and respond to this incident immediately.</p>
          <p><a href="${process.env.NEXT_PUBLIC_APP_URL}/dashboard/incidents/${incidentId}">View Incident</a></p>
        </div>
      `,
      text: `Security Incident Alert - ${severity.toUpperCase()}\n\nIncident ID: ${incidentId}\n\nPlease review and respond immediately.`,
    });
  } catch (error) {
    console.error("Notify incident stakeholders error:", error);
  }
}

/**
 * Escalate incident
 */
export async function escalateIncident(
  incidentId: string,
  escalatedBy: string,
  reason: string
): Promise<{ success: boolean; error?: string }> {
  try {
    const supabase = await createClient();

    // Get incident
    const incident = await getIncident(incidentId);
    if (!incident) {
      return {
        success: false,
        error: "Incident not found",
      };
    }

    // Increase severity if not already critical
    let newSeverity: IncidentSeverity = incident.severity;
    if (incident.severity === "low") {
      newSeverity = "medium";
    } else if (incident.severity === "medium") {
      newSeverity = "high";
    } else if (incident.severity === "high") {
      newSeverity = "critical";
    }

    const { error } = await supabase
      .from("security_incidents")
      .update({
        severity: newSeverity,
        escalation_reason: reason,
        escalated_at: new Date().toISOString(),
        escalated_by: escalatedBy,
      })
      .eq("id", incidentId);

    if (error) {
      throw new Error(`Failed to escalate incident: ${error.message}`);
    }

    // Notify stakeholders
    await notifyIncidentStakeholders(incidentId, newSeverity);

    // Log escalation
    await logDataModification(
      escalatedBy,
      "update",
      "incident_escalate",
      incidentId,
      undefined,
      undefined,
      true,
      {
        reason,
        newSeverity,
      }
    );

    return { success: true };
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : "Unknown error";
    console.error("Escalate incident error:", error);
    return {
      success: false,
      error: errorMessage,
    };
  }
}





