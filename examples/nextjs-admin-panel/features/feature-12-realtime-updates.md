# Feature F12: Real-time Updates & Notifications

**Priority**: P3 (Medium - Phase 3)  
**Business Value**: 6/10  
**Estimated Effort**: 1.5 weeks  
**Dependencies**: F02 (Dashboard), F06 (Queue Monitoring)

---

## Feature Description

Real-time notification system providing toast notifications, live data updates without page refresh, and background sync indicators. Enhances user experience by keeping users informed of system events, data changes, and operation completions without requiring manual refreshes.

---

## User Stories

### US1: Receive Toast Notifications for Actions
**As an** admin user  
**I want to** receive immediate visual feedback for my actions  
**So that** I know operations completed successfully or failed

**Acceptance Criteria**:
- Toast notifications appear for:
  - Successful saves (e.g., "Category updated successfully")
  - Errors (e.g., "Failed to update product - network error")
  - Bulk operation completion (e.g., "23 products updated")
  - Long-running operation status (e.g., "Export in progress...")
- Toast types with visual distinction:
  - Success (green, checkmark icon)
  - Error (red, X icon)
  - Warning (yellow, warning icon)
  - Info (blue, info icon)
- Toast auto-dismisses after 5 seconds (configurable)
- Manual dismiss button (X) on each toast
- Toast stacks vertically (max 3 visible at once)
- Actions in toast (e.g., "Undo", "View Details", "Retry")

---

### US2: Enable Auto-refresh for Live Data
**As an** admin user  
**I want to** see data updates automatically without refreshing the page  
**So that** I have up-to-date information when monitoring operations

**Acceptance Criteria**:
- Auto-refresh toggle on key pages:
  - Dashboard (queue stats)
  - Queue monitoring (all queue tabs)
  - Category browser (when viewing processing status)
- Configurable refresh intervals: 5s, 10s, 30s, 60s, Off
- Visual indicator during refresh (subtle spinner in corner)
- Refresh preserves:
  - Current page number
  - Applied filters
  - Sort order
  - Selected items (checkboxes)
- Pause refresh when:
  - User is editing (form fields have focus)
  - Modal/dialog is open
  - Tab is not visible (browser tab inactive)

---

### US3: Display Background Sync Indicators
**As an** admin user  
**I want to** see visual indicators when data is syncing  
**So that** I know the app is working and when data is fresh

**Acceptance Criteria**:
- Sync status indicator in app header/corner:
  - 🟢 "Up to date" (green dot)
  - 🟡 "Syncing..." (yellow spinner)
  - 🔴 "Sync failed" (red dot with retry button)
- Last sync timestamp displayed (e.g., "Updated 3 seconds ago")
- Hover tooltip shows sync details
- Failed sync shows error message
- Manual "Refresh Now" button
- Optimistic UI updates (show change immediately, rollback if fails)

---

### US4: Notify on Important System Events
**As an** admin user  
**I want to** receive notifications for important system events  
**So that** I can respond to issues quickly

**Acceptance Criteria**:
- System event notifications for:
  - Queue processing completed (e.g., "Category queue completed - 145 items processed")
  - High failure rate detected (e.g., "⚠️ Dischem scraper: 45% failure rate in last hour")
  - Worker stuck/crashed (e.g., "⚠️ Worker #1234 locked for > 1 hour")
  - Database connection issues
- Notification badge counter in app header
- Notification center panel (slide-out) showing recent notifications
- Mark as read functionality
- Clear all notifications button
- Notification persistence (saved per user)
- Sound alerts for critical notifications (optional, user preference)

---

## Success Criteria

### Functional
- ✅ Toast notifications appear for all user actions
- ✅ Auto-refresh updates data without disrupting user
- ✅ Sync indicators accurately reflect backend state
- ✅ System notifications trigger for important events
- ✅ Notification center stores notification history

### Performance
- ✅ Auto-refresh completes in < 500ms
- ✅ Toast rendering is instant (< 50ms)
- ✅ Background sync doesn't block UI interactions
- ✅ Notification center loads in < 200ms

### UX
- ✅ Toasts don't obstruct important UI elements
- ✅ Auto-refresh is non-intrusive
- ✅ Clear visual distinction between notification types
- ✅ Animations are smooth (60fps)
- ✅ User can control notification preferences

---

## Scope

### Includes
✅ Toast notification system (success, error, warning, info)  
✅ Auto-refresh toggle with configurable intervals  
✅ Background sync indicators (status dot + timestamp)  
✅ System event notifications  
✅ Notification center (history panel)  
✅ Mark as read/clear functionality  
✅ Optimistic UI updates  
✅ Pause refresh during user interactions  
✅ Visual feedback during sync  
✅ Manual refresh button  

### Excludes
❌ WebSocket real-time connection (use polling for MVP)  
❌ Push notifications (browser notifications API)  
❌ Email notifications  
❌ SMS/Slack notifications  
❌ Notification filtering/preferences (all users see all)  
❌ Notification analytics/tracking  
❌ Custom notification sounds per event type  

---

## Technical Notes

