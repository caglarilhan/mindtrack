import { NextRequest, NextResponse } from 'next/server';
import { requirePermission } from '@/lib/rbac';

export async function POST(request: NextRequest) {
  try {
    await requirePermission('settings:integrations:write');
    
    const { ruleId, trigger, testData } = await request.json();
    
    if (!trigger) {
      return NextResponse.json({ error: 'trigger gerekli' }, { status: 400 });
    }

    // Mock test execution - gerçek implementasyonda automation engine'e gönderilecek
    const mockResult = {
      ruleId: ruleId || 'test-rule',
      triggerMatched: true,
      conditionsMet: testData?.conditions || [],
      actionsExecuted: [
        {
          type: 'notify',
          status: 'success',
          message: 'Test bildirimi gönderildi (mock)'
        }
      ],
      executionTime: 45, // ms
      timestamp: new Date().toISOString()
    };

    return NextResponse.json({
      success: true,
      result: mockResult
    });
  } catch (e: any) {
    return NextResponse.json({ error: e?.message || 'Test başarısız' }, { status: 500 });
  }
}










