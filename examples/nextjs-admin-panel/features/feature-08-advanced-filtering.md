# Feature F08: Advanced Filtering & Saved Views

**Priority**: P2 (High - Phase 2)  
**Business Value**: 7/10  
**Estimated Effort**: 1.5 weeks  
**Dependencies**: F03 (Category Browser), F04 (Product Browser)

---

## Feature Description

Advanced filtering system with complex query builders, URL state persistence for shareable links, and saved view functionality. Users can create sophisticated filter combinations across multiple criteria, save their favorite views, and share filtered results via URLs.

This feature transforms basic filtering into a power-user tool for data analysis and workflow optimization.

---

## User Stories

### US1: Create Complex Multi-Criteria Filters
**As an** admin user  
**I want to** combine multiple filter criteria with AND/OR logic  
**So that** I can find exactly the data I need

**Acceptance Criteria**:
- "Advanced Filters" panel with expandable sections
- Available filter types:
  - Text search (name, description, SKU)
  - Numeric range (price, rating, ingredient count)
  - Date range (created, updated)
  - Multi-select (retailer, brand, category)
  - Boolean flags (processed, has ingredients, has images)
- Filters can be combined (all use AND logic)
- "Add Filter" button to create additional filter rows
- "Remove Filter" (X) button on each filter
- Real-time result count updates as filters change
- "Apply Filters" button triggers search

---

### US2: Share Filtered Views via URL
**As an** admin user  
**I want to** share filtered views with colleagues via URL  
**So that** they can see the same data without recreating filters

**Acceptance Criteria**:
- All active filters encoded in URL query parameters
- URL updates automatically when filters change (debounced)
- Opening a URL with filters automatically applies them
- "Copy Link" button copies current filtered view URL
- URL remains under 2000 characters (compresses if needed)
- Browser back/forward buttons work with filter history
- Shareable URL example: `?retailer=1,2&price_min=50&price_max=200&has_ingredients=true`

---

### US3: Save Custom Filter Views
**As an** admin user  
**I want to** save commonly-used filter combinations as named views  
**So that** I can quickly access them without recreating filters

**Acceptance Criteria**:
- "Save View" button opens modal with:
  - View name input (required)
  - View description (optional)
  - Make default view checkbox
- Saved views appear in sidebar/dropdown menu
- Clicking saved view applies all filters instantly
- "Edit View" updates filter criteria
- "Delete View" removes saved view (with confirmation)
- Views are per-user (not shared globally)
- Maximum 20 saved views per user

---

### US4: Use Pre-built Filter Templates
**As an** admin user  
**I want to** access pre-built filter templates for common use cases  
**So that** I can quickly access relevant data views

**Acceptance Criteria**:
- Filter template dropdown with options:
  - "High-risk Products" (unsafe ingredients, safety score < 5)
  - "Missing Data" (no images OR no ingredients OR no price)
  - "Recent Scrapes" (created in last 7 days)
  - "Pending Review" (processed=false)
  - "Failed Scrapes" (processing attempts > 3)
- Selecting template applies filters instantly
- Templates can be modified after applying
- "Clear Filters" resets to default view

---

## Success Criteria

### Functional
- ✅ All filter types work correctly
- ✅ Filters combine properly (AND logic)
- ✅ URL state updates with all active filters
- ✅ Saved views persist across sessions
- ✅ Pre-built templates apply correct filters
- ✅ Browser navigation works with filter history

### Performance
- ✅ Filter application returns results in < 500ms
- ✅ URL encoding/decoding happens instantly
- ✅ Saved views load in < 100ms
- ✅ Real-time result count updates in < 200ms

### UX
- ✅ Filter panel is collapsible (save screen space)
- ✅ Clear visual feedback for active filters
- ✅ "Active Filters" badge shows count
- ✅ One-click to clear all filters
- ✅ Intuitive filter builder interface

---

## Scope

### Includes
✅ Advanced filter panel with multiple criteria types  
✅ Text, numeric range, date range, multi-select filters  
✅ URL state persistence (query parameters)  
✅ Shareable filtered view URLs  
✅ Save custom filter views (per user)  
✅ Edit and delete saved views  
✅ Pre-built filter templates (5 common use cases)  
✅ Real-time result count preview  
✅ Active filter badges  
✅ Clear all filters button  

### Excludes
❌ OR logic between filters (only AND supported)  
❌ Global shared views (admin-defined for all users)  
❌ Filter history (undo/redo filter changes)  
❌ Scheduled filter reports (email results daily)  
❌ Filter presets based on user role  
❌ Export filter definition (JSON download)  

---

## Technical Notes

### Tech Stack
- **API Routes**:
  - `/api/filters/saved-views` (GET, POST, PUT, DELETE)
  - `/api/filters/templates` (GET pre-built templates)