### Tech Stack
- **Notifications**: `sonner` or `react-hot-toast` library
- **Real-time Updates**: React Query with polling (refetchInterval)
- **State Management**: Zustand or React Context for notification state
- **API Routes**:
  - `/api/notifications` (GET user notifications)
  - `/api/notifications/mark-read` (POST)
  - `/api/system/health` (GET sync status)

### Toast Notification Implementation
```typescript
import { toast } from 'sonner';

// Success toast
toast.success('Product updated successfully', {
  description: 'Changes saved to database',
  duration: 5000,
  action: {
    label: 'View',
    onClick: () => router.push(`/products/${productId}`)
  }
});

// Error toast with retry
toast.error('Failed to update product', {
  description: error.message,
  action: {
    label: 'Retry',
    onClick: () => retryUpdate()
  }
});

// Loading toast (dismissable manually)
const toastId = toast.loading('Exporting 1,245 products...');
// Later: toast.success('Export complete', { id: toastId });
```

### Auto-refresh with React Query
```typescript
const { data, isRefetching } = useQuery({
  queryKey: ['queue-stats'],
  queryFn: fetchQueueStats,
  refetchInterval: refreshInterval, // 5000, 10000, 30000, etc.
  refetchIntervalInBackground: false, // Pause when tab not visible
  enabled: isRefreshEnabled && !isModalOpen && !hasFieldFocus
});
```

### Optimistic Updates
```typescript
const updateMutation = useMutation({
  mutationFn: updateProduct,
  onMutate: async (newData) => {
    // Cancel outgoing refetches
    await queryClient.cancelQueries(['product', id]);
    
    // Snapshot previous value
    const previousData = queryClient.getQueryData(['product', id]);
    
    // Optimistically update
    queryClient.setQueryData(['product', id], newData);
    
    // Return context with previous value
    return { previousData };
  },
  onError: (err, newData, context) => {
    // Rollback to previous value
    queryClient.setQueryData(['product', id], context.previousData);
    toast.error('Update failed - changes reverted');
  },
  onSuccess: () => {
    toast.success('Product updated');
  }
});
```

### System Event Detection
```typescript
// Example: Detect high failure rate
async function checkFailureRate(retailerId: number) {
  const oneHourAgo = new Date(Date.now() - 60 * 60 * 1000);
  
  const stats = await prisma.scraping_queue.groupBy({
    by: ['status'],
    _count: true,
    where: {
      retailer_id: retailerId,
      created_at: { gte: oneHourAgo }
    }
  });
  
  const total = stats.reduce((sum, s) => sum + s._count, 0);
  const failed = stats.find(s => s.status === 'failed')?._count || 0;
  const failureRate = (failed / total) * 100;
  
  if (failureRate > 40) {
    // Create notification
    await createSystemNotification({
      type: 'warning',
      title: 'High Failure Rate Detected',
      message: `${retailer.name}: ${failureRate.toFixed(0)}% failure rate in last hour`,
      severity: 'high'
    });
  }
}
```

---

## Dependencies

**Required Before Starting**:
- F02: Dashboard (target page for notifications)
- F06: Queue Monitoring (target page for auto-refresh)
- React Query configured

**External Dependencies**:
- sonner (^1.4.0) OR react-hot-toast (^2.4.0)
- date-fns (for timestamp formatting)

---

## Acceptance Testing Checklist

- [ ] Success toast appears on successful save
- [ ] Error toast appears on failed operation
- [ ] Toast auto-dismisses after 5 seconds
- [ ] Manual dismiss (X button) works
- [ ] Toast stacks vertically (max 3)
- [ ] Action buttons in toast work (Undo, Retry, View)
- [ ] Auto-refresh toggle works (on/off)
- [ ] Refresh interval selector works (5s/10s/30s/60s)
- [ ] Data updates automatically at selected interval
- [ ] Refresh preserves page, filters, sort
- [ ] Refresh preserves checkbox selections
- [ ] Refresh pauses when modal open
- [ ] Refresh pauses when field has focus
- [ ] Refresh pauses when tab inactive
- [ ] Sync indicator shows status (green/yellow/red)
- [ ] Last sync timestamp displays
- [ ] "Updated X seconds ago" updates in real-time
- [ ] Failed sync shows error message
- [ ] Manual "Refresh Now" button works
- [ ] Optimistic updates show immediately
- [ ] Optimistic updates rollback on error
- [ ] System notifications trigger correctly
- [ ] Notification badge counter displays
- [ ] Notification center panel opens
- [ ] Notification history displays
- [ ] Mark as read functionality works
- [ ] Clear all notifications works
- [ ] Critical notifications visually distinct
- [ ] Mobile layout shows notifications appropriately
- [ ] Toasts don't obstruct important UI elements
- [ ] Animations are smooth

---

## Related Documentation

- Main Spec: `/docs/NEXTJS_ADMIN_SPEC.md` (lines 951-961)
- Dashboard Auto-refresh: `/docs/NEXTJS_ADMIN_SPEC.md` (lines 133-136)
- Queue Auto-refresh: `/docs/NEXTJS_ADMIN_SPEC.md` (lines 723-724)

---

## Ready for Specification

To create the full specification for this feature, run:

```bash
/speckit.specify docs/features/feature-12-realtime-updates.md
```

Or use the quick-start script:

```bash
cd docs/features
./quick-start.sh F12
```
