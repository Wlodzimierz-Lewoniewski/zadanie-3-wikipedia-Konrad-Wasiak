import re, requests
from itertools import islice

def content_section(html):
    return html.split('<div id="mw-content-text"')[1].split('<div id="catlinks"')[0]

def reference_section(html):
    if 'id="Przypisy"' in html:
        refs = html.split('id="Przypisy"')[1]
        return refs.split('<div class="mw-heading')[0]
    return ""

def category_section(html):
    return html.split('<div id="catlinks"')[1]

def find_matches(regex, text, flags=0, max_results=5):
    return [match.groups() for match in islice(re.finditer(regex, text, flags=flags), max_results)]

def get_articles_from_category(name, max_results=3):
    category_page = make_category_url(name)
    response = requests.get(category_page)
    return find_matches(article_pattern, response.text, max_results=max_results)

def fetch_article_content(endpoint):
    response = requests.get("https://pl.wikipedia.org" + endpoint)
    return response.text


def extract_internal_links(content, max_results=5):
    return find_matches(internal_link_pattern, content_section(content), max_results=max_results)

def extract_external_links(content, max_results=3):
    return find_matches(external_link_pattern, reference_section(content), max_results=max_results)

def extract_images(content, max_results=3):
    return find_matches(image_pattern, content_section(content), max_results=max_results)

def extract_categories(content, max_results=3):
    return find_matches(category_pattern, category_section(content), max_results=max_results)

def display_result(items):
    print(' | '.join(items).strip())

article_pattern = r'<li[^>]*><a[^>]*href=\"(/wiki/(?![^"]*:)[^"]+)\"[^>]*title=\"([^"]+)\"[^>]*>'
category_pattern = r'<a[^>]*href=\"(/wiki/Kategoria:[^"]+)\"[^>]*title=\"([^"]+)\"[^>]*>'
image_pattern = r'<img[^>]*src=\"(//upload\.wikimedia\.org/[^"]+)\"[^>]*/>'
external_link_pattern = r'<a[^>]*class=\"external[^"]*\"[^>]*href=\"([^"]+)\"[^>]*>'
internal_link_pattern = r'<a[^>]*href=\"(/wiki/(?![^"]*:)[^"]+)\"[^>]*title=\"([^"]+)\"[^>]*>'

def make_category_url(name):
    return f'https://pl.wikipedia.org/wiki/Kategoria:{name.replace(" ", "_")}'

category = input().strip()
articles = get_articles_from_category(category)
for link, title in articles:
    article_content = fetch_article_content(link)
    display_result([item[1] for item in extract_internal_links(article_content)])
    display_result([item[0] for item in extract_images(article_content)])
    display_result([item[0] for item in extract_external_links(article_content)])
    display_result([cat[1].replace('Kategoria:', '') for cat in extract_categories(article_content)])
