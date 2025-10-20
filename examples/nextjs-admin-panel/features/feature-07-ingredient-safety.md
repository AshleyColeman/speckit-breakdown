# Feature F07: Ingredient Safety Analysis

**Priority**: P2 (High - Phase 2)  
**Business Value**: 8/10  
**Estimated Effort**: 2 weeks  
**Dependencies**: F01 (Authentication), F05 (Product Detail)

---

## Feature Description

A comprehensive ingredient safety analysis system that displays ingredient lists with safety ratings, concern flags, banned substance alerts, and suggested safer alternatives. This feature transforms raw ingredient data into actionable health and safety insights for users.

The ingredient tab on product detail pages will show detailed safety scores, color-coded risk indicators, concentration percentages, known concerns, and alternatives for problematic ingredients.

---

## User Stories

### US1: View Product Ingredient List with Safety Ratings
**As an** admin user  
**I want to** see a product's complete ingredient list with individual safety scores  
**So that** I can assess the overall safety profile of a product

**Acceptance Criteria**:
- Ingredients displayed in order (as they appear on product)
- Each ingredient shows:
  - Name (with synonyms expandable)
  - Concentration percentage (if available)
  - Safety score (1-10 scale)
  - Safety color indicator (🟢 Safe 8-10, 🟡 Moderate 5-7, 🔴 Unsafe 1-4)
  - Purpose/function (e.g., "Solvent", "Preservative")
- Overall product safety score calculated and prominently displayed
- Safety score methodology explained (tooltip or info icon)

---

### US2: Identify Ingredient Concerns and Warnings
**As an** admin user  
**I want to** see flagged concerns for each ingredient (allergens, irritants, environmental impact)  
**So that** I can understand specific risks

**Acceptance Criteria**:
- Concern badges display for each ingredient:
  - ⚠️ Allergy potential (High/Medium/Low)
  - 🔴 Irritant (High/Medium/Low)
  - 🌍 Environmental concerns
  - 🚫 Banned/restricted in certain regions
- Expandable section shows detailed concern explanations
- Links to scientific studies (if available)
- "View Studies" link opens references

---

### US3: View Banned Ingredient Alerts
**As an** admin user  
**I want to** see clear warnings when products contain banned or restricted ingredients  
**So that** I can flag products for review or removal

**Acceptance Criteria**:
- Prominent alert banner if any ingredient is banned/restricted
- Banner shows: ingredient name, regions where banned, restriction level
- Example: "⚠️ Warning! Parabens (Methyl) - Banned in EU, Restricted in US"
- Alert is color-coded (red for banned, yellow for restricted)
- Product marked with "Contains Banned Ingredients" flag in database
- Export function includes banned ingredient flag

---

### US4: Analyze Safety Distribution
**As an** admin user  
**I want to** see a summary of ingredient safety distribution  
**So that** I can quickly assess overall product safety profile

**Acceptance Criteria**:
- Safety distribution chart/summary shows:
  - Count of Safe ingredients (8-10 score)
  - Count of Moderate ingredients (5-7 score)
  - Count of Unsafe ingredients (1-4 score)
  - Percentage breakdown
- Visual chart (pie or bar chart)
- Concerns summary: count by type (Environmental, Allergy, Irritant)
- Total banned ingredients count highlighted

---

### US5: Suggest Safer Ingredient Alternatives
**As an** admin user  
**I want to** see suggested safer alternatives for problematic ingredients  
**So that** I can recommend better product choices to customers

**Acceptance Criteria**:
- For each ingredient with score < 7, show "View Alternatives" button
- Alternatives section displays:
  - Alternative ingredient name
  - Safety improvement (e.g., "Score: 9.2 vs 4.1 - 126% safer")
  - Used in N products (link to products using alternative)
- Sortable by safety score improvement
- "Suggest Alternative" action flags product for reformulation recommendation

---

## Success Criteria

### Functional
- ✅ All product ingredients display with correct safety scores
- ✅ Color indicators match safety thresholds accurately
- ✅ Banned ingredient warnings trigger correctly
- ✅ Alternatives shown only for ingredients with safety concerns
- ✅ Safety distribution calculates correctly

### Performance
- ✅ Ingredient tab loads in < 1 second for products with 50+ ingredients
- ✅ Safety score calculation happens server-side (not blocking UI)
- ✅ Alternative ingredient lookup cached (< 200ms response)

### UX
- ✅ Color-blind accessible (not relying solely on color)
- ✅ Expandable sections for detailed information
- ✅ Mobile responsive layout
- ✅ Loading states for async operations
- ✅ Tooltips explain scoring methodology

---

## Scope

### Includes
✅ Ingredient list display with safety scores  
✅ Safety color indicators (green/yellow/red)  
✅ Concern badges (allergy, irritant, environmental)  
✅ Banned ingredient alerts  
✅ Safety distribution summary/chart  
✅ Ingredient purpose/function display  
✅ Synonym/alternative names  
✅ Safer alternative suggestions  
✅ Study references (links)  
✅ Overall product safety score  

