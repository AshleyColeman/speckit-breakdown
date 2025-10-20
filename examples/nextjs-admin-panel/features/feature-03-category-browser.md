# Feature F03: Category Browser & Management

**Priority**: P1 (Critical - MVP)  
**Business Value**: 9/10  
**Estimated Effort**: 2.5 weeks  
**Dependencies**: F01 (Authentication)

---

## Feature Description

A comprehensive category management interface supporting both tree and table views of the category hierarchy. Users can browse, search, filter, and perform bulk operations on categories across all retailers. The interface handles hierarchical data efficiently while providing powerful filtering capabilities for processing status, queue states, and relationships.

This feature is essential for understanding product organization and managing the category scraping pipeline.

---

## User Stories

### US1: Browse Categories in Tree and Table Views
**As an** admin user  
**I want to** view categories in both tree (hierarchical) and table (flat) views  
**So that** I can understand the category structure and find specific categories easily

**Acceptance Criteria**:
- View toggle allows switching between Tree View and Table View
- Tree view displays parent-child relationships with indentation and icons
- Table view shows flat list with "Hierarchy Path" column (e.g., "Beauty › Makeup › Lipstick")
- Categories display: ID, Name, Retailer, Depth, Has URL, Products count, Status flags
- Both views support pagination (50 items per page default)
- View preference is saved per user session

---

### US2: Search and Filter Categories
**As an** admin user  
**I want to** search and filter categories by multiple criteria  
**So that** I can find specific categories quickly

**Acceptance Criteria**:
- Text search filters by category name and URL (case-insensitive)
- Filter options include:
  - Retailer (multi-select)
  - Processing status (processed/not processed)
  - Enabled status (yes/no)
  - Has URL (yes/no)
  - Products done status
  - Queue status (pending, queued, processing, completed, failed)
- Filters can be combined (AND logic)
- "Clear Filters" button resets all filters
- Result count displays (e.g., "Showing 245 results")
- Filters persist in URL query parameters

---

### US3: Sort Categories
**As an** admin user  
**I want to** sort categories by different columns  
**So that** I can organize data meaningfully

**Acceptance Criteria**:
- Sortable columns: ID, Name, Depth, Products count, Created date
- Click column header to sort (ascending first click, descending second click)
- Sort indicator (▲/▼) shows current sort direction
- Default sort: by hierarchy path (parent_path ASC, then name ASC)
- Sort persists in URL query parameters

---

### US4: Inline Edit Category Properties
**As an** admin user  
**I want to** edit category properties inline without opening a separate modal  
**So that** I can make quick updates efficiently

**Acceptance Criteria**:
- Click category name to edit inline (opens text input)
- Toggle switches for boolean fields (enabled, processed, products_done)
- Save on Enter key or blur, cancel on Escape
- Visual feedback during save (loading spinner)
- Success/error toast notification after save
- Optimistic UI updates (immediate visual change)

---

### US5: Perform Bulk Operations on Categories
**As an** admin user  
**I want to** select multiple categories and perform bulk actions  
**So that** I can manage many categories at once

**Acceptance Criteria**:
- Checkbox column allows selecting individual categories
- "Select All" checkbox selects all on current page
- Bulk actions available:
  - Enable Selected
  - Disable Selected
  - Mark Products Done
  - Reset Queue Status (to "pending")
  - Export Selected (CSV)
- Bulk action button shows count (e.g., "Enable 15 Selected")
- Confirmation dialog for destructive actions
- Progress indicator for long-running operations
- Success message shows count affected (e.g., "23 categories updated")

---

## Success Criteria

### Functional
- ✅ Table displays all categories with correct hierarchical relationships
- ✅ Tree view renders parent-child structure accurately
- ✅ All filters work correctly and can be combined
- ✅ Inline editing saves changes to database
- ✅ Bulk operations update multiple records correctly
- ✅ URL state persistence allows sharing filtered views

### Performance
- ✅ Initial page load < 2 seconds for 1000+ categories
- ✅ Filtering updates results in < 500ms
- ✅ Tree view renders 500+ categories without lag
- ✅ Bulk update processes 100 categories in < 3 seconds

### UX
- ✅ Loading skeletons during data fetch
- ✅ Empty state message when no results
- ✅ Clear visual hierarchy in tree view (indentation, icons)
- ✅ Responsive design (collapses columns on mobile)
- ✅ Keyboard navigation support (tab through fields, arrow keys in table)

---

## Scope

