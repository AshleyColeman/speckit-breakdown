# Feature F11: Retailer & Brand Management

**Priority**: P3 (Medium - Phase 3)  
**Business Value**: 5/10  
**Estimated Effort**: 1.5 weeks  
**Dependencies**: F01 (Authentication)

---

## Feature Description

Management interface for retailers and brands including listing, viewing, editing, and viewing statistics. Provides visibility into retailer/brand performance, product counts, and scraping activity. Basic CRUD operations with relationship awareness.

---

## User Stories

### US1: View Retailers List
**As an** admin user  
**I want to** see a list of all retailers with key statistics  
**So that** I can manage retailer data and see performance at a glance

**Acceptance Criteria**:
- Table displays all retailers with columns:
  - Retailer name
  - Base URL
  - Total products
  - Total categories
  - Active status (enabled/disabled toggle)
  - Last scrape date
  - Success rate (%)
- Sortable columns (name, product count, success rate)
- Search by retailer name
- "Add Retailer" button (opens form modal)
- Click row to view retailer detail page

---

### US2: View and Edit Retailer Details
**As an** admin user  
**I want to** view and edit detailed information about a retailer  
**So that** I can manage retailer configuration and troubleshoot issues

**Acceptance Criteria**:
- Retailer detail page shows:
  - Retailer name (editable inline)
  - Base URL (editable inline)
  - Enabled status (toggle switch)
  - Created and updated timestamps
  - Configuration: selectors, rate limits (JSONB field, expandable editor)
- Statistics section:
  - Total products scraped
  - Total categories
  - Success rate (last 30 days)
  - Average scrape time per product
  - Failed scrapes count
- Recent activity feed (last 20 scrape operations)
- "View All Products" button (navigates to filtered product list)
- "View All Categories" button (navigates to filtered category list)

---

### US3: View Brands List
**As an** admin user  
**I want to** see a list of all brands with product counts  
**So that** I can manage brand data

**Acceptance Criteria**:
- Table displays all brands with columns:
  - Brand name
  - Logo (thumbnail)
  - Product count
  - Retailers carrying brand
  - Created date
- Sortable by name, product count
- Search by brand name
- Filter by retailer
- "Add Brand" button (opens form modal)
- Click row to view brand detail page

---

## Success Criteria

### Functional
- ✅ Retailer list displays all retailers with correct stats
- ✅ Brand list displays all brands with correct product counts
- ✅ Edit operations save to database
- ✅ Statistics calculations are accurate
- ✅ Navigation links work (view products, categories)

### Performance
- ✅ Retailer list loads in < 1 second
- ✅ Brand list loads in < 1 second
- ✅ Statistics queries optimized (aggregate queries)
- ✅ Inline edits save in < 300ms

### UX
- ✅ Clear visual layout
- ✅ Loading states during data fetch
- ✅ Confirmation for destructive actions
- ✅ Mobile responsive design

---

## Scope

### Includes
✅ Retailers list table with stats  
✅ Retailer detail page  
✅ Retailer editing (name, URL, config)  
✅ Retailer statistics (products, categories, success rate)  
✅ Brands list table  
✅ Brand detail page  
✅ Brand editing (name, logo)  
✅ Add new retailer/brand (basic form)  
✅ Search and filter  
✅ Navigation to related entities  

### Excludes
❌ Retailer deletion (keep all retailers for data integrity)  
❌ Scraper configuration editor (complex JSONB editing)  
❌ Brand merging/deduplication  
❌ Brand website scraping  
❌ Retailer health monitoring alerts  
❌ Historical trend charts  

---

## Technical Notes

### Tech Stack
- **API Routes**:
  - `/api/retailers` (GET, POST)
  - `/api/retailers/[id]` (GET, PUT)
  - `/api/retailers/[id]/stats` (GET statistics)
  - `/api/brands` (GET, POST)
  - `/api/brands/[id]` (GET, PUT)
- **UI Components**: shadcn/ui (Table, Form, Dialog, Badge)

### Retailer Statistics Query
```typescript
// Aggregate retailer stats
const retailerStats = await prisma.retailers.findUnique({
  where: { id: retailerId },
  include: {
    _count: {
      select: {
        products: true,
        categories: true
      }
    }
  }
});

// Success rate calculation
const last30Days = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000);

const scrapeStats = await prisma.scraping_queue.groupBy({
  by: ['status'],
  _count: true,
  where: {
    retailer_id: retailerId,
    created_at: { gte: last30Days }
  }
});

const totalScrapes = scrapeStats.reduce((sum, s) => sum + s._count, 0);
const successfulScrapes = scrapeStats.find(s => s.status === 'completed')?._count || 0;
const successRate = totalScrapes > 0 ? (successfulScrapes / totalScrapes) * 100 : 0;
```

---

## Dependencies

**Required Before Starting**:
- F01: Authentication
- Retailers and brands tables exist
- Product and category relationships established

**External Dependencies**:
- None (uses existing stack)

---

## Acceptance Testing Checklist

- [ ] Retailers list page loads
- [ ] All retailers display in table
- [ ] Product counts accurate
- [ ] Success rate calculates correctly
- [ ] Search by retailer name works
- [ ] Sortable columns work
- [ ] "Add Retailer" button opens modal
- [ ] Retailer form validates inputs
- [ ] New retailer saves successfully
- [ ] Click row navigates to detail page
- [ ] Retailer detail page loads
- [ ] All retailer info displays
- [ ] Inline editing saves changes
- [ ] Toggle switch updates enabled status
- [ ] Statistics section shows correct data
- [ ] Recent activity feed displays
- [ ] "View All Products" navigates correctly
- [ ] "View All Categories" navigates correctly
- [ ] Brands list page loads
- [ ] All brands display with logos
- [ ] Product counts per brand accurate
- [ ] Search by brand name works
- [ ] Filter by retailer works
- [ ] "Add Brand" button opens modal
- [ ] Brand form validates inputs
- [ ] New brand saves successfully
- [ ] Brand detail page loads
- [ ] Brand editing works
- [ ] Mobile layout responsive

---

## Related Documentation

- Main Spec: `/docs/NEXTJS_ADMIN_SPEC.md` (lines 815-828)
- API Routes: `/docs/NEXTJS_ADMIN_SPEC.md` (lines 860-865)

---

## Ready for Specification

To create the full specification for this feature, run:

```bash
/speckit.specify docs/features/feature-11-retailer-brand-mgmt.md
```

Or use the quick-start script:

```bash
cd docs/features
./quick-start.sh F11
```
