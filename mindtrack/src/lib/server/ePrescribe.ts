/**
 * E-Prescribe Service
 * Mock external pharmacy connector + lab protocol scheduler
 */

import { createSupabaseServerClient } from "@/lib/supabaseClient";

export interface EPrescriptionPayload {
  patientId: string;
  medicationName: string;
  dosage: string;
  route?: string;
  quantity?: number;
  frequency: string;
  pharmacyName?: string;
  pharmacyNpi?: string;
  region?: "us" | "eu";
}

export interface LabProtocolInput {
  patientId: string;
  testName: string;
  protocol: "clozapine" | "lithium" | "general";
  dueDate: string;
  region?: "us" | "eu";
}

export async function submitEPrescription(payload: EPrescriptionPayload) {
  const supabase = await createSupabaseServerClient();
  const region = payload.region || "us";

  // Mock external API call
  const externalReference = `EP-${Date.now()}`;
  const success = Math.random() > 0.05;

  const { data, error } = await supabase
    .from("medication_orders")
    .insert({
      patient_id: payload.patientId,
      medication_name: payload.medicationName,
      dosage: payload.dosage,
      route: payload.route,
      quantity: payload.quantity,
      frequency: payload.frequency,
      pharmacy_name: payload.pharmacyName,
      pharmacy_npi: payload.pharmacyNpi,
      status: success ? "sent" : "failed",
      external_reference: externalReference,
      response_message: success ? "Prescription transmitted" : "Transmission error",
      region,
    })
    .select()
    .single();

  if (error) {
    console.error("[ePrescribe] DB error", error);
    return { success: false, error: error.message };
  }

  return { success, order: data };
}

export async function scheduleLabProtocol(input: LabProtocolInput) {
  const supabase = await createSupabaseServerClient();
  const region = input.region || "us";

  const { data, error } = await supabase
    .from("lab_orders")
    .insert({
      patient_id: input.patientId,
      test_name: input.testName,
      protocol: input.protocol,
      due_date: input.dueDate,
      status: new Date(input.dueDate) < new Date() ? "overdue" : "pending",
      region,
    })
    .select()
    .single();

  if (error) {
    console.error("[labProtocol] insert error", error);
    return { success: false, error: error.message };
  }

  return { success: true, order: data };
}