### Includes
✅ Tree and table view toggle  
✅ Hierarchical data display with parent paths  
✅ Full-text search (name, URL)  
✅ Multi-criteria filtering (retailer, status, queue, etc.)  
✅ Column sorting  
✅ Inline editing (name, boolean fields)  
✅ Bulk operations (enable/disable, mark done, reset queue)  
✅ CSV export (selected or all)  
✅ Pagination (with page size options)  
✅ URL state persistence  

### Excludes
❌ Drag-and-drop category reordering  
❌ Category creation/deletion (covered in admin panel)  
❌ Advanced tree operations (move category to different parent)  
❌ Category detail page (covered in F10)  
❌ Visual tree diagram/chart  
❌ Import categories from CSV  

---

## Technical Notes

### Tech Stack
- **API Routes**: 
  - `/api/categories` (GET, POST, PATCH for bulk)
  - `/api/categories/[id]` (PUT for single update)
- **Table Library**: TanStack Table v8
- **State Management**: React Query + URL state (next/navigation)
- **UI Components**: shadcn/ui (Table, Checkbox, Switch, Select, Badge)

### Database Query Optimization
```typescript
// Efficient category query with counts and relationships
const categories = await prisma.categories.findMany({
  where: {
    // Apply filters
    AND: [
      searchTerm ? { 
        OR: [
          { name: { contains: searchTerm, mode: 'insensitive' } },
          { category_url: { contains: searchTerm, mode: 'insensitive' } }
        ]
      } : {},
      retailerIds?.length ? { retailer_id: { in: retailerIds } } : {},
      processed !== null ? { processed } : {},
      enabled !== null ? { enabled } : {},
      // ... other filters
    ]
  },
  include: {
    retailers: { select: { name: true } },
    parent: { select: { id: true, name: true } },
    _count: {
      select: { 
        product_categories: true,
        category_url_products: true 
      }
    }
  },
  orderBy: [
    { parent_path: 'asc' },
    { name: 'asc' }
  ],
  skip: (page - 1) * pageSize,
  take: pageSize
});
```

### Tree View Rendering
- Use `parent_path` field to determine indentation level
- Recursive component not needed (flat list with indentation)
- Use CSS for visual hierarchy (margin-left based on depth)

### URL State Management
```typescript
// Sync filters with URL
const router = useRouter();
const searchParams = useSearchParams();

const updateFilters = (newFilters) => {
  const params = new URLSearchParams(searchParams);
  Object.entries(newFilters).forEach(([key, value]) => {
    if (value) params.set(key, value);
    else params.delete(key);
  });
  router.push(`?${params.toString()}`);
};
```

---

## Dependencies

**Required Before Starting**:
- F01: Authentication & authorization
- Prisma schema (categories table exists)
- TanStack Table installed

**External Dependencies**:
- @tanstack/react-table (^8.0.0)
- @tanstack/react-query (^5.0.0)
- shadcn/ui components

---

## Acceptance Testing Checklist

- [ ] Tree view displays categories with correct indentation
- [ ] Table view shows all columns with correct data
- [ ] View toggle switches between tree and table
- [ ] Search box filters by name and URL
- [ ] All filter dropdowns work (retailer, status, etc.)
- [ ] Multiple filters can be combined
- [ ] Clear Filters button resets all
- [ ] Result count updates with filters
- [ ] Clicking column header sorts data
- [ ] Sort direction indicator shows (▲/▼)
- [ ] Inline edit saves category name
- [ ] Toggle switches save boolean fields
- [ ] Checkbox selects individual categories
- [ ] Select All checkbox works
- [ ] Bulk Enable updates multiple categories
- [ ] Bulk Disable works
- [ ] Mark Products Done bulk action works
- [ ] Reset Queue Status works
- [ ] Export CSV downloads file with correct data
- [ ] Pagination controls work (next/previous)
- [ ] Page size selector works (25/50/100)
- [ ] URL updates with filters (shareable links)
- [ ] Mobile layout collapses columns appropriately
- [ ] Loading skeletons show during data fetch
- [ ] Error states display if API fails

---

## Related Documentation

- Main Spec: `/docs/NEXTJS_ADMIN_SPEC.md` (lines 140-250)
- Category Detail Page: `/docs/NEXTJS_ADMIN_SPEC.md` (lines 252-343)
- API Design: `/docs/NEXTJS_ADMIN_SPEC.md` (lines 836-842)

---

## Ready for Specification

To create the full specification for this feature, run:

```bash
/speckit.specify docs/features/feature-03-category-browser.md
```

Or use the quick-start script:

```bash
cd docs/features
./quick-start.sh F03
```
