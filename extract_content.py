#!/usr/bin/env python3
"""
Content extraction script for migrating Shout.com product pages from HTML to Astro.
Extracts content from WordPress/Stackable block structure and outputs structured markdown.
"""

import os
import re
from bs4 import BeautifulSoup
from pathlib import Path

def clean_text(text):
    """Clean and normalize text content."""
    if not text:
        return ""
    # Remove extra whitespace and normalize
    text = re.sub(r'\s+', ' ', text.strip())
    # Remove HTML entities
    text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    return text

def extract_image_info(img_element):
    """Extract image information from img element."""
    if not img_element:
        return None

    src = img_element.get('src', '')
    alt = img_element.get('alt', '')
    width = img_element.get('width', '')
    height = img_element.get('height', '')

    return {
        'src': src,
        'alt': alt,
        'width': width,
        'height': height
    }

def extract_section_content(soup, page_name):
    """Extract structured content from a parsed HTML document."""
    content = {
        'page_name': page_name,
        'title': '',
        'description': '',
        'hero': {},
        'sections': []
    }

    # Extract page title and description from meta tags
    title_tag = soup.find('title')
    if title_tag:
        content['title'] = clean_text(title_tag.text)

    desc_tag = soup.find('meta', {'name': 'description'})
    if desc_tag:
        content['description'] = clean_text(desc_tag.get('content', ''))

    # Find hero section - look for main h1
    hero_h1 = soup.find('h1')
    if hero_h1:
        hero_text = clean_text(hero_h1.get_text())

        # Look for associated content near the hero - use broader search
        hero_container = hero_h1.find_parent('div', class_=lambda x: x and 'stk-block' in x) or hero_h1.find_parent('div')

        hero_content = {
            'headline': hero_text,
            'description': '',
            'image': None,
            'cta_buttons': []
        }

        if hero_container:
            # Look for Stackable text blocks specifically
            text_blocks = hero_container.find_next_siblings('div', class_=lambda x: x and 'stk-block-text' in x)
            if not text_blocks:
                # Try finding within the same container
                text_blocks = hero_container.find_all('div', class_=lambda x: x and 'stk-block-text' in x)

            for text_block in text_blocks:
                p_tag = text_block.find('p')
                if p_tag:
                    text = clean_text(p_tag.get_text())
                    if text and len(text) > 20:  # Skip very short text
                        hero_content['description'] = text
                        break

            # Find hero image (look broadly in columns)
            columns_container = hero_h1.find_parent('div', class_=lambda x: x and 'stk-block-columns' in x)
            if columns_container:
                hero_img = columns_container.find('img')
                if hero_img:
                    hero_content['image'] = extract_image_info(hero_img)

            # Find CTA buttons
            buttons = hero_container.find_all('a', class_=lambda x: x and any(cls in x for cls in ['btn', 'button', 'link']))
            for btn in buttons:
                btn_text = clean_text(btn.get_text())
                btn_href = btn.get('href', '')
                if btn_text and 'Start' in btn_text:  # Focus on main CTA buttons
                    hero_content['cta_buttons'].append({
                        'text': btn_text,
                        'href': btn_href
                    })

        content['hero'] = hero_content

    # Extract all sections based on h2 and h3 elements (Stackable headings)
    headings = soup.find_all(['h2', 'h3'], class_=lambda x: x and 'stk-block-heading__text' in x)

    for heading in headings:
        if not heading.get_text().strip():
            continue

        section = {
            'level': heading.name,
            'title': clean_text(heading.get_text()),
            'id': heading.get('id', ''),
            'content': [],
            'features': [],
            'images': []
        }

        # Get the heading's parent container
        heading_block = heading.find_parent('div', class_=lambda x: x and 'stk-block-heading' in x)

        if heading_block:
            # Look for next text blocks after this heading
            current = heading_block
            while current:
                current = current.find_next_sibling('div', class_=lambda x: x and 'stk-block' in x)
                if not current:
                    break

                # If we hit another heading, stop
                if current.find('h2') or current.find('h3'):
                    break

                # Extract text from stk-block-text
                if 'stk-block-text' in current.get('class', []):
                    p_tag = current.find('p')
                    if p_tag:
                        text = clean_text(p_tag.get_text())
                        if text and len(text) > 10:
                            section['content'].append(text)

                # Extract images
                images = current.find_all('img')
                for img in images:
                    img_info = extract_image_info(img)
                    if img_info and img_info['src']:
                        section['images'].append(img_info)

            # For feature sections, look for columns containing this heading
            columns_container = heading_block.find_parent('div', class_=lambda x: x and 'stk-block-columns' in x)
            if columns_container:
                # Find all columns in this container
                columns = columns_container.find_all('div', class_=lambda x: x and 'stk-block-column' in x)

                for column in columns:
                    feature_title = ''
                    feature_desc = ''

                    # Get title from h3 in this column
                    h3 = column.find('h3')
                    if h3:
                        feature_title = clean_text(h3.get_text())

                    # Get description from p in this column
                    p = column.find('p')
                    if p:
                        feature_desc = clean_text(p.get_text())

                    if feature_title and feature_desc:
                        section['features'].append({
                            'title': feature_title,
                            'description': feature_desc,
                            'icon': ''
                        })

        content['sections'].append(section)

    return content

