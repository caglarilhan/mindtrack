import FormRunner from "@/components/forms/form-runner";
import type { FormTemplate } from "@/types/forms";
import { createClient } from "@supabase/supabase-js";

const FALLBACK_TEMPLATE: FormTemplate = {
  id: "demo-kiosk",
  clinic_id: "demo-clinic",
  name: "Kiosk Check-in",
  description: "Temel check-in formu",
  version: 1,
  fields: [
    { id: "full_name", type: "text", label: "Ad Soyad", required: true },
    { id: "birth_date", type: "date", label: "Doğum Tarihi" },
    { id: "reason", type: "textarea", label: "Ziyaret Nedeni" },
    { id: "consent", type: "checkbox", label: "Aydınlatılmış onamı kabul ediyorum", required: true },
    { id: "signature", type: "signature", label: "İmza" },
  ],
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
  category: "Intake",
  tags: ["kiosk"],
  is_published: true,
};

async function fetchTemplate(templateId: string | null): Promise<FormTemplate> {
  if (!templateId) {
    return FALLBACK_TEMPLATE;
  }
  try {
    const supabase = createClient(process.env.NEXT_PUBLIC_SUPABASE_URL!, process.env.SUPABASE_SERVICE_ROLE_KEY!);
    const { data } = await supabase
      .from("form_templates")
      .select("*")
      .eq("id", templateId)
      .maybeSingle();
    if (data) {
      return {
        ...data,
        fields: data.fields || [],
        tags: data.tags || [],
      } as FormTemplate;
    }
  } catch (error) {
    console.error("[kiosk] template fetch error", error);
  }
  return FALLBACK_TEMPLATE;
}

export default async function KioskPage({ searchParams }: { searchParams: { templateId?: string } }) {
  const templateId = searchParams.templateId || null;
  const template = await fetchTemplate(templateId);

  return (
    <main className="min-h-screen bg-slate-100">
      <div className="mx-auto max-w-3xl p-4">
        <div className="mb-6 text-center">
          <p className="text-xs uppercase tracking-wide text-slate-500">MindTrack Kiosk</p>
          <h1 className="text-3xl font-semibold">{template.name}</h1>
          {!templateId && <p className="text-sm text-muted-foreground">Demo form görüntüleniyor</p>}
        </div>
        <FormRunner template={template} kiosk />
      </div>
    </main>
  );
}
