# Feature F09: Bulk Operations & Data Export

**Priority**: P2 (High - Phase 2)  
**Business Value**: 7/10  
**Estimated Effort**: 1.5 weeks  
**Dependencies**: F03 (Category Browser), F04 (Product Browser)

---

## Feature Description

Comprehensive bulk operations system allowing users to select multiple records and perform batch updates, deletions, or exports. Includes multi-format export capabilities (CSV, Excel, JSON) with customizable column selection and data export scheduling.

This feature dramatically improves efficiency when managing large datasets by enabling operations on hundreds or thousands of records simultaneously.

---

## User Stories

### US1: Select Multiple Records for Bulk Operations
**As an** admin user  
**I want to** select multiple products or categories using checkboxes  
**So that** I can perform actions on many records at once

**Acceptance Criteria**:
- Checkbox column on far left of table
- Individual row checkboxes select single records
- "Select All" checkbox in header selects all on current page
- "Select All Pages" option selects all matching filter (shows warning if > 1000 records)
- Selection count badge shows: "23 selected" or "All 1,245 selected"
- "Clear Selection" button deselects all
- Selection persists when changing pages (within session)
- Visual highlighting of selected rows

---

### US2: Perform Bulk Update Operations
**As an** admin user  
**I want to** update multiple records with the same values  
**So that** I can make consistent changes efficiently

**Acceptance Criteria**:
- "Bulk Actions" dropdown appears when items selected
- Available bulk update actions for products:
  - Update Processed Status
  - Add to Category
  - Remove from Category
  - Update Retailer
  - Mark for Review
- Available bulk update actions for categories:
  - Enable/Disable
  - Mark Products Done
  - Reset Queue Status
- Bulk action modal shows:
  - Count of records affected
  - Field(s) to update
  - Confirmation checkbox for destructive actions
- Progress bar for operations affecting > 100 records
- Success notification shows count updated
- Failed updates show error list

---

### US3: Bulk Delete Records
**As an** admin user  
**I want to** delete multiple records at once  
**So that** I can clean up data efficiently

**Acceptance Criteria**:
- "Delete Selected" action in bulk actions dropdown
- Confirmation modal shows:
  - Count of records to delete
  - Warning message about permanent deletion
  - "Type DELETE to confirm" input field (for safety)
- Soft delete by default (sets deleted_at timestamp)
- Hard delete option (admin only, requires second confirmation)
- Progress indicator for large deletions
- Success message shows count deleted
- Error handling if some deletions fail

---

### US4: Export Data in Multiple Formats
**As an** admin user  
**I want to** export selected records (or all) in various formats  
**So that** I can analyze data externally or share with stakeholders

**Acceptance Criteria**:
- "Export" button/dropdown with format options:
  - CSV (simple, compatible)
  - Excel (.xlsx with formatting)
  - JSON (complete data with relationships)
- Export options modal allows:
  - Column selection (checkboxes for which fields to include)
  - "Export Selected" (only checked records) or "Export All" (all matching filters)
  - File name customization
- Export respects current filters
- Progress indicator for large exports (> 10,000 records)
- Download triggers automatically when ready
- Export history tracked (who, when, what)

---

## Success Criteria

### Functional
- ✅ Checkbox selection works across pages
- ✅ Bulk updates apply correctly to all selected records
- ✅ Exports contain accurate data in correct format
- ✅ Delete confirmation prevents accidental data loss
- ✅ Progress bars show for long-running operations

### Performance
- ✅ Selecting 1000+ records responds in < 200ms
- ✅ Bulk update processes 1000 records in < 10 seconds
- ✅ CSV export generates 10,000 records in < 5 seconds
- ✅ Excel export generates 10,000 records in < 15 seconds

### UX
- ✅ Clear feedback during bulk operations
- ✅ Cancellable long-running operations
- ✅ Error messages are actionable
- ✅ Export downloads automatically
- ✅ Selection persists during pagination

---

## Scope

### Includes
✅ Multi-select checkboxes with "Select All"  
✅ Bulk update modal with field selection  
✅ Bulk delete with confirmation  
✅ Export to CSV, Excel, JSON  
✅ Column selection for exports  
✅ Export selected or all (with filters)  
✅ Progress indicators for long operations  
✅ Export history tracking  
✅ Soft delete by default  
✅ Error handling with partial failure recovery  

### Excludes
❌ Scheduled exports (daily/weekly automation)  
❌ Email export delivery  
❌ Cloud storage integration (S3, Drive)  
❌ PDF export format  
❌ Import data from files (bulk create)  
❌ Undo bulk operations  
❌ Bulk edit via spreadsheet upload  

---

## Technical Notes

### Tech Stack
- **API Routes**:
  - `/api/products/bulk-update` (PATCH)
  - `/api/products/bulk-delete` (DELETE)
  - `/api/products/export` (POST - generates file)
  - `/api/categories/bulk-update` (PATCH)
  - `/api/categories/export` (POST)
- **Export Libraries**:
  - CSV: `csv-stringify` or `papaparse`
  - Excel: `exceljs` or `xlsx`
  - JSON: Native JSON.stringify