def generate_markdown(content):
    """Generate markdown from extracted content."""
    md = f"# {content['page_name'].title()} Page Content\n\n"

    if content['title']:
        md += f"**Title:** {content['title']}\n\n"

    if content['description']:
        md += f"**Description:** {content['description']}\n\n"

    # Hero section
    hero = content['hero']
    if hero:
        md += "## Hero Section\n\n"
        if hero['headline']:
            md += f"**Headline:** {hero['headline']}\n\n"
        if hero['description']:
            md += f"**Description:** {hero['description']}\n\n"
        if hero['image']:
            img = hero['image']
            md += f"**Image:** `{img['src']}` (alt: \"{img['alt']}\")\n\n"
        if hero['cta_buttons']:
            md += "**CTA Buttons:**\n"
            for btn in hero['cta_buttons']:
                md += f"- {btn['text']} → `{btn['href']}`\n"
            md += "\n"

    # Sections
    for section in content['sections']:
        md += f"## Section: {section['title']}\n\n"

        if section['id']:
            md += f"**ID:** {section['id']}\n\n"

        if section['content']:
            md += "**Content:**\n"
            for content_item in section['content']:
                md += f"- {content_item}\n"
            md += "\n"

        if section['features']:
            md += "**Features:**\n"
            for feature in section['features']:
                md += f"- **{feature['title']}**: {feature['description']}"
                if feature['icon']:
                    md += f" (icon: {feature['icon']})"
                md += "\n"
            md += "\n"

        if section['images']:
            md += "**Images:**\n"
            for img in section['images']:
                md += f"- `{img['src']}` (alt: \"{img['alt']}\")\n"
            md += "\n"

        md += "---\n\n"

    return md

def process_html_file(html_path, output_dir):
    """Process a single HTML file and generate markdown output."""
    print(f"Processing {html_path}...")

    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract page name from path
    page_name = Path(html_path).parent.name

    # Extract content
    content = extract_section_content(soup, page_name)

    # Generate markdown
    markdown = generate_markdown(content)

    # Write output file
    output_file = Path(output_dir) / f"{page_name}-content.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown)

    print(f"Generated {output_file}")
    return content

def main():
    """Main function to process all product pages."""
    static_dir = "/home/david/RiderProjects/shout-website/shout-static"
    output_dir = "/home/david/RiderProjects/shout-website/shout-astro"

    # Product pages to process
    pages = [
        "survey-maker/index.html",
        "form-builder/index.html",
        "quiz-builder/index.html"
    ]

    extracted_content = {}

    for page in pages:
        html_path = Path(static_dir) / page
        if html_path.exists():
            content = process_html_file(html_path, output_dir)
            page_name = Path(page).parent.name
            extracted_content[page_name] = content
        else:
            print(f"Warning: {html_path} not found")

    print(f"\nExtraction complete! Generated markdown files in {output_dir}")
    print("Files generated:")
    for page_name in extracted_content.keys():
        print(f"- {page_name}-content.md")

if __name__ == "__main__":
    main()