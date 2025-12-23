# Sprint 7: Performance & Optimization - Detaylı Plan

## 🎯 Sprint Hedefi
Uygulamanın performansını optimize etmek, hızlandırmak ve kullanıcı deneyimini iyileştirmek.

## 📋 Task Detayları

### Task 7.1: Caching Stratejisi

#### React Query Entegrasyonu
```typescript
// src/lib/react-query.ts
import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 dakika
      cacheTime: 10 * 60 * 1000, // 10 dakika
      refetchOnWindowFocus: false,
    },
  },
});
```

#### API Response Caching
- SOAP notları için cache
- Client listesi cache
- Session data cache
- Analytics data cache

#### Cache Invalidation
- SOAP notu oluşturulduğunda cache'i temizle
- SOAP notu güncellendiğinde cache'i güncelle
- Manual cache refresh butonu

**Dosyalar:**
- `src/lib/react-query.ts` - Query client config
- `src/hooks/use-soap-notes.ts` - SOAP notes hook
- `src/hooks/use-clients.ts` - Clients hook
- `src/hooks/use-analytics.ts` - Analytics hook

---

### Task 7.2: Lazy Loading & Code Splitting

#### Route-based Code Splitting
```typescript
// src/app/dashboard/analytics/page.tsx
import dynamic from 'next/dynamic';

const AnalyticsDashboard = dynamic(
  () => import('@/components/ai/analytics-dashboard'),
  { loading: () => <SOAPSkeleton /> }
);
```

#### Component Lazy Loading
- Analytics dashboard
- Chart components (Recharts)
- PDF viewer
- Word editor
- Heavy UI components

#### Bundle Analyzer
```bash
npm install @next/bundle-analyzer
```

**Dosyalar:**
- `next.config.js` - Bundle analyzer config
- Component'lerde dynamic import kullanımı

---

### Task 7.3: Bundle Size Optimization

#### Dependency Cleanup
- Gereksiz paketleri kaldır
- Duplicate dependencies'i temizle
- Tree shaking için ES modules kullan

#### Icon Optimization
```typescript
// Sadece kullanılan icon'ları import et
import { FileText, Calendar } from 'lucide-react';
```

#### Font Optimization
- System fonts kullan (varsayılan)
- Custom font için font-display: swap
- Font subsetting

**Komutlar:**
```bash
npm run analyze  # Bundle analyzer
npm run build -- --analyze
```

---

### Task 7.4: Database Query Optimization

#### Index Optimization
```sql
-- SOAP notes için index
CREATE INDEX IF NOT EXISTS idx_notes_client_created 
ON notes(client_id, created_at DESC);

-- Sessions için index
CREATE INDEX IF NOT EXISTS idx_sessions_client_created 
ON therapy_sessions(client_id, created_at DESC);
```

#### Query Pagination
```typescript
// Pagination hook
export function usePaginatedNotes(clientId: string, pageSize = 20) {
  return useQuery({
    queryKey: ['notes', clientId, page],
    queryFn: () => fetchNotes(clientId, page, pageSize),
  });
}
```

#### Batch Operations
- Multiple SOAP notes oluşturma
- Bulk updates
- Batch exports

**Dosyalar:**
- `supabase/migrations/xxx_add_indexes.sql`
- `src/lib/db/optimizations.ts`

---

### Task 7.5: Frontend Performance

#### React.memo Optimizasyonu
```typescript
export const SOAPDisplay = React.memo(({ soap }: Props) => {
  // Component implementation
});
```

#### useMemo/useCallback
```typescript
const memoizedAnalytics = useMemo(
  () => calculateAnalytics(notes),
  [notes]
);

const handleSave = useCallback(() => {
  // Save logic
}, [dependencies]);
```

#### Virtual Scrolling
```typescript
import { FixedSizeList } from 'react-window';

// Büyük listeler için
<FixedSizeList
  height={600}
  itemCount={items.length}
  itemSize={50}
>
  {Row}
</FixedSizeList>
```

**Dosyalar:**
- Component'lerde memo/useMemo/useCallback kullanımı
- `src/components/ui/virtual-list.tsx`

---

## 📊 Success Metrics

### Performance Goals
- ⚡ First Contentful Paint (FCP): < 1.5s
- ⚡ Largest Contentful Paint (LCP): < 2.5s
- ⚡ Time to Interactive (TTI): < 3.5s
- 📦 Bundle size: < 500KB (gzipped)
- 🚀 API response time: < 200ms (p95)

### Measurement Tools
- Lighthouse CI
- Web Vitals
- Bundle Analyzer
- Sentry Performance

---

## 🚀 Implementation Order

1. **Caching (Task 7.1)** - En hızlı kazanç
2. **Lazy Loading (Task 7.2)** - Bundle size azaltma
3. **Bundle Optimization (Task 7.3)** - Devam
4. **DB Optimization (Task 7.4)** - Backend iyileştirme
5. **Frontend Performance (Task 7.5)** - Son dokunuşlar

---

## ✅ Definition of Done

- [ ] Tüm task'lar tamamlandı
- [ ] Performance metrikleri hedeflere ulaştı
- [ ] Bundle size %30+ azaldı
- [ ] Lighthouse score > 90
- [ ] Test coverage korundu
- [ ] Documentation güncellendi

---

## 📝 Notes

- Her task sonunda performance test yapılmalı
- Metrics dashboard'a eklenecek
- Breaking changes için migration guide hazırlanmalı





