# Shout.com Astro Migration Documentation

## Project Overview
This document outlines the migration of Shout.com from a static WordPress site to Astro using the Astroship theme, preserving all original content while modernizing the design and architecture.

## What We've Accomplished

### 1. Content Extraction & Migration
- **Extracted 333 HTML files** from the static site using a comprehensive Python script
- **Preserved complete content** including headings, descriptions, metadata, and images
- **Created markdown files** in `/extracted_content/` with full content structure
- **Migrated survey-maker page** with original content structure intact

### 2. Icon System Overhaul
- **❌ REMOVED:** Ugly emoji icons (🎨💎🔀📊🔐🎯📈🚀🔒🤝)
- **✅ IMPLEMENTED:** Professional BoxIcons from `@iconify-json/bx`
- **Applied consistent styling** with `text-primary` color and proper sizing

### 3. Component Architecture
- **Used Astroship's components** instead of custom implementations
- **Maintained original content** while leveraging professional theme components
- **Added customer logos** using actual Shout customer SVGs
- **Applied consistent branding** with proper color schemes

## File Structure

```
shout-astro/                    # Main project directory
├── astroship/                  # Original Astroship theme (reference only)
├── src/
│   ├── components/
│   │   ├── hero.astro          # Reusable hero component
│   │   ├── features.astro      # Feature grid component
│   │   ├── customer-logos.astro # Customer logos section
│   │   ├── pricing-card.astro  # Pricing card component
│   │   ├── sectionhead.astro   # Section header component
│   │   └── ui/
│   │       ├── button.astro    # Button component
│   │       └── link.astro      # Link component
│   ├── pages/
│   │   ├── index.astro         # Homepage
│   │   ├── pricing.astro       # Pricing page with comparison table
│   │   ├── survey-maker.astro  # Survey maker product page
│   │   ├── form-builder.astro  # Form builder product page
│   │   └── quiz-builder.astro  # Quiz builder product page
│   └── layouts/
│       └── AstroshipLayout.astro
├── extracted_content/          # All 333 original HTML files converted to markdown
│   ├── pricing_pricing.md      # Original pricing page content (60k+ tokens)
│   ├── survey-maker_survey-maker.md
│   ├── form-builder_form-builder.md
│   └── ... (330+ other extracted files)
├── convert_all_html.py        # Content extraction script
├── public/
│   └── images/
│       ├── survey-hero.jpg     # Updated hero image
│       └── logo.svg           # Shout logo
└── CLAUDE.md                  # This documentation
```

## Important File Reading Guidelines

### ⚠️ Reading Large Extracted Files Efficiently

The extracted markdown files in `/extracted_content/` are VERY LARGE (some 60k+ tokens). **Never use Grep tool for content searching** - it's inefficient and wastes time.

**ALWAYS use Read tool with offset and limit parameters:**

```bash
# ❌ DON'T DO THIS (wastes time)
Grep pattern="table" path="/extracted_content/pricing_pricing.md"

# ✅ DO THIS INSTEAD (efficient)
Read file_path="/extracted_content/pricing_pricing.md" offset=150 limit=100
```

