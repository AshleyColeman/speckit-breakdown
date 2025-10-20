# Feature F10: Category Detail & Hierarchy View

**Priority**: P2 (High - Phase 2)  
**Business Value**: 6/10  
**Estimated Effort**: 1.5 weeks  
**Dependencies**: F03 (Category Browser)

---

## Feature Description

Detailed category page showing complete category information, hierarchical relationships (parents, children), associated products, category URL products, processing statistics, and queue history. This page provides deep insights into individual categories and their data quality.

---

## User Stories

### US1: View Complete Category Information
**As an** admin user  
**I want to** see all details of a specific category on a dedicated page  
**So that** I can understand its complete state and relationships

**Acceptance Criteria**:
- Page displays:
  - Category name, ID, URL
  - Retailer name and ID
  - Parent category (if exists)
  - Hierarchy depth level
  - Created and updated timestamps
- Status flags with toggle switches:
  - Enabled (yes/no)
  - Processed (yes/no)
  - Products Processed (yes/no)
  - Category URLs Done (yes/no)
- Queue status badge (pending/queued/processing/completed/failed)
- Product counts: Products Found, Products Saved
- Breadcrumb navigation showing full hierarchy path

---

### US2: Visualize Category Hierarchy
**As an** admin user  
**I want to** see the category's position in the hierarchy tree  
**So that** I can understand parent-child relationships

**Acceptance Criteria**:
- Full parent path displayed (e.g., "Beauty > Makeup > Lipstick > Matte Lipstick")
- Each ancestor in path is clickable (navigates to that category)
- "You are here" indicator on current category
- Children categories list (if any) shows:
  - Child category name (clickable)
  - Child category ID
  - Product count per child
- Expandable/collapsible children list
- Visual tree structure with indentation

---

### US3: View Category Processing Statistics
**As an** admin user  
**I want to** see detailed processing statistics for the category  
**So that** I can troubleshoot scraping issues

**Acceptance Criteria**:
- Processing stats section shows:
  - Processing started timestamp
  - Processing ended timestamp
  - Duration (formatted: "45m 23s")
  - Last processed page (e.g., "9 of 9")
  - Retry count
  - Extraction attempts
  - Error message (if any, expandable)
- Queue history timeline:
  - Status change events (queued → in_progress → completed)
  - Timestamps for each change
  - Worker ID for in_progress events
- Visual timeline component

---

### US4: Browse Category URL Products
**As an** admin user  
**I want to** view all category URL products associated with this category  
**So that** I can verify URL extraction completeness

**Acceptance Criteria**:
- "Category Product URLs" section shows table:
  - URL (truncated with full URL on hover)
  - Processed status (✓/⏳/✗)
  - Skip flag
  - Created timestamp
- Table paginated (25 per page)
- "View All" button navigates to filtered category URL products page
- "Export" button downloads CSV of all URLs
- URL click opens in new tab

---

## Success Criteria

### Functional
- ✅ All category data displays correctly
- ✅ Hierarchy path shows accurate parent-child relationships
- ✅ Toggle switches update database
- ✅ Processing stats calculate correctly
- ✅ Queue history timeline shows all state changes
- ✅ Category URL products table loads correctly

### Performance
- ✅ Page loads in < 1 second for categories with 1000+ products
- ✅ Hierarchy query optimized (single query with joins)
- ✅ URL products table loads first 25 instantly

### UX
- ✅ Breadcrumb navigation intuitive
- ✅ Visual hierarchy clear
- ✅ Loading states for async sections
- ✅ Error states for missing data
- ✅ Mobile responsive layout

---

## Scope

### Includes
✅ Complete category information display  
✅ Editable status flags (inline toggles)  
✅ Full hierarchy path with breadcrumbs  
✅ Parent and children categories  
✅ Processing statistics section  
✅ Queue history timeline  
✅ Category URL products table  
✅ Product count and status  
✅ Export category URLs  
✅ Navigation links (parent, children, products)  

### Excludes
❌ Category editing form (name, URL changes)  
❌ Category creation/deletion  
❌ Move category to different parent  
❌ Merge categories  
❌ Category analytics (covered in analytics feature)  
❌ Product list on this page (link to filtered products page instead)  

---

## Technical Notes

