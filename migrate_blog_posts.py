#!/usr/bin/env python3

import os
import re
import yaml
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

# Configuration
SOURCE_DIR = Path("/home/david/RiderProjects/shout-website/shout-astro/extracted_content")
DEST_DIR = Path("/home/david/RiderProjects/shout-website/shout-astro/src/content/blog")
IMAGES_DIR = Path("/home/david/RiderProjects/shout-website/shout-astro/public/images")

# Category mapping
CATEGORY_MAP = {
    "business": "Business",
    "survey-design": "Survey Design",
    "email-marketing": "Email Marketing",
    "customer-experience": "Customer Experience",
    "digital-marketing": "Digital Marketing",
    "customer-feedback": "Customer Feedback",
    "quiz-design": "Quiz Design",
    "landing-pages": "Landing Pages",
    "employees": "Employees",
    "employee-experience": "Employee Experience",
    "compliance": "Compliance",
    "seo": "SEO",
    "calculators": "Calculators",
}

# Files to skip (already exist)
SKIP_FILES = {
    "7-tools-for-business-communication.md",
    "digital-marketing-strategies-for-small-business.md",
}

# Stats tracking
stats = {
    "migrated": 0,
    "skipped": 0,
    "flagged": 0,
    "missing_images": [],
    "flagged_posts": [],
}

def get_slug_from_filename(filename):
    """Extract slug from filename format: category_slug_slug.md"""
    parts = filename.replace(".md", "").split("_")
    if len(parts) >= 3:
        return parts[1]
    return None

def extract_metadata_from_html_comment(content):
    """Extract metadata from HTML comment block"""
    metadata = {}
    # Find the HTML comment block
    comment_match = re.search(r"<!--\n(.*?)\n-->", content, re.DOTALL)
    if comment_match:
        comment_text = comment_match.group(1)
        lines = comment_text.split("\n")
        for line in lines:
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip()
                metadata[key] = value
    return metadata

def parse_frontmatter(content):
    """Parse YAML frontmatter manually"""
    match = re.match(r"^---\n(.*?)\n---\n(.*)$", content, re.DOTALL)
    if match:
        frontmatter_text = match.group(1)
        body = match.group(2)
        try:
            frontmatter_dict = yaml.safe_load(frontmatter_text) or {}
            return frontmatter_dict, body
        except:
            return {}, content
    return {}, content

def convert_wordpress_image_url(url):
    """Convert WordPress image URL to local path"""
    if not url:
        return None

    # Extract the date and filename from WordPress URL
    # Format: https://shout.com/wp-content/uploads/2022/10/Image-Name.png
    match = re.search(r"wp-content/uploads/(\d{4})/(\d{2})/(.+)$", url)
    if match:
        year, month, filename = match.groups()
        local_path = f"/images/{year}/{month}/{filename}"

        # Check if image exists
        full_path = IMAGES_DIR / year / month / filename
        if full_path.exists():
            return local_path
        else:
            stats["missing_images"].append({"url": url, "expected_path": str(full_path)})
            return local_path  # Still return the path for the frontmatter

    return None

def get_image_alt_text(title, image_url):
    """Generate alt text from title or image filename"""
    if not title:
        title = "Article image"

    # Clean up title for alt text
    alt_text = re.sub(r"\s+-\s+Shout\.com$", "", title)
    alt_text = re.sub(r"[^a-zA-Z0-9\s-]", "", alt_text)
    return alt_text.strip()

def check_for_spam(content, title, description):
    """Check if post contains spam markers"""
    spam_markers = {
        "indian_coding": [
            "indiancoding.com", "programmingblog.in", "codinginindia.net",
            "techblog.in", "pythoninindia.com", "javadeveloper.in"
        ],
        "broken_links": ["404", "[broken]", "[dead link]"],
        "excessive_promo": [
            "clickhere", "buynowr", "limited time offer", "act now",
            "exclusively for", "special discount code"
        ]
    }

    flags = []

    # Check for spam links in content
    for marker, patterns in spam_markers.items():
        for pattern in patterns:
            if pattern.lower() in content.lower():
                flags.append(f"Potential spam marker: {pattern} ({marker})")

    # Check if content appears to be purely promotional
    if len(content) < 500:
        flags.append("Very short content (potential stub or low quality)")

    # Check for excessive external links
    external_links = re.findall(r"\[.*?\]\(https?://(?!shout\.com)[^\)]+\)", content)
    if len(external_links) > 10:
        flags.append(f"Excessive external links ({len(external_links)} found)")

    return flags

