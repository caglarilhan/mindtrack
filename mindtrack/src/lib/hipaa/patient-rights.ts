/**
 * Patient Rights Implementation
 * HIPAA Requirement: §164.524 - Access of Individuals
 */

import { createClient } from "@/utils/supabase/server";
import { hasAccess } from "./access-control";
import { logDataAccess, logDataModification, logDataExport } from "./audit-log";
import { encryptPHI, decryptPHI } from "./encryption";
import { generateSOAPPDF } from "../pdf/soap-pdf";

export interface PatientAccessRequest {
  patientId: string;
  requestType: "access" | "amend" | "delete" | "restrict";
  description?: string;
  requestedData?: string[]; // Specific data types requested
}

export interface PatientAccessResponse {
  success: boolean;
  requestId?: string;
  error?: string;
}

/**
 * Request patient data access
 */
export async function requestPatientAccess(
  patientId: string,
  requestedData?: string[]
): Promise<PatientAccessResponse> {
  try {
    const supabase = await createClient();

    // Create access request
    const { data, error } = await supabase
      .from("patient_access_requests")
      .insert({
        patient_id: patientId,
        request_type: "access",
        requested_data: requestedData || null,
        status: "pending",
      })
      .select("id")
      .single();

    if (error) {
      throw new Error(`Failed to create access request: ${error.message}`);
    }

    // Log access request
    await logDataAccess(patientId, "patient_access_request", data.id, undefined, undefined, true);

    return {
      success: true,
      requestId: data.id,
    };
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : "Unknown error";
    console.error("Request patient access error:", error);
    return {
      success: false,
      error: errorMessage,
    };
  }
}

/**
 * Export patient data (Right to Access)
 */
export async function exportPatientData(
  patientId: string,
  format: "pdf" | "json" | "csv" = "pdf",
  dateRange?: { start: string; end: string }
): Promise<{ success: boolean; data?: Buffer | string; filename?: string; error?: string }> {
  try {
    const supabase = await createClient();

    // Verify patient access (patients can only access their own data)
    const { data: { user } } = await supabase.auth.getUser();
    if (!user || user.id !== patientId) {
      return {
        success: false,
        error: "Access denied - can only access own data",
      };
    }

    // Get patient data
    const { data: client } = await supabase
      .from("clients")
      .select("*")
      .eq("id", patientId)
      .single();

    if (!client) {
      return {
        success: false,
        error: "Patient not found",
      };
    }

    // Get session notes
    let notesQuery = supabase
      .from("notes")
      .select("*")
      .eq("client_id", patientId);

    if (dateRange) {
      notesQuery = notesQuery
        .gte("created_at", dateRange.start)
        .lte("created_at", dateRange.end);
    }

    const { data: notes } = await notesQuery.order("created_at", { ascending: false });

    // Log export
    await logDataExport(
      patientId,
      "patient_data",
      patientId,
      format,
      undefined,
      undefined
    );

    // Format data based on requested format
    if (format === "pdf") {
      // Generate PDF export
      // For now, return a simple PDF (in production, create comprehensive PDF)
      return {
        success: true,
        data: Buffer.from("PDF export - implementation needed"),
        filename: `patient-data-${patientId}-${new Date().toISOString().split("T")[0]}.pdf`,
      };
    } else if (format === "json") {
      // JSON export
      const exportData = {
        patient: {
          id: client.id,
          name: client.name,
          // Add other non-PHI fields
        },
        notes: notes?.map((note) => ({
          id: note.id,
          date: note.created_at,
          type: note.type,
          // Decrypt note content if needed
        })) || [],
        exportedAt: new Date().toISOString(),
      };

      return {
        success: true,
        data: JSON.stringify(exportData, null, 2),
        filename: `patient-data-${patientId}-${new Date().toISOString().split("T")[0]}.json`,
      };
    } else {
      // CSV export
      const csvRows: string[] = [];
      csvRows.push("Date,Type,Note");
      
      notes?.forEach((note) => {
        csvRows.push(`${note.created_at},${note.type},""`);
      });

      return {
        success: true,
        data: csvRows.join("\n"),
        filename: `patient-data-${patientId}-${new Date().toISOString().split("T")[0]}.csv`,
      };
    }
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : "Unknown error";
    console.error("Export patient data error:", error);
    return {
      success: false,
      error: errorMessage,
    };
  }
}

/**
 * Request data amendment (Right to Amend)
 */
