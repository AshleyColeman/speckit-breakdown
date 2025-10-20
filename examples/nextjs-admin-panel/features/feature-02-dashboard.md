# Feature F02: Dashboard Overview & System Health

**Priority**: P1 (Critical - MVP)  
**Business Value**: 9/10  
**Estimated Effort**: 1.5 weeks  
**Dependencies**: F01 (Authentication)

---

## Feature Description

A real-time dashboard providing immediate visibility into the health and performance of the entire product scraper system. The dashboard displays key metrics, active queue statuses, retailer performance, and recent scraping activity through cards and visualizations.

This is the landing page users see after authentication, giving them an instant overview of system status and quick access to critical areas requiring attention.

---

## User Stories

### US1: View System Overview Metrics
**As an** admin user  
**I want to** see high-level metrics (total products, categories, brands, active workers) on the dashboard  
**So that** I can quickly understand the current state of the system

**Acceptance Criteria**:
- Dashboard displays 4 metric cards: Products, Categories, Brands, Active Workers
- Each card shows current count with percentage change indicator (e.g., "+12% ↑")
- Metrics update when page is refreshed
- Metrics are accurate as of last data sync (< 5 minutes old)

---

### US2: Monitor Scraping Activity Over Time
**As an** admin user  
**I want to** view a chart showing products scraped over the last 7 days  
**So that** I can identify scraping trends and potential issues

**Acceptance Criteria**:
- Line chart displays products scraped per day for last 7 days
- Chart shows data broken down by retailer (multi-line chart)
- X-axis shows dates, Y-axis shows product count
- Chart is interactive with tooltips showing exact values
- Chart uses appropriate colors for each retailer

---

### US3: Monitor Active Queue Status
**As an** admin user  
**I want to** see real-time status of all scraping queues (queued, in progress, failed)  
**So that** I can identify bottlenecks or failures quickly

**Acceptance Criteria**:
- Table displays all 3 queue types: Product Queue, Category URL Queue, Category Queue
- For each queue: shows queued count, in-progress count, failed count
- Failed items are highlighted in red if count > 0
- Clicking a queue row navigates to detailed queue page
- Auto-refresh every 5 seconds (with toggle to disable)

---

### US4: View Retailer Health Status
**As an** admin user  
**I want to** see the status of each retailer including product counts and failures  
**So that** I can identify retailer-specific issues

**Acceptance Criteria**:
- Grid displays cards for each retailer (Clicks, Dischem, Faithful to Nature, Wellness Warehouse)
- Each card shows: retailer name, total products, status indicator (✅ healthy, ⚠️ warnings)
- Warning indicator appears if failed scrapes > 10
- Cards are color-coded (green for healthy, yellow for warnings)
- Clicking a card navigates to retailer detail page

---

## Success Criteria

### Functional
- ✅ Dashboard loads within 2 seconds on initial page load
- ✅ All metrics display accurate data from database
- ✅ Charts render correctly with proper scaling
- ✅ Auto-refresh works without memory leaks
- ✅ Mobile responsive layout (cards stack vertically)

### Performance
- ✅ Dashboard API endpoint responds in < 500ms
- ✅ Single database query per metric (no N+1 queries)
- ✅ Charts render with < 200ms delay after data load

### UX
- ✅ Loading states shown for all async data
- ✅ Skeleton loaders during initial load
- ✅ Clear visual hierarchy (most important metrics at top)
- ✅ Accessible color choices (not relying only on color for status)

---

## Scope

### Includes
✅ Dashboard layout with 4 metric cards  
✅ Scraping activity line chart (7 days)  
✅ Active queue status table  
✅ Retailer status grid  
✅ Auto-refresh toggle  
✅ Responsive design for mobile/tablet  
✅ Loading states and error handling  

### Excludes
❌ Historical data beyond 7 days (defer to analytics)  
❌ Customizable dashboard widgets  
❌ Export dashboard data  
❌ Real-time WebSocket updates (use polling for now)  
❌ Drill-down into specific time periods  
❌ Alerting/notifications (covered in F12)  

---

## Technical Notes

### Tech Stack
- **API Route**: `/api/dashboard/overview` (GET)
- **State Management**: React Query for data fetching
- **Charts**: Recharts library
- **UI Components**: shadcn/ui cards, skeleton loaders
- **Styling**: Tailwind CSS

### Database Queries
```typescript
// Dashboard metrics - single query with aggregations
const metrics = await prisma.$transaction([
  prisma.products.count(),
  prisma.categories.count(),
  prisma.brands.count(),
  // Worker count from active queue tasks
  prisma.scraping_queue.groupBy({
    by: ['worker_id'],
    where: { status: 'in_progress', worker_id: { not: null } }
  })
]);

// Scraping activity - 7 day aggregation
const activity = await prisma.products.groupBy({
  by: ['retailer_id', 'created_at'],
  _count: true,
  where: {
    created_at: { gte: sevenDaysAgo }
  }
});

// Queue stats - per queue type
const queueStats = await prisma.$transaction([
  // Product queue
  prisma.scraping_queue.groupBy({
    by: ['status'],
    _count: true
  }),
  // Category URL queue  
  prisma.category_url_scraping_queue.groupBy({
    by: ['queue_status'],
    _count: true
  }),
  // Category queue
  prisma.category_scraping_queue.groupBy({
    by: ['queue_status'],
    _count: true
  })
]);
```

### Polling Strategy
- Use React Query's `refetchInterval` option
- Default: 5 seconds for queue stats, 30 seconds for metrics
- Pause polling when tab is not visible
- User can toggle auto-refresh on/off

---

## Dependencies

**Required Before Starting**:
- F01: Authentication system must be complete
- Database schema (already exists)
- Prisma client configured

**External Dependencies**:
- Recharts (^2.12.0)
- React Query (^5.0.0)
- shadcn/ui components

---

## Acceptance Testing Checklist

- [ ] Dashboard loads successfully after login
- [ ] All 4 metric cards display correct counts
- [ ] Percentage changes calculate correctly
- [ ] Line chart renders with 7 days of data
- [ ] Chart tooltips show on hover
- [ ] Queue table shows all 3 queues
- [ ] Failed queue items highlight in red
- [ ] Retailer cards display all retailers
- [ ] Warning indicator shows when failures > 10
- [ ] Auto-refresh updates data every 5 seconds
- [ ] Toggle switch stops/starts auto-refresh
- [ ] Dashboard is responsive on mobile (320px width)
- [ ] Loading skeletons appear during data fetch
- [ ] Error states display if API fails
- [ ] Navigation links work (click queue row, retailer card)

---

## Related Documentation

- Main Spec: `/docs/NEXTJS_ADMIN_SPEC.md` (lines 94-137)
- API Design: `/docs/NEXTJS_ADMIN_SPEC.md` (lines 833-878)
- Tech Stack: `/docs/NEXTJS_ADMIN_SPEC.md` (lines 9-28)

---

## Ready for Specification

To create the full specification for this feature, run:

```bash
/speckit.specify docs/features/feature-02-dashboard.md
```

Or use the quick-start script:

```bash
cd docs/features
./quick-start.sh F02
```