- **State Management**: 
  - URL state: next/navigation (useSearchParams, useRouter)
  - Local state: React useState
  - Saved views: React Query + database
- **UI Components**: shadcn/ui (Select, Input, DatePicker, Badge, Popover)

### URL State Management
```typescript
// Encode filters to URL
const encodeFiltersToURL = (filters) => {
  const params = new URLSearchParams();
  
  Object.entries(filters).forEach(([key, value]) => {
    if (Array.isArray(value)) {
      params.set(key, value.join(','));
    } else if (value !== null && value !== undefined) {
      params.set(key, String(value));
    }
  });
  
  return params.toString();
};

// Decode URL to filters
const decodeURLToFilters = (searchParams) => {
  const filters = {};
  
  for (const [key, value] of searchParams.entries()) {
    // Handle arrays (e.g., retailer=1,2,3)
    if (key === 'retailer' || key === 'brand' || key === 'category') {
      filters[key] = value.split(',').map(Number);
    } 
    // Handle booleans
    else if (value === 'true' || value === 'false') {
      filters[key] = value === 'true';
    }
    // Handle numbers
    else if (!isNaN(Number(value))) {
      filters[key] = Number(value);
    }
    // Handle strings
    else {
      filters[key] = value;
    }
  }
  
  return filters;
};
```

### Saved Views Database Schema
```typescript
// saved_views table
{
  id: number,
  user_id: number, // references account_user
  view_name: string,
  view_description: string?,
  filter_criteria: jsonb, // stores filter object
  is_default: boolean,
  entity_type: enum('products', 'categories'), // which page
  created_at: timestamp,
  updated_at: timestamp
}
```

### Filter Template Definitions
```typescript
const filterTemplates = {
  'high-risk-products': {
    name: 'High-risk Products',
    filters: {
      has_ingredients: true,
      safety_score_max: 5
    }
  },
  'missing-data': {
    name: 'Missing Data',
    filters: {
      OR: [
        { image_url: null },
        { price: null },
        { has_ingredients: false }
      ]
    }
  },
  'recent-scrapes': {
    name: 'Recent Scrapes',
    filters: {
      created_after: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
    }
  },
  'pending-review': {
    name: 'Pending Review',
    filters: {
      processed: false
    }
  },
  'failed-scrapes': {
    name: 'Failed Scrapes',
    filters: {
      attempts_min: 3,
      processed: false
    }
  }
};
```

---

## Dependencies

**Required Before Starting**:
- F03: Category Browser (basic filtering exists)
- F04: Product Browser (basic filtering exists)
- Database table for saved views (migration needed)

**External Dependencies**:
- date-fns (for date manipulation)
- shadcn/ui components

---

## Acceptance Testing Checklist

- [ ] Advanced filter panel opens/closes correctly
- [ ] Text search filter works
- [ ] Price range filter works (min/max)
- [ ] Date range filter works (created/updated)
- [ ] Multi-select filters work (retailer, brand, category)
- [ ] Boolean flag filters work (processed, has ingredients)
- [ ] "Add Filter" button creates new filter row
- [ ] "Remove Filter" button deletes filter
- [ ] Result count updates in real-time
- [ ] "Apply Filters" triggers search
- [ ] URL updates with all active filters
- [ ] Opening URL with filters applies them correctly
- [ ] "Copy Link" button copies filtered URL to clipboard
- [ ] Browser back button restores previous filters
- [ ] Browser forward button works
- [ ] "Save View" modal opens
- [ ] View name is required (validation)
- [ ] Saved view appears in dropdown/sidebar
- [ ] Clicking saved view applies filters instantly
- [ ] "Edit View" updates filter criteria
- [ ] "Delete View" removes saved view (with confirmation)
- [ ] "Make Default" checkbox sets default view
- [ ] Filter templates dropdown shows all 5 templates
- [ ] Selecting template applies correct filters
- [ ] Templates can be modified after applying
- [ ] "Clear Filters" resets to default view
- [ ] Active filters badge shows count
- [ ] Maximum 20 saved views enforced
- [ ] Views are per-user (not visible to others)

---

## Related Documentation

- Main Spec: `/docs/NEXTJS_ADMIN_SPEC.md` (lines 196-236, 418-455)
- URL State Management: `/docs/NEXTJS_ADMIN_SPEC.md` (lines 963-978)
- Saved Views: `/docs/NEXTJS_ADMIN_SPEC.md` (lines 1035-1040)

---

## Ready for Specification

To create the full specification for this feature, run:

```bash
/speckit.specify docs/features/feature-08-advanced-filtering.md
```

Or use the quick-start script:

```bash
cd docs/features
./quick-start.sh F08
```
