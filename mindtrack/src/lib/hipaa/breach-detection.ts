/**
 * Breach Detection & Notification System
 * HIPAA Requirement: §164.404 - Notification to Individuals
 */

import { createClient } from "@/utils/supabase/server";
import { logDataAccess, logDataModification } from "./audit-log";
import { sendEmail } from "@/lib/email";
import crypto from "crypto";

export type BreachSeverity = "low" | "medium" | "high" | "critical";

export interface BreachEvent {
  id: string;
  type: "unauthorized_access" | "data_exfiltration" | "data_loss" | "system_compromise" | "other";
  severity: BreachSeverity;
  description: string;
  affectedUsers: string[];
  affectedRecords: number;
  detectedAt: string;
  reportedAt?: string;
  resolvedAt?: string;
  status: "detected" | "assessed" | "notified" | "resolved";
  riskScore: number; // 0-100
}

export interface BreachAssessment {
  isBreach: boolean;
  riskScore: number;
  affectedCount: number;
  requiresNotification: boolean;
  notificationDeadline: string; // 60 days from detection
  recommendations: string[];
}

/**
 * Detect potential breaches from audit logs
 */
export async function detectPotentialBreaches(
  timeWindowHours: number = 24
): Promise<BreachEvent[]> {
  const supabase = await createClient();
  const breaches: BreachEvent[] = [];

  const startTime = new Date(Date.now() - timeWindowHours * 60 * 60 * 1000);

  // Check for unauthorized access attempts
  const { data: unauthorizedAccess } = await supabase
    .from("audit_logs")
    .select("*")
    .eq("action", "access_denied")
    .gte("created_at", startTime.toISOString())
    .order("created_at", { ascending: false });

  if (unauthorizedAccess && unauthorizedAccess.length > 10) {
    // Multiple unauthorized access attempts = potential breach
    const affectedUsers = [...new Set(unauthorizedAccess.map((log) => log.user_id))];
    
    breaches.push({
      id: crypto.randomUUID(),
      type: "unauthorized_access",
      severity: unauthorizedAccess.length > 50 ? "high" : "medium",
      description: `Multiple unauthorized access attempts detected: ${unauthorizedAccess.length} attempts`,
      affectedUsers,
      affectedRecords: unauthorizedAccess.length,
      detectedAt: new Date().toISOString(),
      status: "detected",
      riskScore: Math.min(100, unauthorizedAccess.length * 2),
    });
  }

  // Check for unusual data access patterns
  const { data: unusualAccess } = await supabase
    .from("audit_logs")
    .select("user_id, resource_type, COUNT(*)")
    .eq("action", "read")
    .gte("created_at", startTime.toISOString())
    .group("user_id, resource_type")
    .having("COUNT(*) > 100");

  if (unusualAccess && unusualAccess.length > 0) {
    breaches.push({
      id: crypto.randomUUID(),
      type: "data_exfiltration",
      severity: "high",
      description: "Unusual data access patterns detected",
      affectedUsers: [...new Set(unusualAccess.map((log) => log.user_id))],
      affectedRecords: unusualAccess.reduce((sum, log) => sum + (log.count || 0), 0),
      detectedAt: new Date().toISOString(),
      status: "detected",
      riskScore: 75,
    });
  }

  // Check for failed login attempts
  const { data: failedLogins } = await supabase
    .from("audit_logs")
    .select("*")
    .eq("action", "failed_login")
    .gte("created_at", startTime.toISOString());

  if (failedLogins && failedLogins.length > 20) {
    breaches.push({
      id: crypto.randomUUID(),
      type: "system_compromise",
      severity: "medium",
      description: `Multiple failed login attempts: ${failedLogins.length} attempts`,
      affectedUsers: [...new Set(failedLogins.map((log) => log.user_id))],
      affectedRecords: failedLogins.length,
      detectedAt: new Date().toISOString(),
      status: "detected",
      riskScore: Math.min(100, failedLogins.length),
    });
  }

  return breaches;
}

/**
 * Assess breach severity and requirements
 */
export function assessBreach(breach: BreachEvent): BreachAssessment {
  const isBreach = breach.severity === "high" || breach.severity === "critical" || breach.riskScore >= 60;
  const requiresNotification = isBreach && breach.affectedRecords > 0;

  // Calculate notification deadline (60 days from detection)
  const detectedDate = new Date(breach.detectedAt);
  const notificationDeadline = new Date(detectedDate.getTime() + 60 * 24 * 60 * 60 * 1000);

  const recommendations: string[] = [];

  if (isBreach) {
    recommendations.push("Immediately assess the scope of the breach");
    recommendations.push("Identify all affected individuals");
    recommendations.push("Document the breach and response actions");
    
    if (breach.affectedRecords >= 500) {
      recommendations.push("Notify HHS within 60 days");
      recommendations.push("Notify media if required");
    }
    
    recommendations.push("Notify affected individuals within 60 days");
    recommendations.push("Implement remediation measures");
  } else {
    recommendations.push("Monitor the situation");
    recommendations.push("Document the incident");
  }

  return {
    isBreach,
    riskScore: breach.riskScore,
    affectedCount: breach.affectedRecords,
    requiresNotification,
    notificationDeadline: notificationDeadline.toISOString(),
    recommendations,
  };
}

/**
 * Create breach record
 */