**Best practices for large file reading:**
1. **Start with small chunks:** Read 50-100 lines at a time
2. **Use strategic offsets:** Jump to likely content locations
3. **Read sequentially:** Use previous read results to determine next offset
4. **Search for structure:** Look for markdown headers (#) and table markers (|)

### File Organization Notes

- **astroship/** folder contains the original theme for reference
- **extracted_content/** contains ALL original site content (333 files)
- **src/** contains our custom Astro implementation using Astroship components
- Large extracted files require strategic reading with offset/limit parameters

## Development Guidelines

### 🚫 NEVER USE EMOJI ICONS AGAIN
**Always use BoxIcons instead of emoji for professional appearance:**

```astro
<!-- ❌ NEVER DO THIS -->
<div class="text-3xl">🎨</div>

<!-- ✅ ALWAYS DO THIS -->
<div class="w-12 h-12 text-primary">
  <Icon name="bx:palette" />
</div>
```

### Icon Usage Standards
1. **Import:** Always import Icon component: `import { Icon } from "astro-icon/components";`
2. **Sizing:** Use consistent sizing classes:
   - Small icons: `w-8 h-8`
   - Medium icons: `w-12 h-12`
   - Large icons: `w-16 h-16`
3. **Color:** Always use `text-primary` for brand consistency
4. **Centering:** Use `mx-auto` for centered icons in cards

### Component Development Best Practices

#### 1. Create Reusable Components
Extract repeated sections into components rather than copying code:

```astro
<!-- Extract this pattern into a reusable component -->
<div class="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow">
  <div class="w-8 h-8 mb-3 text-primary">
    <Icon name="bx:icon-name" />
  </div>
  <h3 class="text-lg font-semibold mb-2 text-primary">Title</h3>
  <p class="text-gray-600">Description</p>
</div>
```

#### 2. Use Props for Customization
Make components flexible with TypeScript interfaces:

```astro
---
export interface Props {
  icon: string;
  title: string;
  description: string;
}
const { icon, title, description } = Astro.props;
---

<div class="feature-card">
  <Icon name={icon} />
  <h3>{title}</h3>
  <p>{description}</p>
</div>
```

#### 3. Maintain Content Consistency
- **Always reference original content** from `/extracted_content/` when updating pages
- **Preserve exact headings and descriptions** from the original site
- **Keep SEO-optimized titles and meta descriptions**

### Content Migration Process

When updating additional pages:

1. **Check extracted content:**
   ```bash
   ls extracted_content/ | grep page-name
   ```

2. **Review original structure:**
   ```bash
   head -50 extracted_content/page-name_page-name.md
   ```

3. **Use original headings and descriptions** - don't create new content

4. **Replace emoji icons** with appropriate BoxIcons

5. **Test locally** before considering complete

### Available BoxIcons for Common Uses

| Use Case | BoxIcon Name | Example |
|----------|--------------|---------|
| Surveys/Polls | `bx:poll` | Survey questions |
| Multiple Choice | `bx:checkbox-checked` | Form options |
| Analytics | `bx:chart` | Data visualization |
| Security | `bx:shield` | Data protection |
| Users/Teams | `bx:group` | Collaboration |
| Settings | `bx:cog` | Configuration |
| Calendar | `bx:calendar` | Date selection |
| Images | `bx:image` | Picture uploads |
| Text | `bx:text` | Text inputs |
| Stars | `bx:star` | Ratings |

### Running Commands

- **Development server:** `npm run dev`
- **Build:** `npm run build`
- **Extract new content:** `python3 convert_all_html.py`

### Development Workflow

⚠️ **IMPORTANT: Always check for Astro errors after making changes**

After editing any `.astro` files or components:
1. Check the dev server output for compilation errors
2. Use `BashOutput` tool to monitor the running dev server
3. Look for TypeScript errors, missing imports, or syntax issues
4. Fix any errors before considering the task complete

Common error types to watch for:
- Missing imports for components or icons
- Incorrect component props or interfaces
- Syntax errors in Astro frontmatter
- Invalid HTML structure in templates

## Design System & Layout Patterns

### Section Spacing Standards

**16-unit consistent spacing between all sections:**
- Use `pt-16 pb-16` for most sections
- First section after hero can use larger top padding: `pt-16 pb-16`
- Avoid mixing margin and padding - prefer padding for consistency
- Components should use `py-16` for self-contained spacing

### Heading & Text Alignment

**All section headings should be LEFT-ALIGNED:**
```astro
<!-- ✅ CORRECT -->
<div class="mb-12">
  <h2 class="text-4xl lg:text-5xl font-bold lg:tracking-tight">Section Title</h2>
  <p class="text-lg mt-4 text-gray-600">Description text</p>
</div>

<!-- ❌ AVOID -->
<div class="text-center mb-12">
  <h2 class="text-4xl lg:text-5xl font-bold lg:tracking-tight">Section Title</h2>
  <p class="text-lg mt-4 text-gray-600 max-w-3xl mx-auto">Description text</p>
</div>
```

**Pattern established:** All sections follow the "Integrated solutions for every need" left-aligned style for consistency.

### Feature Card Patterns

**Standard feature card with inline icon+text:**
```astro
<div class="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow">
  <div class="flex items-center mb-3">
    <Icon name="bx:poll" class="w-8 h-8 text-primary mr-3" />
    <h3 class="text-lg font-semibold text-primary">Feature Title</h3>
  </div>
  <p class="text-gray-600">Feature description explaining the capability.</p>
</div>
```

**Key patterns:**
- Icons are `w-8 h-8` with `text-primary` color
- Use `flex items-center` for inline icon+heading layout
- `mr-3` spacing between icon and text
- Consistent padding `p-6` and hover effects
- Grid layouts: `md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4` for feature grids

### Survey-Maker Page Structure

**Current optimized page flow:**
1. Hero Section
2. "Everything you need to make surveys" (20 feature cards) - **MOVED TO TOP**
3. Customer Logos (shortened text)
4. Integrated Solutions (Features component)
5. Building surveys
6. Best Reasons To Choose Shout
7. Shout out! (delivery methods)
8. Survey reports
9. The perfect survey maker for teams
10. Final CTA

**Key changes made:**
- **20 comprehensive survey features** added (NPS, Multiple Choice, eSignatures, AI Question Writing, GDPR Consent, etc.)
- **Section moved to top** for immediate feature visibility
- **"Online survey tool" section removed** (was redundant)
- **Slideout surveys vs Popups** distinction clarified

### Branding Updates

- **Copyright:** Updated to "Shout.com" in footer component
- **Customer logos text:** Shortened to "Organizations all over the world use Shout to improve customer and employee experiences."

### Quality Checklist

Before considering any page complete:

- [ ] ✅ All emoji icons replaced with BoxIcons
- [ ] ✅ Original content preserved from extracted markdown
- [ ] ✅ Icons use `text-primary` color
- [ ] ✅ Consistent sizing classes applied
- [ ] ✅ **16-unit spacing between sections (`pt-16 pb-16`)**
- [ ] ✅ **All headings left-aligned (no `text-center`)**
- [ ] ✅ **No `max-w-3xl mx-auto` on section descriptions**
- [ ] ✅ Hover effects and transitions maintained
- [ ] ✅ Mobile responsiveness verified
- [ ] ✅ No console errors in dev tools

## Next Steps & Recommendations

### 1. Component Refactoring Priority
1. **Extract question types grid** into reusable component
2. **Create feature card component** for benefits sections
3. **Build team features component** for collaboration sections
4. **Standardize CTA sections** across all pages

### 2. Completed & Remaining Pages

**✅ COMPLETED:**
- `survey-maker.astro` - Fully migrated with 20 comprehensive features, optimized structure, and consistent design patterns

**🚧 REMAINING:**
- `form-builder.astro` - Use `/extracted_content/form-builder_form-builder.md`
- `quiz-builder.astro` - Use `/extracted_content/quiz-builder_quiz-builder.md`
- Additional product/feature pages as needed

**📋 APPLY TO NEW PAGES:**
- Use established 16-unit spacing pattern
- Left-align all section headings
- Follow survey-maker.astro structure as template
- Replace emoji icons with BoxIcons
- Maintain consistent component usage

### 3. Performance Optimizations
- Implement lazy loading for images
- Optimize SVG customer logos
- Consider component-level code splitting

### 4. SEO Enhancements
- Ensure all pages use original meta descriptions
- Implement structured data markup
- Add proper Open Graph tags

## Important Notes

⚠️ **Never modify content without checking original:** Always reference the extracted markdown files to ensure content accuracy.

⚠️ **Icon consistency is crucial:** The professional appearance depends on consistent BoxIcon usage throughout the site.

⚠️ **Astroship components first:** Always try to use existing Astroship components before creating custom ones.

---

*This documentation should be updated as the project evolves. Always maintain this file when making significant changes to the architecture or content.*