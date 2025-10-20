# Feature F06: Queue Monitoring & Management

**Priority**: P1 (Critical - MVP)  
**Business Value**: 10/10  
**Estimated Effort**: 2 weeks  
**Dependencies**: F01 (Authentication)

---

## Feature Description

Real-time monitoring and management interface for all three scraping queue types: Product Queue, Category URL Queue, and Category Queue. Provides visibility into queue status, worker assignments, retry counts, and allows administrative actions like retry, reset, pause, and resume operations.

This is a mission-critical feature for operations teams to ensure scraping pipelines run smoothly and to troubleshoot issues quickly.

---

## User Stories

### US1: View Queue Overview Statistics
**As an** admin user  
**I want to** see high-level statistics for each queue type  
**So that** I can quickly assess queue health

**Acceptance Criteria**:
- Dashboard displays 4 metric cards per queue: Queued, In Progress, Completed, Failed
- Metrics update automatically every 5 seconds
- Failed count highlighted in red if > 0
- Each metric card is clickable to filter queue table
- Toggle to pause/resume auto-refresh

---

### US2: View and Filter Queue Items
**As an** admin user  
**I want to** view detailed queue items with filtering capabilities  
**So that** I can find and inspect specific tasks

**Acceptance Criteria**:
- Tabbed interface: Product Queue | Category URL Queue | Category Queue
- Table columns: URL, Retailer, Category ID, Status, Attempts, Worker ID, Last Update
- Status indicators with color coding:
  - 🟡 Queued (yellow)
  - 🟢 In Progress (green)
  - ✅ Completed (green check)
  - 🔴 Failed (red)
  - ⏸️ Locked (gray)
- Filter dropdowns: Retailer, Status
- URL search box with debounced search
- Pagination with page size options (25/50/100)

---

### US3: Perform Individual Queue Actions
**As an** admin user  
**I want to** retry, reset, or delete individual queue items  
**So that** I can manually intervene when needed

**Acceptance Criteria**:
- Actions menu (⋮) for each row with options:
  - Retry Now (for failed items)
  - Reset Status (unlock/set to queued)
  - Delete Item (with confirmation)
  - View Details (shows full error message if failed)
- Optimistic UI updates (immediate visual feedback)
- Toast notification confirming action
- Error handling with user-friendly messages

---

### US4: Perform Bulk Queue Actions
**As an** admin user  
**I want to** select multiple queue items and perform bulk operations  
**So that** I can manage queues efficiently at scale

**Acceptance Criteria**:
- Checkbox selection for individual items
- "Select All" checkbox selects all on current page
- Bulk action dropdown with options:
  - Retry Selected (for failed items)
  - Reset Selected (clear status, set to queued)
  - Delete Selected (with confirmation)
- Action button shows selection count (e.g., "Retry 15 Selected")
- Progress indicator for bulk operations
- Success message shows affected count

---

### US5: Monitor Queue in Real-time
**As an** admin user  
**I want to** see queue updates in real-time without manual refresh  
**So that** I can monitor active scraping operations

**Acceptance Criteria**:
- Auto-refresh every 5 seconds by default
- Visual indicator when data is refreshing (subtle spinner)
- Option to change refresh interval (5s, 10s, 30s, off)
- Pause auto-refresh when modal is open (to prevent data changes during edits)
- Resume auto-refresh when modal closes
- Refresh does not reset current page or filters

---

## Success Criteria

### Functional
- ✅ All three queue types are accessible via tabs
- ✅ Status indicators accurately reflect database state
- ✅ Filters work correctly and can be combined
- ✅ Bulk actions update multiple records correctly
- ✅ Real-time updates show latest queue status
- ✅ Worker ID displays for in-progress items

### Performance
- ✅ Initial queue load < 2 seconds for 10,000+ items
- ✅ Auto-refresh completes in < 500ms
- ✅ Filtering returns results in < 300ms
- ✅ Bulk operations process 100 items in < 5 seconds

### UX
- ✅ Loading states don't disrupt current view
- ✅ Failed items clearly highlighted
- ✅ Stuck workers identified (locked > 1 hour)
- ✅ Mobile responsive (table scrolls horizontally)
- ✅ Keyboard shortcuts (Ctrl+R to refresh)

---

## Scope

### Includes
✅ Three queue tabs (Product, Category URL, Category)  
✅ Queue overview metrics (4 cards per queue)  
✅ Queue item table with sorting and pagination  
✅ Status filtering (queued, in progress, completed, failed)  
✅ Retailer filtering  
✅ URL search  
✅ Individual actions (retry, reset, delete)  
✅ Bulk actions (retry, reset, delete)  
✅ Auto-refresh with configurable interval  
✅ Worker ID display  
✅ Error message viewing  