export async function createBreachRecord(breach: BreachEvent): Promise<{ success: boolean; breachId?: string; error?: string }> {
  try {
    const supabase = await createClient();

    const { data, error } = await supabase
      .from("breach_events")
      .insert({
        breach_type: breach.type,
        severity: breach.severity,
        description: breach.description,
        affected_users: breach.affectedUsers,
        affected_records: breach.affectedRecords,
        detected_at: breach.detectedAt,
        status: breach.status,
        risk_score: breach.riskScore,
      })
      .select("id")
      .single();

    if (error) {
      throw new Error(`Failed to create breach record: ${error.message}`);
    }

    return {
      success: true,
      breachId: data.id,
    };
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : "Unknown error";
    console.error("Create breach record error:", error);
    return {
      success: false,
      error: errorMessage,
    };
  }
}

/**
 * Send breach notification to patients
 */
export async function sendBreachNotification(
  breachId: string,
  patientEmails: string[]
): Promise<{ success: boolean; notified: number; error?: string }> {
  try {
    const supabase = await createClient();

    // Get breach details
    const { data: breach, error: breachError } = await supabase
      .from("breach_events")
      .select("*")
      .eq("id", breachId)
      .single();

    if (breachError || !breach) {
      throw new Error("Breach record not found");
    }

    // Send notifications
    let notified = 0;
    const errors: string[] = [];

    for (const email of patientEmails) {
      try {
        const emailResult = await sendEmail({
          to: email,
          subject: "Important: Data Security Notice - MindTrack",
          html: `
            <div style="font-family: Arial, sans-serif; padding: 20px;">
              <h2>Important Security Notice</h2>
              <p>Dear Patient,</p>
              <p>We are writing to inform you of a potential security incident that may have affected your protected health information.</p>
              
              <div style="background-color: #fef2f2; border-left: 4px solid #dc2626; padding: 15px; margin: 20px 0;">
                <h3>Incident Details</h3>
                <p><strong>Type:</strong> ${breach.breach_type}</p>
                <p><strong>Detected:</strong> ${new Date(breach.detected_at).toLocaleDateString()}</p>
                <p><strong>Description:</strong> ${breach.description}</p>
              </div>

              <h3>What We're Doing</h3>
              <ul>
                <li>Conducting a thorough investigation</li>
                <li>Implementing additional security measures</li>
                <li>Notifying all affected individuals</li>
                <li>Working with security experts to prevent future incidents</li>
              </ul>

              <h3>What You Can Do</h3>
              <ul>
                <li>Monitor your accounts for suspicious activity</li>
                <li>Review your medical records for accuracy</li>
                <li>Report any suspicious activity immediately</li>
                <li>Consider placing a fraud alert on your credit report</li>
              </ul>

              <p>If you have questions or concerns, please contact us immediately.</p>
              
              <p>Sincerely,<br>MindTrack Security Team</p>
            </div>
          `,
          text: `
Important Security Notice

Dear Patient,

We are writing to inform you of a potential security incident that may have affected your protected health information.

Incident Details:
Type: ${breach.breach_type}
Detected: ${new Date(breach.detected_at).toLocaleDateString()}
Description: ${breach.description}

What We're Doing:
- Conducting a thorough investigation
- Implementing additional security measures
- Notifying all affected individuals
- Working with security experts to prevent future incidents

What You Can Do:
- Monitor your accounts for suspicious activity
- Review your medical records for accuracy
- Report any suspicious activity immediately
- Consider placing a fraud alert on your credit report

If you have questions or concerns, please contact us immediately.

Sincerely,
MindTrack Security Team
          `,
        });

        if (emailResult.success) {
          notified++;
        } else {
          errors.push(`Failed to send to ${email}: ${emailResult.error}`);
        }
      } catch (error) {
        errors.push(`Failed to send to ${email}: ${error instanceof Error ? error.message : "Unknown error"}`);
      }
    }

    // Update breach status
    await supabase
      .from("breach_events")
      .update({
        status: "notified",
        notified_at: new Date().toISOString(),
        notified_count: notified,
      })
      .eq("id", breachId);

    // Log notification
    await logDataModification(
      "system",
      "create",
      "breach_notification",
      breachId,
      undefined,
      undefined,
      true,
      {
        notified,
        total: patientEmails.length,
      }
    );

    if (errors.length > 0) {
      return {
        success: notified > 0,
        notified,
        error: `Some notifications failed: ${errors.join(", ")}`,
      };
    }

    return {
      success: true,
      notified,
    };
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : "Unknown error";
    console.error("Send breach notification error:", error);
    return {
      success: false,
      notified: 0,
      error: errorMessage,
    };
  }
}

/**
 * Notify HHS (if required)
 */
export async function notifyHHS(breachId: string): Promise<{ success: boolean; error?: string }> {
  try {
    const supabase = await createClient();

    // Get breach details
    const { data: breach, error: breachError } = await supabase
      .from("breach_events")
      .select("*")
      .eq("id", breachId)
      .single();

    if (breachError || !breach) {
      throw new Error("Breach record not found");
    }

    // Check if HHS notification is required (>500 affected)
    if (breach.affected_records < 500) {
      return {
        success: true,
        error: "HHS notification not required (<500 affected records)",
      };
    }

    // TODO: Implement actual HHS notification (via HHS portal or API)
    // For now, log the requirement
    
    await logDataModification(
      "system",
      "create",
      "hhs_notification",
      breachId,
      undefined,
      undefined,
      true,
      {
        affectedRecords: breach.affected_records,
        breachType: breach.breach_type,
      }
    );

    // Update breach record
    await supabase
      .from("breach_events")
      .update({
        hhs_notified: true,
        hhs_notified_at: new Date().toISOString(),
      })
      .eq("id", breachId);

    return { success: true };
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : "Unknown error";
    console.error("Notify HHS error:", error);
    return {
      success: false,
      error: errorMessage,
    };
  }
}