- **UI Components**: shadcn/ui (Checkbox, Dialog, Progress, Select)

### Bulk Update Implementation
```typescript
// Bulk update API endpoint
async function bulkUpdateProducts(req: Request) {
  const { ids, updates } = req.body;
  
  // Validate inputs
  if (!ids || !Array.isArray(ids) || ids.length === 0) {
    return { error: 'No IDs provided' };
  }
  
  // Perform update in transaction
  const result = await prisma.$transaction(async (tx) => {
    const updated = await tx.products.updateMany({
      where: { id: { in: ids } },
      data: updates
    });
    
    // Log bulk operation
    await tx.audit_log.create({
      data: {
        user_id: req.user.id,
        action: 'bulk_update',
        entity: 'products',
        affected_count: updated.count,
        changes: updates
      }
    });
    
    return updated;
  });
  
  return { success: true, count: result.count };
}
```

### Export Implementation (CSV)
```typescript
import { stringify } from 'csv-stringify/sync';

async function exportProductsToCSV(filters, selectedColumns) {
  // Fetch data with filters
  const products = await prisma.products.findMany({
    where: buildWhereClause(filters),
    include: {
      brands: true,
      retailers: true,
      product_categories: { include: { categories: true } }
    }
  });
  
  // Transform to flat structure
  const rows = products.map(p => ({
    id: p.id,
    name: p.name,
    brand: p.brands?.name,
    retailer: p.retailers?.name,
    price: p.price,
    categories: p.product_categories.map(pc => pc.categories.name).join('; '),
    created_at: p.created_at.toISOString()
  }));
  
  // Filter columns
  const filteredRows = rows.map(row => 
    Object.fromEntries(
      Object.entries(row).filter(([key]) => selectedColumns.includes(key))
    )
  );
  
  // Generate CSV
  const csv = stringify(filteredRows, { header: true });
  
  return csv;
}
```

### Export Implementation (Excel)
```typescript
import ExcelJS from 'exceljs';

async function exportProductsToExcel(filters, selectedColumns) {
  const products = await fetchProducts(filters);
  
  const workbook = new ExcelJS.Workbook();
  const worksheet = workbook.addWorksheet('Products');
  
  // Define columns
  worksheet.columns = selectedColumns.map(col => ({
    header: col.label,
    key: col.key,
    width: col.width || 20
  }));
  
  // Style header row
  worksheet.getRow(1).font = { bold: true };
  worksheet.getRow(1).fill = {
    type: 'pattern',
    pattern: 'solid',
    fgColor: { argb: 'FFE0E0E0' }
  };
  
  // Add data rows
  products.forEach(product => {
    worksheet.addRow(transformProductToRow(product));
  });
  
  // Generate buffer
  const buffer = await workbook.xlsx.writeBuffer();
  
  return buffer;
}
```

---

## Dependencies

**Required Before Starting**:
- F03: Category Browser
- F04: Product Browser
- Audit log table for tracking bulk operations

**External Dependencies**:
- csv-stringify (^6.0.0) OR papaparse (^5.4.0)
- exceljs (^4.4.0) OR xlsx (^0.18.0)

---

## Acceptance Testing Checklist

- [ ] Individual row checkboxes select records
- [ ] "Select All" checkbox selects all on page
- [ ] "Select All Pages" option selects all (with warning)
- [ ] Selection count badge displays correctly
- [ ] "Clear Selection" deselects all
- [ ] Selected rows visually highlighted
- [ ] Selection persists when paginating
- [ ] "Bulk Actions" dropdown appears when items selected
- [ ] Bulk update modal opens with correct fields
- [ ] Bulk update applies to all selected records
- [ ] Progress bar shows for large bulk updates
- [ ] Success notification shows count updated
- [ ] Bulk delete requires confirmation
- [ ] "Type DELETE to confirm" validation works
- [ ] Soft delete sets deleted_at timestamp
- [ ] Hard delete option requires admin role
- [ ] Export dropdown shows all format options (CSV/Excel/JSON)
- [ ] Export options modal allows column selection
- [ ] "Export Selected" exports only checked records
- [ ] "Export All" exports all matching filters
- [ ] File name customization works
- [ ] CSV export downloads with correct data
- [ ] Excel export downloads with formatting
- [ ] JSON export includes relationships
- [ ] Export progress indicator shows for large datasets
- [ ] Export history records operation
- [ ] Cancellation stops long-running operations
- [ ] Partial failures show error list
- [ ] Mobile layout shows bulk actions appropriately

---

## Related Documentation

- Main Spec: `/docs/NEXTJS_ADMIN_SPEC.md` (lines 238-244, 1029-1034)
- Bulk Edit Modal: `/docs/NEXTJS_ADMIN_SPEC.md` (lines 1006-1027)
- Category Bulk Ops: `/docs/NEXTJS_ADMIN_SPEC.md` (lines 238-244)

---

## Ready for Specification

To create the full specification for this feature, run:

```bash
/speckit.specify docs/features/feature-09-bulk-operations.md
```

Or use the quick-start script:

```bash
cd docs/features
./quick-start.sh F09
```