def format_datetime(dt_str):
    """Convert datetime string to ISO format with Z"""
    if not dt_str:
        return None

    try:
        # Parse various datetime formats
        # Try ISO format first
        if "T" in dt_str:
            # Remove timezone info for parsing
            dt_str_clean = dt_str.replace("+00:00", "").replace("Z", "")
            dt = datetime.fromisoformat(dt_str_clean)
        else:
            dt = datetime.fromisoformat(dt_str)

        return dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    except:
        return None

def build_yaml_frontmatter(data):
    """Build YAML frontmatter string"""
    lines = ["---"]

    # Add title
    if "title" in data:
        lines.append(f'title: "{data["title"]}"')

    # Add description
    if "description" in data:
        lines.append(f'description: "{data["description"]}"')

    # Add author
    if "author" in data:
        lines.append(f'author: "{data["author"]}"')

    # Add publish date
    if "publishDate" in data:
        lines.append(f'publishDate: {data["publishDate"]}')

    # Add modified date if exists
    if "modifiedDate" in data:
        lines.append(f'modifiedDate: {data["modifiedDate"]}')

    # Add image if exists
    if "image" in data:
        lines.append("image:")
        lines.append(f'  src: "{data["image"]["src"]}"')
        lines.append(f'  alt: "{data["image"]["alt"]}"')

    # Add category
    if "category" in data:
        lines.append(f'category: "{data["category"]}"')

    # Add reading time
    if "readingTime" in data:
        lines.append(f'readingTime: "{data["readingTime"]}"')

    lines.append("---")
    return "\n".join(lines)

def process_post(filepath):
    """Process a single blog post"""
    filename = filepath.name

    # Check if already migrated
    slug = get_slug_from_filename(filename)
    if not slug:
        return None

    dest_filename = f"{slug}.md"
    if dest_filename in SKIP_FILES:
        stats["skipped"] += 1
        return {"skipped": True, "reason": "Already exists"}

    # Check if destination already exists
    dest_path = DEST_DIR / dest_filename
    if dest_path.exists():
        stats["skipped"] += 1
        return {"skipped": True, "reason": "Destination file exists"}

    # Read source file
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Parse frontmatter and extract metadata
    fm_dict, body = parse_frontmatter(content)
    metadata = extract_metadata_from_html_comment(content)

    # Get category from filename
    category_prefix = filename.split("_")[0]
    category = CATEGORY_MAP.get(category_prefix, "General")

    # Extract main content (remove HTML comment block and skip to content)
    main_content = body
    # Remove the HTML comment block if still present
    main_content = re.sub(r"<!--\n.*?\n-->\n?", "", main_content, flags=re.DOTALL)
    # Remove navigation and skip to content links
    main_content = re.sub(r"\[Skip to content\].*?\n", "", main_content)
    main_content = re.sub(r"\[<img.*?</a>\]\s*\n", "", main_content, flags=re.DOTALL)
    # Remove complex navigation structures (handle indented lists)
    main_content = re.sub(r"(?:^\s*[\*\+\-]\s+\[.*?\]\(.*?\).*?$\n?)+", "", main_content, flags=re.MULTILINE)
    # Remove all Log-in links and sections
    main_content = re.sub(r"\[Log\-?in\]\(.*?\)", "", main_content)
    # Remove Menu sections
    main_content = re.sub(r"Menu\\\[SVG_REMOVED\]", "", main_content)
    # Remove SVG removed markers and remaining escaped brackets
    main_content = re.sub(r"\\\[SVG_REMOVED\]", "", main_content)
    main_content = re.sub(r"\\\[", "[", main_content)
    main_content = re.sub(r"\\\]", "]", main_content)
    # Remove markdown images that point to wp-content
    main_content = re.sub(r"!\[.*?\]\(https://shout\.com/wp-content/.*?\)\n?", "", main_content)
    # Remove lines that are just logo/branding image links (often at start and end)
    main_content = re.sub(r"^\[<img src='https://shout\.com/wp-content/.*?</a>\]\s*$\n?", "", main_content, flags=re.MULTILINE)

    # Clean up multiple newlines
    main_content = re.sub(r"\n\n\n+", "\n\n", main_content)

    # Remove empty lines at the start
    main_content = main_content.lstrip()

    # Remove trailing whitespace
    main_content = main_content.rstrip()

    # Check for spam
    spam_flags = check_for_spam(main_content, fm_dict.get("title", ""), fm_dict.get("description", ""))
    if spam_flags:
        stats["flagged"] += 1
        stats["flagged_posts"].append({
            "file": filename,
            "slug": slug,
            "title": fm_dict.get("title", ""),
            "flags": spam_flags
        })
        return {"flagged": True, "flags": spam_flags}

    # Prepare new metadata
    title = fm_dict.get("title", "")
    # Remove " - Shout.com" suffix
    title = re.sub(r"\s+-\s+Shout\.com$", "", title)

    description = fm_dict.get("description", "")

    author = metadata.get("meta-author", "Evan")
    published_time = metadata.get("meta-article-published_time")
    modified_time = metadata.get("meta-article-modified_time")
    og_image = metadata.get("meta-og-image")
    reading_time = metadata.get("meta-twitter:data2", "")

    # Convert image URL
    image_src = convert_wordpress_image_url(og_image)
    image_alt = get_image_alt_text(title, og_image)

    # Build new frontmatter data
    new_fm = {
        "title": title,
        "description": description,
        "author": author,
        "publishDate": format_datetime(published_time),
        "category": category,
    }

    if modified_time:
        new_fm["modifiedDate"] = format_datetime(modified_time)

    if image_src:
        new_fm["image"] = {
            "src": image_src,
            "alt": image_alt
        }

    if reading_time:
        new_fm["readingTime"] = reading_time

    # Build new file content
    new_frontmatter = build_yaml_frontmatter(new_fm)
    new_content = new_frontmatter + "\n\n" + main_content.strip() + "\n"

    # Write new file
    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    stats["migrated"] += 1
    return {"migrated": True, "filename": dest_filename}