export async function requestDataAmendment(
  patientId: string,
  recordId: string,
  recordType: string,
  amendmentRequest: string
): Promise<PatientAccessResponse> {
  try {
    const supabase = await createClient();

    // Verify patient access
    const { data: { user } } = await supabase.auth.getUser();
    if (!user || user.id !== patientId) {
      return {
        success: false,
        error: "Access denied",
      };
    }

    // Create amendment request
    const { data, error } = await supabase
      .from("patient_access_requests")
      .insert({
        patient_id: patientId,
        request_type: "amend",
        record_id: recordId,
        record_type: recordType,
        amendment_request: amendmentRequest,
        status: "pending",
      })
      .select("id")
      .single();

    if (error) {
      throw new Error(`Failed to create amendment request: ${error.message}`);
    }

    // Log amendment request
    await logDataModification(
      patientId,
      "create",
      "amendment_request",
      recordId,
      undefined,
      undefined,
      true,
      {
        recordType,
        amendmentRequest,
      }
    );

    return {
      success: true,
      requestId: data.id,
    };
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : "Unknown error";
    console.error("Request data amendment error:", error);
    return {
      success: false,
      error: errorMessage,
    };
  }
}

/**
 * Request data deletion (Right to be Forgotten)
 */
export async function requestDataDeletion(
  patientId: string,
  reason?: string
): Promise<PatientAccessResponse> {
  try {
    const supabase = await createClient();

    // Verify patient access
    const { data: { user } } = await supabase.auth.getUser();
    if (!user || user.id !== patientId) {
      return {
        success: false,
        error: "Access denied",
      };
    }

    // Create deletion request
    const { data, error } = await supabase
      .from("patient_access_requests")
      .insert({
        patient_id: patientId,
        request_type: "delete",
        deletion_reason: reason || null,
        status: "pending",
      })
      .select("id")
      .single();

    if (error) {
      throw new Error(`Failed to create deletion request: ${error.message}`);
    }

    // Log deletion request
    await logDataModification(
      patientId,
      "create",
      "deletion_request",
      patientId,
      undefined,
      undefined,
      true,
      {
        reason,
      }
    );

    return {
      success: true,
      requestId: data.id,
    };
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : "Unknown error";
    console.error("Request data deletion error:", error);
    return {
      success: false,
      error: errorMessage,
    };
  }
}

/**
 * Process deletion request (secure deletion)
 */
export async function processDeletionRequest(
  requestId: string,
  therapistId: string
): Promise<{ success: boolean; deletedRecords?: number; error?: string }> {
  try {
    const supabase = await createClient();

    // Get deletion request
    const { data: request, error: requestError } = await supabase
      .from("patient_access_requests")
      .select("*")
      .eq("id", requestId)
      .eq("request_type", "delete")
      .eq("status", "pending")
      .single();

    if (requestError || !request) {
      throw new Error("Deletion request not found or already processed");
    }

    // Verify therapist has access
    const hasAccessToPatient = await hasAccess(therapistId, "clients", "delete", request.patient_id);
    if (!hasAccessToPatient) {
      throw new Error("Access denied");
    }

    // Secure deletion (mark as deleted, don't actually delete for audit purposes)
    let deletedCount = 0;

    // Delete notes (soft delete)
    const { data: notes } = await supabase
      .from("notes")
      .select("id")
      .eq("client_id", request.patient_id);

    if (notes) {
      await supabase
        .from("notes")
        .update({ deleted_at: new Date().toISOString() })
        .eq("client_id", request.patient_id);
      deletedCount += notes.length;
    }

    // Delete client record (soft delete)
    await supabase
      .from("clients")
      .update({ deleted_at: new Date().toISOString() })
      .eq("id", request.patient_id);

    deletedCount++;

    // Update request status
    await supabase
      .from("patient_access_requests")
      .update({
        status: "completed",
        completed_at: new Date().toISOString(),
        completed_by: therapistId,
      })
      .eq("id", requestId);

    // Log deletion
    await logDataModification(
      therapistId,
      "delete",
      "patient_data",
      request.patient_id,
      undefined,
      undefined,
      true,
      {
        requestId,
        deletedRecords: deletedCount,
      }
    );

    return {
      success: true,
      deletedRecords: deletedCount,
    };
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : "Unknown error";
    console.error("Process deletion request error:", error);
    return {
      success: false,
      error: errorMessage,
    };
  }
}





