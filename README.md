# Shout.com Astro Website

This is the migrated version of the Shout.com website, converted from WordPress static export to Astro.

## 🚀 Project Structure

```
/
├── public/
│   └── images/          # Static images and assets
├── src/
│   ├── components/      # Reusable Astro components
│   ├── content/         # Content collections (blog posts, etc.)
│   │   ├── blog/        # Blog posts in Markdown
│   │   └── config.ts    # Content collection schemas
│   ├── layouts/         # Layout components
│   │   ├── BaseLayout.astro    # Main site layout
│   │   └── BlogLayout.astro    # Blog post layout
│   └── pages/           # File-based routing
│       ├── index.astro         # Homepage
│       └── blog/
│           ├── index.astro     # Blog index
│           └── [...slug].astro # Dynamic blog post pages
├── astro.config.mjs     # Astro configuration
├── package.json
└── tsconfig.json
```

## 🧞 Commands

All commands are run from the root of the project, from a terminal:

| Command                   | Action                                           |
| :------------------------ | :----------------------------------------------- |
| `npm install`             | Installs dependencies                            |
| `npm run dev`             | Starts local dev server at `localhost:4321`     |
| `npm run build`           | Build your production site to `./dist/`         |
| `npm run preview`         | Preview your build locally, before deploying    |
| `npm run astro ...`       | Run CLI commands like `astro add`, `astro check` |
| `npm run astro -- --help` | Get help using the Astro CLI                     |

## 📝 Content Management

### Adding Blog Posts

1. Create a new `.md` file in `src/content/blog/`
2. Add frontmatter with required fields:
   ```yaml
   ---
   title: "Your Post Title"
   description: "Post description for SEO"
   author: "Author Name"
   publishDate: 2025-01-01T00:00:00.000Z
   category: "Category Name"
   tags: ["tag1", "tag2"]
   ---
   ```
3. Write your content in Markdown below the frontmatter

### Updating Content

- Homepage content: Edit `src/pages/index.astro`
- Site-wide navigation: Edit `src/layouts/BaseLayout.astro`
- Blog layout: Edit `src/layouts/BlogLayout.astro`

## 🎨 Styling

The site uses custom CSS with CSS custom properties (variables) for theming:

- Primary colors, fonts, and spacing are defined in `:root` in `BaseLayout.astro`
- Component-specific styles are scoped to each `.astro` file
- Responsive design follows mobile-first approach

## 🔧 Migration from WordPress

This site was migrated from a WordPress static export (wp2static) with the following conversions:

1. **Structure**: WordPress theme structure → Astro layouts
2. **Content**: HTML blog posts → Markdown with frontmatter
3. **Styling**: WordPress/plugin CSS → Modern CSS with custom properties
4. **SEO**: WordPress SEO plugins → Built-in Astro SEO optimization
5. **Performance**: Heavy WordPress site → Lightweight static Astro site

## 🌟 Features

- ✅ Static site generation for optimal performance
- ✅ SEO-optimized with proper meta tags and structured data
- ✅ Responsive design that works on all devices
- ✅ Blog with content collections for easy management
- ✅ Clean, modern design based on original WordPress theme
- ✅ Fast loading times and excellent Core Web Vitals
- ✅ Accessible markup and navigation

## 🚀 Deployment

The site can be deployed to any static hosting provider:

- **Netlify**: Connect your Git repository for automatic deployments
- **Vercel**: Import the project for instant deployments
- **GitHub Pages**: Use GitHub Actions to build and deploy
- **Cloudflare Pages**: Connect repository for global CDN deployment

Build command: `npm run build`
Output directory: `dist`

## 📊 Performance Benefits

Compared to the original WordPress site:

- **Load time**: Significantly faster (static files vs. server-side rendering)
- **Bundle size**: Much smaller (no WordPress overhead)
- **SEO**: Better Core Web Vitals scores
- **Maintenance**: No security updates, database management, or server costs
- **Developer experience**: Modern tooling with hot reload and TypeScript support

## 🛠️ Customization

### Adding New Pages

1. Create a new `.astro` file in `src/pages/`
2. Use the `BaseLayout` component for consistent styling
3. Add navigation links in `BaseLayout.astro` if needed

### Modifying Design

1. Update CSS custom properties in `BaseLayout.astro` for global changes
2. Modify component-specific styles in individual `.astro` files
3. All styles are scoped by default in Astro

### Adding Integrations

Astro supports many integrations for additional functionality:

```bash
npx astro add tailwind    # Add Tailwind CSS
npx astro add react       # Add React support
npx astro add sitemap     # Add sitemap generation
```

## 👀 Want to learn more?

Feel free to check [Astro documentation](https://docs.astro.build) or jump into their [Discord server](https://astro.build/chat).