def main():
    """Main migration function"""
    print("Starting blog post migration...")
    print(f"Source directory: {SOURCE_DIR}")
    print(f"Destination directory: {DEST_DIR}")
    print()

    # Create destination directory if needed
    DEST_DIR.mkdir(parents=True, exist_ok=True)

    # Find all blog posts matching the category patterns
    pattern = re.compile(r"^(business_|survey-design_|email-marketing_|customer-experience_|digital-marketing_|customer-feedback_|quiz-design_|landing-pages_|employees_|employee-experience_|compliance_|seo_|calculators_)")

    blog_posts = [f for f in SOURCE_DIR.glob("*.md") if pattern.match(f.name)]
    blog_posts = [f for f in blog_posts if f.name.startswith(tuple([k + "_" for k in CATEGORY_MAP.keys()]))]

    print(f"Found {len(blog_posts)} blog posts to process")
    print()

    # Process each post
    for idx, filepath in enumerate(sorted(blog_posts), 1):
        print(f"[{idx}/{len(blog_posts)}] Processing: {filepath.name}")
        result = process_post(filepath)
        if result:
            if result.get("migrated"):
                print(f"  ✓ Migrated to: {result['filename']}")
            elif result.get("skipped"):
                print(f"  ⊘ Skipped: {result['reason']}")
            elif result.get("flagged"):
                print(f"  ⚠ Flagged for review:")
                for flag in result['flags']:
                    print(f"    - {flag}")
            elif result.get("error"):
                print(f"  ✗ Error: {result['error']}")

    print()
    print("=" * 60)
    print("MIGRATION SUMMARY")
    print("=" * 60)
    print(f"Successfully migrated: {stats['migrated']}")
    print(f"Skipped (duplicates):  {stats['skipped']}")
    print(f"Flagged for review:    {stats['flagged']}")
    print()

    if stats["missing_images"]:
        print(f"Missing images: {len(stats['missing_images'])}")
        for img in stats["missing_images"][:10]:
            print(f"  - {img['url']}")
        if len(stats["missing_images"]) > 10:
            print(f"  ... and {len(stats['missing_images']) - 10} more")
        print()

    # Write review file if there are flagged posts
    if stats["flagged_posts"]:
        review_file = Path("/home/david/RiderProjects/shout-website/shout-astro/BLOG_REVIEW_NEEDED.md")
        with open(review_file, "w", encoding="utf-8") as f:
            f.write("# Blog Posts Requiring Manual Review\n\n")
            f.write("These posts were flagged during migration for potential quality issues.\n\n")
            for post in stats["flagged_posts"]:
                f.write(f"## {post['title']}\n\n")
                f.write(f"**File:** {post['file']}\n")
                f.write(f"**Slug:** {post['slug']}\n\n")
                f.write("**Issues:**\n")
                for flag in post['flags']:
                    f.write(f"- {flag}\n")
                f.write("\n---\n\n")
        print(f"Review file created: BLOG_REVIEW_NEEDED.md")

    print()
    print("Migration complete!")

if __name__ == "__main__":
    main()