### Excludes
❌ Queue job creation (done by scrapers)  
❌ Worker management (start/stop workers) - separate feature  
❌ Queue prioritization (change job order)  
❌ Historical queue analytics (covered in F08)  
❌ Custom retry logic per item  
❌ Queue pause/resume at system level (manual worker control only)  

---

## Technical Notes

### Tech Stack
- **API Routes**:
  - `/api/queues/product` (GET, PATCH bulk, DELETE)
  - `/api/queues/category-url` (GET, PATCH bulk, DELETE)
  - `/api/queues/category` (GET, PATCH bulk, DELETE)
  - `/api/queues/stats` (GET overview metrics)
  - `/api/queues/actions` (POST retry/reset individual)
- **State Management**: React Query with polling
- **UI Components**: shadcn/ui (Tabs, Table, Badge, Select)

### Database Queries
```typescript
// Queue stats aggregation
const queueStats = await prisma.scraping_queue.groupBy({
  by: ['status'],
  _count: true,
  where: { retailer_id: retailerId } // optional filter
});

// Queue items with relationships
const queueItems = await prisma.scraping_queue.findMany({
  where: {
    AND: [
      retailerId ? { retailer_id: retailerId } : {},
      status ? { status } : {},
      searchTerm ? { 
        product_url: { contains: searchTerm, mode: 'insensitive' } 
      } : {}
    ]
  },
  include: {
    retailers: { select: { name: true } },
    categories: { select: { id: true, name: true } }
  },
  orderBy: { updated_at: 'desc' },
  skip: (page - 1) * pageSize,
  take: pageSize
});

// Bulk retry (reset failed to queued)
const result = await prisma.scraping_queue.updateMany({
  where: { id: { in: selectedIds }, status: 'failed' },
  data: { 
    status: 'pending',
    attempts: 0,
    error_message: null,
    locked_at: null,
    locked_by: null
  }
});
```

### Real-time Updates Strategy
```typescript
// React Query polling
const { data, isRefetching } = useQuery({
  queryKey: ['queue', queueType, filters],
  queryFn: () => fetchQueueItems(queueType, filters),
  refetchInterval: refreshInterval, // 5000ms default
  refetchIntervalInBackground: true,
  // Keep previous data while refetching
  placeholderData: keepPreviousData
});
```

### Status Color Coding
```typescript
const statusConfig = {
  pending: { icon: '🟡', color: 'yellow', label: 'Queued' },
  in_progress: { icon: '🟢', color: 'green', label: 'In Progress' },
  completed: { icon: '✅', color: 'green', label: 'Completed' },
  failed: { icon: '🔴', color: 'red', label: 'Failed' },
  locked: { icon: '⏸️', color: 'gray', label: 'Locked' }
};
```

---

## Dependencies

**Required Before Starting**:
- F01: Authentication
- Queue tables exist (scraping_queue, category_url_scraping_queue, category_scraping_queue)
- Prisma client configured

**External Dependencies**:
- React Query (^5.0.0)
- shadcn/ui components
- date-fns (for time formatting)

---

## Acceptance Testing Checklist

- [ ] All three queue tabs load successfully
- [ ] Overview metrics cards display correct counts
- [ ] Auto-refresh updates data every 5 seconds
- [ ] Failed count highlights in red
- [ ] Clicking metric card filters table
- [ ] Retailer filter dropdown works
- [ ] Status filter dropdown works
- [ ] URL search filters results (debounced)
- [ ] Table displays all columns correctly
- [ ] Status indicators show with correct colors
- [ ] Worker ID displays for in-progress items
- [ ] Actions menu (⋮) opens for each row
- [ ] Retry action works for failed items
- [ ] Reset action changes status to queued
- [ ] Delete action removes item (with confirmation)
- [ ] View Details shows error message
- [ ] Checkbox selects individual items
- [ ] Select All checkbox works
- [ ] Bulk Retry updates selected items
- [ ] Bulk Reset works
- [ ] Bulk Delete works (with confirmation)
- [ ] Refresh interval can be changed (5s/10s/30s/off)
- [ ] Auto-refresh pauses when modal open
- [ ] Pagination works (next/previous/page size)
- [ ] Table sorts by last update time (descending)
- [ ] Mobile layout scrolls table horizontally
- [ ] Toast notifications show for all actions
- [ ] Error handling displays user-friendly messages

---

## Related Documentation

- Main Spec: `/docs/NEXTJS_ADMIN_SPEC.md` (lines 688-742)
- Queue Tables Schema: `prisma/schema.prisma` (scraping_queue, category_url_scraping_queue, category_scraping_queue)
- API Design: `/docs/NEXTJS_ADMIN_SPEC.md` (lines 853-858)

---

## Ready for Specification

To create the full specification for this feature, run:

```bash
/speckit.specify docs/features/feature-06-queue-monitoring.md
```

Or use the quick-start script:

```bash
cd docs/features
./quick-start.sh F06
```
