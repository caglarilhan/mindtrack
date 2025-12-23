# Sprint 8: Email & Communication - Detaylı Plan

## 🎯 Sprint Hedefi
Email gönderme, bildirimler ve iletişim özelliklerini tamamlamak.

## 📋 Task Detayları

### Task 8.1: Email Service Entegrasyonu

#### Resend Entegrasyonu (Önerilen)
```typescript
// src/lib/email/resend.ts
import { Resend } from 'resend';

const resend = new Resend(process.env.RESEND_API_KEY);

export async function sendEmail({
  to,
  subject,
  html,
  text,
  attachments,
}: EmailOptions) {
  return await resend.emails.send({
    from: 'MindTrack <noreply@mindtrack.com>',
    to,
    subject,
    html,
    text,
    attachments,
  });
}
```

#### SMTP Yapılandırması
- Environment variables
- SMTP connection pooling
- Retry logic
- Error handling

**Dosyalar:**
- `src/lib/email/resend.ts` - Resend service
- `src/lib/email/smtp.ts` - SMTP fallback
- `.env.example` - Email config

---

### Task 8.2: Email Template'leri

#### Template Sistemi
```typescript
// src/lib/email/templates.ts
export const EMAIL_TEMPLATES = {
  soapNote: (data: SOAPEmailData) => ({
    subject: `SOAP Notu - ${data.clientName}`,
    html: renderSOAPTemplate(data),
    text: renderSOAPTextTemplate(data),
  }),
  riskAlert: (data: RiskEmailData) => ({
    subject: `⚠️ Risk Uyarısı - ${data.clientName}`,
    html: renderRiskTemplate(data),
  }),
  // ...
};
```

#### Template'ler
1. **SOAP Notu Email**
   - SOAP içeriği
   - PDF attachment
   - Paylaşım linki
   - Risk bilgisi

2. **Risk Uyarısı Email**
   - Risk seviyesi
   - Tespit edilen kelimeler
   - Önerilen aksiyonlar
   - Acil durum bilgileri

3. **Randevu Hatırlatma**
   - Randevu detayları
   - Telehealth linki
   - İptal linki

4. **Paylaşım Linki**
   - Paylaşım linki
   - QR kod (image)
   - Güvenlik notları

**Dosyalar:**
- `src/lib/email/templates.ts` - Template definitions
- `src/lib/email/templates/soap.tsx` - SOAP template
- `src/lib/email/templates/risk.tsx` - Risk template
- `src/lib/email/templates/appointment.tsx` - Appointment template
- `src/lib/email/templates/share.tsx` - Share template

---

### Task 8.3: Email Gönderme Özellikleri

#### SOAP Notu Email Gönderme
```typescript
// src/app/api/email/send-soap/route.ts
export async function POST(request: NextRequest) {
  const { soapId, recipientEmails } = await request.json();
  
  const soap = await getSOAPNote(soapId);
  const pdf = await generatePDF(soap);
  
  await sendEmail({
    to: recipientEmails,
    ...EMAIL_TEMPLATES.soapNote({
      clientName: soap.clientName,
      date: soap.createdAt,
      soap: soap.content,
    }),
    attachments: [{
      filename: `SOAP-${soap.clientName}.pdf`,
      content: pdf,
    }],
  });
}
```

#### Özellikler
- PDF attachment
- Çoklu alıcı
- Email gönderim durumu
- Gönderim geçmişi
- Hata yönetimi

**Dosyalar:**
- `src/app/api/email/send-soap/route.ts`
- `src/app/api/email/send-risk/route.ts`
- `src/components/email/send-email-button.tsx`
- `src/components/email/email-history.tsx`

---

### Task 8.4: Bildirim Sistemi İyileştirmeleri

#### Email Bildirimleri
- Risk tespit edildiğinde email
- SOAP notu oluşturulduğunda email
- Randevu hatırlatmaları

#### SMS Bildirimleri (Twilio)
```typescript
// src/lib/notifications/sms.ts
import twilio from 'twilio';

const client = twilio(
  process.env.TWILIO_ACCOUNT_SID,
  process.env.TWILIO_AUTH_TOKEN
);

export async function sendSMS(to: string, body: string) {
  return await client.messages.create({
    body,
    to,
    from: process.env.TWILIO_PHONE_NUMBER,
  });
}
```

#### Push Notifications (Web)
- Service Worker
- Notification API
- Permission management

**Dosyalar:**
- `src/lib/notifications/email.ts`
- `src/lib/notifications/sms.ts`
- `src/lib/notifications/push.ts`
- `src/components/notifications/notification-center.tsx`

---

### Task 8.5: Communication Features (Opsiyonel)

#### Mesajlaşma Sistemi
- Secure messaging
- File sharing
- Message threading
- Read receipts

**Dosyalar:**
- `src/app/api/messages/route.ts`
- `src/components/messaging/message-list.tsx`
- `src/components/messaging/message-composer.tsx`

---

## 📊 Success Metrics

### Email Metrics
- 📧 Email delivery rate: > 95%
- ⏱️ Email send time: < 2s
- 📄 PDF attachment success: > 98%
- 🔔 Notification delivery: > 90%

---

## 🚀 Implementation Order

1. **Email Service (Task 8.1)** - Temel altyapı
2. **Email Templates (Task 8.2)** - Template'ler
3. **Email Features (Task 8.3)** - Özellikler
4. **Notifications (Task 8.4)** - Bildirimler
5. **Communication (Task 8.5)** - Opsiyonel

---

## ✅ Definition of Done

- [ ] Email gönderme çalışıyor
- [ ] PDF attachment çalışıyor
- [ ] Email template'leri hazır
- [ ] Bildirim sistemi çalışıyor
- [ ] Error handling yapıldı
- [ ] Test coverage > 80%

---

## 📝 Notes

- Resend önerilir (kolay setup, iyi fiyat)
- Email template'leri responsive olmalı
- Test email'leri için development mode
- Rate limiting email gönderiminde