### Excludes
❌ Ingredient database management (CRUD operations)  
❌ Custom safety score algorithm editing  
❌ User-submitted ingredient reviews  
❌ Real-time ingredient research API integration  
❌ Ingredient interaction analysis (synergies/conflicts)  
❌ Personalized allergen warnings (user profiles)  

---

## Technical Notes

### Tech Stack
- **API Routes**:
  - `/api/products/[id]/ingredients` (GET)
  - `/api/ingredients/[id]/alternatives` (GET)
  - `/api/ingredients/safety-score` (POST calculate)
- **UI Components**: shadcn/ui (Accordion, Badge, Alert, Chart)
- **Charts**: Recharts (for distribution pie chart)

### Database Schema (Existing)
```typescript
// Tables involved:
- product_ingredients (junction table)
- ingredients (ingredient master data)
- ingredient_safety_data (safety scores, concerns)
- ingredient_alternatives (alternative suggestions)
```

### Safety Score Calculation
```typescript
// Example calculation logic
const calculateProductSafetyScore = (ingredients) => {
  const scores = ingredients.map(i => i.safety_score || 5);
  const weightedAvg = scores.reduce((sum, score, idx) => {
    // Higher concentration = more weight
    const weight = ingredients[idx].concentration || 1;
    return sum + (score * weight);
  }, 0) / scores.length;
  
  return {
    overall_score: weightedAvg.toFixed(1),
    overall_color: getColorFromScore(weightedAvg),
    distribution: {
      safe: scores.filter(s => s >= 8).length,
      moderate: scores.filter(s => s >= 5 && s < 8).length,
      unsafe: scores.filter(s => s < 5).length
    }
  };
};
```

### Ingredient Query with Safety Data
```typescript
const productIngredients = await prisma.product_ingredients.findMany({
  where: { product_id: productId },
  include: {
    ingredients: {
      include: {
        ingredient_safety_data: {
          select: {
            safety_score: true,
            concerns: true,
            banned_regions: true,
            restriction_level: true,
            studies_links: true
          }
        },
        ingredient_alternatives: {
          where: { 
            safety_improvement: { gte: 2 } // Only better alternatives
          },
          include: {
            alternative_ingredient: {
              select: { name: true, safety_score: true }
            }
          }
        }
      }
    }
  },
  orderBy: { ingredient_order: 'asc' }
});
```

---

## Dependencies

**Required Before Starting**:
- F01: Authentication
- F05: Product Detail (ingredient tab structure)
- `ingredients` table populated with safety data
- `ingredient_safety_data` table exists

**External Dependencies**:
- Recharts (^2.12.0)
- @radix-ui/react-accordion (via shadcn/ui)

---

## Data Requirements

### Ingredient Safety Data Schema
Each ingredient should have:
- `safety_score`: Decimal (1.0-10.0)
- `concerns`: JSONB array (e.g., ["allergy_high", "environmental_moderate"])
- `banned_regions`: Array of strings (e.g., ["EU", "US"])
- `restriction_level`: Enum ("banned", "restricted", "conditional", "safe")
- `purpose`: String (e.g., "Preservative", "Solvent")
- `synonyms`: Array of strings
- `studies_links`: Array of URLs

---

## Acceptance Testing Checklist

- [ ] Ingredient tab loads on product detail page
- [ ] All ingredients display in correct order
- [ ] Safety scores display for each ingredient
- [ ] Color indicators match scores (green/yellow/red)
- [ ] Overall product safety score calculates correctly
- [ ] Concern badges display (allergy, irritant, environmental)
- [ ] Banned ingredient alert shows if applicable
- [ ] Alert displays banned regions correctly
- [ ] Safety distribution chart renders
- [ ] Distribution percentages calculate correctly
- [ ] Expandable sections work (synonyms, concerns)
- [ ] "View Studies" links open correctly
- [ ] Alternative ingredients display for low-scoring items
- [ ] Safety improvement calculation is accurate
- [ ] "Used in N products" links work
- [ ] Mobile layout stacks ingredient cards vertically
- [ ] Tooltips explain scoring methodology
- [ ] Loading states show during data fetch
- [ ] Error handling for missing safety data
- [ ] Color-blind accessible (patterns + colors)

---

## Related Documentation

- Main Spec: `/docs/NEXTJS_ADMIN_SPEC.md` (lines 523-567)
- Product Detail Tabs: `/docs/NEXTJS_ADMIN_SPEC.md` (lines 459-522)
- Database Schema: `prisma/schema.prisma` (ingredient tables)

---

## Ready for Specification

To create the full specification for this feature, run:

```bash
/speckit.specify docs/features/feature-07-ingredient-safety.md
```

Or use the quick-start script:

```bash
cd docs/features
./quick-start.sh F07
```