### Tech Stack
- **API Routes**:
  - `/api/categories/[id]` (GET category details)
  - `/api/categories/[id]/hierarchy` (GET full hierarchy)
  - `/api/categories/[id]/url-products` (GET paginated URLs)
  - `/api/categories/[id]/history` (GET queue history)
- **UI Components**: shadcn/ui (Card, Badge, Switch, Timeline, Table)

### Category Detail Query
```typescript
const categoryDetail = await prisma.categories.findUnique({
  where: { id: categoryId },
  include: {
    retailers: { select: { id: true, name: true } },
    parent: { select: { id: true, name: true } },
    children: {
      select: { 
        id: true, 
        name: true,
        _count: { select: { product_categories: true } }
      }
    },
    category_scraping_queue: {
      select: {
        queue_status: true,
        processing_started_at: true,
        processing_ended_at: true,
        last_processed_page: true,
        total_pages: true,
        retry_count: true,
        extraction_attempts: true,
        error_message: true
      },
      orderBy: { updated_at: 'desc' },
      take: 1
    },
    _count: {
      select: {
        product_categories: true,
        category_url_products: true
      }
    }
  }
});

// Build full hierarchy path
const buildHierarchyPath = async (categoryId) => {
  const path = [];
  let currentId = categoryId;
  
  while (currentId) {
    const cat = await prisma.categories.findUnique({
      where: { id: currentId },
      select: { id: true, name: true, parent_id: true }
    });
    
    path.unshift(cat);
    currentId = cat.parent_id;
  }
  
  return path;
};
```

### Queue History Query
```typescript
// Get category queue status changes
const queueHistory = await prisma.category_queue_history.findMany({
  where: { category_id: categoryId },
  orderBy: { timestamp: 'asc' },
  select: {
    status: true,
    timestamp: true,
    worker_id: true,
    details: true
  }
});

// Transform to timeline events
const timelineEvents = queueHistory.map(event => ({
  timestamp: event.timestamp,
  label: getStatusLabel(event.status),
  description: event.worker_id 
    ? `Worker: ${event.worker_id}` 
    : undefined,
  icon: getStatusIcon(event.status),
  color: getStatusColor(event.status)
}));
```

---

## Dependencies

**Required Before Starting**:
- F03: Category Browser (navigation source)
- Categories table fully populated
- Queue history tracking (table may need to be created)

**External Dependencies**:
- date-fns (for date formatting)
- Timeline component (custom or library)

---

## Acceptance Testing Checklist

- [ ] Category detail page loads from category browser
- [ ] All category fields display correctly
- [ ] Retailer name and ID shown
- [ ] Parent category displays (if exists)
- [ ] Hierarchy depth is accurate
- [ ] Status toggle switches work (enabled, processed, etc.)
- [ ] Queue status badge displays correctly
- [ ] Product counts accurate (found, saved)
- [ ] Breadcrumb navigation shows full path
- [ ] Breadcrumb links navigate correctly
- [ ] Full parent path displays with separators (>)
- [ ] "You are here" indicator on current category
- [ ] Children categories list displays
- [ ] Child names are clickable
- [ ] Product count per child is accurate
- [ ] Processing stats section shows all fields
- [ ] Duration calculates correctly
- [ ] Last processed page displays
- [ ] Error message expandable (if exists)
- [ ] Queue history timeline renders
- [ ] Timeline shows status changes with timestamps
- [ ] Worker ID displays for in_progress events
- [ ] Category URL products table loads
- [ ] URL truncation works with hover tooltip
- [ ] Processed status icons correct (✓/⏳/✗)
- [ ] "View All" navigates to filtered page
- [ ] "Export" downloads CSV
- [ ] URL click opens in new tab
- [ ] Pagination works on URL products table
- [ ] Mobile layout stacks sections vertically
- [ ] Loading states show during data fetch
- [ ] Error states display if data missing

---

## Related Documentation

- Main Spec: `/docs/NEXTJS_ADMIN_SPEC.md` (lines 252-343)
- Category Browser: `/docs/NEXTJS_ADMIN_SPEC.md` (lines 140-250)
- API Routes: `/docs/NEXTJS_ADMIN_SPEC.md` (lines 836-842)

---

## Ready for Specification

To create the full specification for this feature, run:

```bash
/speckit.specify docs/features/feature-10-category-detail.md
```

Or use the quick-start script:

```bash
cd docs/features
./quick-start.sh F10
```
