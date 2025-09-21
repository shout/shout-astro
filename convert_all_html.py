#!/usr/bin/env python3
"""
Comprehensive HTML to Markdown converter for the entire Shout.com static site.
Converts all HTML files to markdown with complete content preservation.
"""

import os
import re
from pathlib import Path
from html_to_markdown import convert_to_markdown
from urllib.parse import urljoin, urlparse

def clean_filename(filename):
    """Convert filename to a safe markdown filename."""
    # Remove index.html and use directory name
    if filename == 'index.html':
        return None  # Will use parent directory name

    # Clean up other filenames
    filename = re.sub(r'[^\w\-_.]', '_', filename)
    filename = re.sub(r'\.html$', '.md', filename)
    return filename

def remove_svg_data(html_content):
    """Remove SVG data to reduce file size."""
    # Remove inline SVG elements (complete SVG tags with content)
    html_content = re.sub(r'<svg[^>]*>.*?</svg>', '[SVG_REMOVED]', html_content, flags=re.DOTALL | re.IGNORECASE)

    # Remove data URIs with SVG content
    html_content = re.sub(r'data:image/svg\+xml[^"\'>\s]*', '[SVG_DATA_REMOVED]', html_content, flags=re.IGNORECASE)

    # Remove base64 encoded SVGs
    html_content = re.sub(r'data:image/svg\+xml;base64,[A-Za-z0-9+/=]*', '[SVG_BASE64_REMOVED]', html_content, flags=re.IGNORECASE)

    return html_content

def extract_metadata(html_content):
    """Extract metadata from HTML."""
    metadata = {}

    # Extract title
    title_match = re.search(r'<title[^>]*>(.*?)</title>', html_content, re.DOTALL | re.IGNORECASE)
    if title_match:
        metadata['title'] = title_match.group(1).strip()

    # Extract meta description
    desc_match = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']*)["\']', html_content, re.IGNORECASE)
    if desc_match:
        metadata['description'] = desc_match.group(1).strip()

    # Extract canonical URL
    canonical_match = re.search(r'<link[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']*)["\']', html_content, re.IGNORECASE)
    if canonical_match:
        metadata['canonical'] = canonical_match.group(1).strip()

    return metadata

def process_html_file(html_path, output_dir, base_url="https://shout.com"):
    """Process a single HTML file and convert to markdown."""
    try:
        print(f"Processing: {html_path}")

        with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
            html_content = f.read()

        # Extract metadata
        metadata = extract_metadata(html_content)

        # Remove SVG data to reduce file size
        html_content = remove_svg_data(html_content)

        # Convert HTML to markdown using html-to-markdown
        markdown_content = convert_to_markdown(html_content)

        # Determine output filename
        relative_path = Path(html_path).relative_to(Path("/home/david/RiderProjects/shout-website/shout-static"))

        if relative_path.name == 'index.html':
            # Use directory name for index files
            if len(relative_path.parts) > 1:
                md_filename = f"{relative_path.parts[-2]}.md"
            else:
                md_filename = "homepage.md"
        else:
            md_filename = clean_filename(relative_path.name)
            if not md_filename:
                md_filename = f"{relative_path.stem}.md"

        # Create subdirectory structure if needed
        if len(relative_path.parts) > 1:
            subdir = "_".join(relative_path.parts[:-1])
            md_filename = f"{subdir}_{md_filename}"

        output_path = Path(output_dir) / md_filename

        # Create markdown with metadata header
        full_markdown = ""

        if metadata:
            full_markdown += "---\n"
            for key, value in metadata.items():
                # Escape YAML special characters
                value = str(value).replace('"', '\\"').replace('\n', ' ')
                full_markdown += f"{key}: \"{value}\"\n"
            full_markdown += f"source_path: \"{relative_path}\"\n"
            full_markdown += "---\n\n"

        full_markdown += markdown_content

        # Write the markdown file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_markdown)

        print(f"✓ Converted: {relative_path} → {md_filename}")
        return True

    except Exception as e:
        print(f"✗ Error processing {html_path}: {e}")
        return False

def find_all_html_files(root_dir):
    """Find all HTML files in the directory tree."""
    html_files = []
    root_path = Path(root_dir)

    for html_file in root_path.rglob("*.html"):
        # Skip certain directories if needed
        skip_dirs = ['wp-admin', 'wp-includes', '.git', 'node_modules']
        if not any(skip_dir in str(html_file) for skip_dir in skip_dirs):
            html_files.append(html_file)

    return sorted(html_files)

def main():
    """Main function to convert all HTML files to markdown."""
    static_dir = "/home/david/RiderProjects/shout-website/shout-static"
    output_dir = "/home/david/RiderProjects/shout-website/shout-astro/extracted_content"

    # Create output directory
    Path(output_dir).mkdir(exist_ok=True)

    # Find all HTML files
    html_files = find_all_html_files(static_dir)

    print(f"Found {len(html_files)} HTML files to process...")

    # Process each file
    successful = 0
    failed = 0

    for html_file in html_files:
        if process_html_file(html_file, output_dir):
            successful += 1
        else:
            failed += 1

    print(f"\n✓ Processing complete!")
    print(f"✓ Successfully converted: {successful} files")
    print(f"✗ Failed to convert: {failed} files")
    print(f"📁 Output directory: {output_dir}")

    # List some of the generated files
    output_files = list(Path(output_dir).glob("*.md"))
    print(f"\nGenerated {len(output_files)} markdown files:")
    for md_file in sorted(output_files)[:10]:  # Show first 10
        print(f"  - {md_file.name}")
    if len(output_files) > 10:
        print(f"  ... and {len(output_files) - 10} more files")

if __name__ == "__main__":
    main()