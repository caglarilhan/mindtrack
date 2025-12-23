import { createSupabaseServerClient } from '@/lib/supabaseClient';

export async function enqueueDelivery(job: { channel: 'email'|'sms'; payload: any; delaySeconds?: number; runAt?: Date; }) {
  const supabase = await createSupabaseServerClient();
  const run_at = job.runAt || new Date(Date.now() + (job.delaySeconds || 0) * 1000);
  await supabase.from('delivery_queue').insert({ channel: job.channel, payload: job.payload, run_at });
}

export async function claimNextBatch(workerId: string, limit = 10) {
  const supabase = await createSupabaseServerClient();
  const nowIso = new Date().toISOString();
  const { data } = await supabase
    .from('delivery_queue')
    .select('*')
    .lte('run_at', nowIso)
    .is('locked_at', null)
    .order('run_at', { ascending: true })
    .limit(limit);
  const jobs = data || [];
  for (const j of jobs) {
    await supabase
      .from('delivery_queue')
      .update({ locked_at: new Date().toISOString(), locked_by: workerId })
      .eq('id', j.id)
      .is('locked_at', null);
  }
  return jobs;
}

export async function completeJob(id: string) {
  const supabase = await createSupabaseServerClient();
  await supabase.from('delivery_queue').delete().eq('id', id);
}

export async function retryJob(id: string, attempts: number, backoffSeconds = 60) {
  const supabase = await createSupabaseServerClient();
  await supabase
    .from('delivery_queue')
    .update({ attempts: attempts + 1, locked_at: null, locked_by: null, run_at: new Date(Date.now() + backoffSeconds * 1000).toISOString() })
    .eq('id', id);
}




