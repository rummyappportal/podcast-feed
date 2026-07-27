import xml.etree.ElementTree as ET
import os
import re
import urllib.request

files = [
    r'c:\Users\dinesh\Downloads\mojolocontentgudlines\podcast-feed-repo\kreditbee\feed.xml',
    r'c:\Users\dinesh\Downloads\mojolocontentgudlines\podcast-feed-repo\kreditbee-account2\feed.xml'
]

ns = {'itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd',
      'googleplay': 'http://www.google.com/schemas/play-podcasts/1.0',
      'content': 'http://purl.org/rss/1.0/modules/content/'}

all_authors = []
all_links = []
all_emails = []
all_pubdates = []
all_categories = []
all_guids = []

for f in files:
    folder = os.path.basename(os.path.dirname(f))
    print(f'\n{"="*60}')
    print(f'  CHECKING: {folder}/feed.xml')
    print(f'{"="*60}')
    
    bugs = []
    warnings = []
    
    try:
        tree = ET.parse(f)
        root = tree.getroot()
        print('  [PASS] XML Parsing: Valid XML')
    except ET.ParseError as e:
        print(f'  [FATAL] XML Parse Error: {e}')
        continue
    
    # Read raw file for namespace + special char checks
    with open(f, 'r', encoding='utf-8') as fh:
        raw = fh.read()
    
    channel = root.find('channel')
    item = channel.find('item')
    
    # =============================================
    # PROMPT 14.2 — RSS Root Tag (Namespace Check)
    # =============================================
    print('\n  --- PROMPT 14.2: Namespace Declaration ---')
    if 'xmlns:googleplay' not in raw:
        bugs.append('14.2: xmlns:googleplay namespace MISSING in RSS tag')
        print('  [FAIL] xmlns:googleplay MISSING')
    else:
        print('  [PASS] xmlns:googleplay declared')
    if 'xmlns:itunes' not in raw:
        bugs.append('14.2: xmlns:itunes namespace MISSING')
        print('  [FAIL] xmlns:itunes MISSING')
    else:
        print('  [PASS] xmlns:itunes declared')
    if 'xmlns:content' not in raw:
        bugs.append('14.2: xmlns:content namespace MISSING')
        print('  [FAIL] xmlns:content MISSING')
    else:
        print('  [PASS] xmlns:content declared')
    
    # =============================================
    # PROMPT 14.3 — Channel Tags (Complete List)
    # =============================================
    print('\n  --- PROMPT 14.3: Channel Tags ---')
    
    # title
    ch_title = channel.find('title')
    if ch_title is not None:
        print(f'  [PASS] <title>: {ch_title.text[:50]}...')
    else:
        bugs.append('14.3: Channel <title> MISSING')
        print('  [FAIL] <title> MISSING')
    
    # link
    ch_link = channel.find('link')
    if ch_link is not None:
        print(f'  [PASS] <link>: {ch_link.text}')
        all_links.append((folder, ch_link.text))
    else:
        bugs.append('14.3: Channel <link> MISSING')
        print('  [FAIL] <link> MISSING')
    
    # language (13.7)
    ch_lang = channel.find('language')
    if ch_lang is not None:
        if ch_lang.text == 'en-us':
            print(f'  [PASS] <language>: en-us')
        else:
            bugs.append(f'13.7: <language> is "{ch_lang.text}" but MUST be "en-us"')
            print(f'  [FAIL] <language> is "{ch_lang.text}" — MUST be "en-us" (Prompt 13.7)')
    else:
        bugs.append('14.3: <language> MISSING')
        print('  [FAIL] <language> MISSING')
    
    # copyright (13.8)
    ch_copy = channel.find('copyright')
    if ch_copy is not None:
        print(f'  [PASS] <copyright>: {ch_copy.text}')
    else:
        bugs.append('13.8: <copyright> MISSING (REQUIRED)')
        print('  [FAIL] <copyright> MISSING (Prompt 13.8: REQUIRED)')
    
    # itunes:author
    ch_author = channel.find('itunes:author', ns)
    if ch_author is not None:
        print(f'  [PASS] <itunes:author>: {ch_author.text}')
        all_authors.append((folder, ch_author.text))
    else:
        bugs.append('14.3: <itunes:author> MISSING')
        print('  [FAIL] <itunes:author> MISSING')
    
    # itunes:type (13.8)
    ch_type = channel.find('itunes:type', ns)
    if ch_type is not None:
        if ch_type.text == 'episodic':
            print(f'  [PASS] <itunes:type>: episodic')
        else:
            bugs.append(f'13.8: <itunes:type> is "{ch_type.text}" but MUST be "episodic"')
            print(f'  [FAIL] <itunes:type> is "{ch_type.text}" — MUST be "episodic"')
    else:
        bugs.append('13.8: <itunes:type> MISSING')
        print('  [FAIL] <itunes:type> MISSING (Prompt 13.8)')
    
    # itunes:summary (14.1 — must be FULL CDATA)
    ch_summary = channel.find('itunes:summary', ns)
    if ch_summary is not None and ch_summary.text:
        word_count = len(ch_summary.text.split())
        print(f'  [PASS] <itunes:summary>: present ({word_count} words)')
        if word_count < 500:
            warnings.append(f'14.1: Channel itunes:summary is only {word_count} words (should be 800+ for Amazon)')
            print(f'  [WARN] Channel itunes:summary only {word_count} words (Prompt 14.1: should be 800+)')
    else:
        bugs.append('14.3: <itunes:summary> MISSING or empty')
        print('  [FAIL] <itunes:summary> MISSING')
    
    # description (14.1 — must be FULL CDATA)
    ch_desc = channel.find('description')
    if ch_desc is not None and ch_desc.text:
        word_count = len(ch_desc.text.split())
        print(f'  [PASS] <description>: present ({word_count} words)')
    else:
        bugs.append('14.3: Channel <description> MISSING or empty')
        print('  [FAIL] <description> MISSING')
    
    # itunes:owner
    ch_owner = channel.find('itunes:owner', ns)
    if ch_owner is not None:
        owner_name = ch_owner.find('itunes:name', ns)
        owner_email = ch_owner.find('itunes:email', ns)
        if owner_name is not None:
            print(f'  [PASS] <itunes:owner>/<itunes:name>: {owner_name.text}')
        else:
            bugs.append('14.3: <itunes:owner>/<itunes:name> MISSING')
            print('  [FAIL] <itunes:owner>/<itunes:name> MISSING')
        if owner_email is not None:
            print(f'  [PASS] <itunes:owner>/<itunes:email>: {owner_email.text}')
            all_emails.append((folder, owner_email.text))
        else:
            bugs.append('14.3: <itunes:owner>/<itunes:email> MISSING')
            print('  [FAIL] <itunes:owner>/<itunes:email> MISSING')
    else:
        bugs.append('14.3: <itunes:owner> MISSING')
        print('  [FAIL] <itunes:owner> MISSING')
    
    # itunes:explicit (13.7)
    ch_explicit = channel.find('itunes:explicit', ns)
    if ch_explicit is not None:
        if ch_explicit.text == 'no':
            print(f'  [PASS] <itunes:explicit>: no')
        else:
            bugs.append(f'13.7: Channel <itunes:explicit> is "{ch_explicit.text}" but MUST be "no"')
            print(f'  [FAIL] <itunes:explicit> is "{ch_explicit.text}" — MUST be "no" (Prompt 13.7)')
    else:
        bugs.append('14.3: <itunes:explicit> MISSING')
        print('  [FAIL] <itunes:explicit> MISSING')
    
    # itunes:image
    ch_img = channel.find('itunes:image', ns)
    if ch_img is not None:
        print(f'  [PASS] <itunes:image>: {ch_img.get("href", "NO HREF!")}')
    else:
        bugs.append('14.3: Channel <itunes:image> MISSING')
        print('  [FAIL] <itunes:image> MISSING')
    
    # itunes:category + sub-category (13.5 + 14.3)
    ch_cat = channel.find('itunes:category', ns)
    if ch_cat is not None:
        cat_text = ch_cat.get('text', '')
        sub_cat = ch_cat.find('itunes:category', ns)
        if sub_cat is not None:
            sub_text = sub_cat.get('text', '')
            print(f'  [PASS] <itunes:category>: {cat_text} > {sub_text}')
            all_categories.append((folder, f'{cat_text} > {sub_text}'))
        else:
            bugs.append('14.3: <itunes:category> has NO sub-category (Prompt 14.3 says required)')
            print(f'  [FAIL] <itunes:category> "{cat_text}" but NO sub-category! (Prompt 14.3)')
            all_categories.append((folder, cat_text))
    else:
        bugs.append('14.3: <itunes:category> MISSING')
        print('  [FAIL] <itunes:category> MISSING')
    
    # googleplay:author
    gp_author = channel.find('googleplay:author', ns)
    if gp_author is not None:
        print(f'  [PASS] <googleplay:author>: {gp_author.text}')
    else:
        bugs.append('14.3: <googleplay:author> MISSING')
        print('  [FAIL] <googleplay:author> MISSING')
    
    # googleplay:image
    gp_img = channel.find('googleplay:image', ns)
    if gp_img is not None:
        print(f'  [PASS] <googleplay:image>: {gp_img.get("href", "NO HREF")}')
    else:
        bugs.append('14.3: <googleplay:image> MISSING')
        print('  [FAIL] <googleplay:image> MISSING')
    
    # <image> standard RSS tag
    std_img = channel.find('image')
    if std_img is not None:
        img_url = std_img.find('url')
        img_title = std_img.find('title')
        img_link = std_img.find('link')
        if img_url is not None:
            print(f'  [PASS] <image>/<url>: {img_url.text}')
        else:
            bugs.append('14.3: <image>/<url> MISSING')
            print('  [FAIL] <image>/<url> MISSING')
        if img_title is not None:
            print(f'  [PASS] <image>/<title>: {img_title.text}')
        else:
            bugs.append('14.3: <image>/<title> MISSING')
            print('  [FAIL] <image>/<title> MISSING')
        if img_link is not None:
            print(f'  [PASS] <image>/<link>: {img_link.text}')
        else:
            bugs.append('14.3: <image>/<link> MISSING')
            print('  [FAIL] <image>/<link> MISSING')
    else:
        bugs.append('14.3: Standard RSS <image> tag MISSING')
        print('  [FAIL] Standard RSS <image> tag MISSING')
    
    # =============================================
    # PROMPT 14.4 — Item Tags (Complete List)
    # =============================================
    if item is not None:
        print('\n  --- PROMPT 14.4: Item Tags ---')
        
        # title
        it_title = item.find('title')
        if it_title is not None:
            print(f'  [PASS] <title>: {it_title.text[:50]}...')
            # 13.12 — Title Tag Safety
            unsafe_chars = ['₹', '\u2019', '\u2018', '—', '&']
            for c in unsafe_chars:
                if c in it_title.text:
                    bugs.append(f'13.12: Title contains unsafe char "{c}" — can crash XML parsers')
                    print(f'  [FAIL] 13.12: Title has unsafe char "{c}" — Use Rs., -, etc.')
        else:
            bugs.append('14.4: Item <title> MISSING')
            print('  [FAIL] <title> MISSING')
        
        # itunes:author
        it_author = item.find('itunes:author', ns)
        if it_author is not None:
            print(f'  [PASS] <itunes:author>: {it_author.text}')
        else:
            bugs.append('14.4: Item <itunes:author> MISSING')
            print('  [FAIL] <itunes:author> MISSING')
        
        # itunes:summary
        it_summary = item.find('itunes:summary', ns)
        if it_summary is not None and it_summary.text:
            word_count = len(it_summary.text.split())
            print(f'  [PASS] <itunes:summary>: present ({word_count} words)')
        else:
            bugs.append('14.4: Item <itunes:summary> MISSING')
            print('  [FAIL] <itunes:summary> MISSING')
        
        # itunes:image
        it_img = item.find('itunes:image', ns)
        if it_img is not None:
            print(f'  [PASS] <itunes:image>: {it_img.get("href", "NO HREF")}')
        else:
            bugs.append('14.4: Item <itunes:image> MISSING')
            print('  [FAIL] <itunes:image> MISSING')
        
        # description
        it_desc = item.find('description')
        if it_desc is not None and it_desc.text:
            word_count = len(it_desc.text.split())
            print(f'  [PASS] <description>: present ({word_count} words)')
        else:
            bugs.append('14.4: Item <description> MISSING')
            print('  [FAIL] <description> MISSING')
        
        # enclosure (13.11)
        it_enc = item.find('enclosure')
        if it_enc is not None:
            enc_url = it_enc.get('url', '')
            enc_type = it_enc.get('type', '')
            enc_length = it_enc.get('length', '0')
            print(f'  [PASS] <enclosure> url: {enc_url}')
            if enc_type != 'audio/mpeg':
                bugs.append(f'13.11: enclosure type is "{enc_type}" but should be "audio/mpeg"')
                print(f'  [FAIL] enclosure type="{enc_type}" — should be "audio/mpeg" (Prompt 13.11)')
            else:
                print(f'  [PASS] enclosure type: audio/mpeg')
            if int(enc_length) < 500000:
                bugs.append(f'13.11: enclosure length={enc_length} — TOO SMALL (min 500000 for 3-min audio)')
                print(f'  [FAIL] enclosure length={enc_length} — TOO SMALL (Prompt 13.11: min 500000)')
            else:
                print(f'  [PASS] enclosure length: {enc_length}')
        else:
            bugs.append('14.4: <enclosure> MISSING')
            print('  [FAIL] <enclosure> MISSING')
        
        # guid (13.9)
        it_guid = item.find('guid')
        if it_guid is not None:
            print(f'  [PASS] <guid>: {it_guid.text}')
            all_guids.append((folder, it_guid.text))
        else:
            bugs.append('14.4: <guid> MISSING')
            print('  [FAIL] <guid> MISSING')
        
        # pubDate (13.4)
        it_pubdate = item.find('pubDate')
        if it_pubdate is not None:
            print(f'  [PASS] <pubDate>: {it_pubdate.text}')
            all_pubdates.append((folder, it_pubdate.text))
        else:
            bugs.append('14.4: <pubDate> MISSING')
            print('  [FAIL] <pubDate> MISSING')
        
        # itunes:duration (13.8)
        it_dur = item.find('itunes:duration', ns)
        if it_dur is not None:
            dur_val = it_dur.text
            print(f'  [PASS] <itunes:duration>: {dur_val}')
            # Check if duration matches guidelines (should be 180 for 3 min)
            try:
                if ':' not in dur_val:
                    dur_secs = int(dur_val)
                    if dur_secs < 180:
                        warnings.append(f'13.8: duration is {dur_secs}s (under 3 minutes) — Amazon may reject')
                        print(f'  [WARN] duration {dur_secs}s is under 3 minutes — Amazon prefers 180+')
            except:
                pass
        else:
            bugs.append('13.8: <itunes:duration> MISSING (MANDATORY)')
            print('  [FAIL] <itunes:duration> MISSING (Prompt 13.8: MANDATORY)')
        
        # itunes:explicit (13.7)
        it_explicit = item.find('itunes:explicit', ns)
        if it_explicit is not None:
            if it_explicit.text == 'no':
                print(f'  [PASS] <itunes:explicit>: no')
            else:
                bugs.append(f'13.7: Item <itunes:explicit> is "{it_explicit.text}" but MUST be "no"')
                print(f'  [FAIL] <itunes:explicit> is "{it_explicit.text}" — MUST be "no" (Prompt 13.7)')
        else:
            bugs.append('14.4: Item <itunes:explicit> MISSING')
            print('  [FAIL] <itunes:explicit> MISSING')
        
        # itunes:episodeType
        it_eptype = item.find('itunes:episodeType', ns)
        if it_eptype is not None:
            print(f'  [PASS] <itunes:episodeType>: {it_eptype.text}')
        else:
            bugs.append('14.4: <itunes:episodeType> MISSING')
            print('  [FAIL] <itunes:episodeType> MISSING')
        
        # author (email)
        it_author_email = item.find('author')
        if it_author_email is not None:
            print(f'  [PASS] <author>: {it_author_email.text}')
        else:
            bugs.append('14.4: Item <author> (email) MISSING')
            print('  [FAIL] <author> (email) MISSING')
        
        # link
        it_link = item.find('link')
        if it_link is not None:
            print(f'  [PASS] <link>: {it_link.text}')
        else:
            bugs.append('14.4: Item <link> MISSING')
            print('  [FAIL] <link> MISSING')
    
    # =============================================
    # PROMPT 14.1 — 4-Place Content Mirroring Check
    # =============================================
    print('\n  --- PROMPT 14.1: 4-Place Content Mirroring ---')
    ch_summary_text = (channel.find('itunes:summary', ns).text or '') if channel.find('itunes:summary', ns) is not None else ''
    ch_desc_text = (channel.find('description').text or '') if channel.find('description') is not None else ''
    it_summary_text = ''
    it_desc_text = ''
    if item is not None:
        it_summary_text = (item.find('itunes:summary', ns).text or '') if item.find('itunes:summary', ns) is not None else ''
        it_desc_text = (item.find('description').text or '') if item.find('description') is not None else ''
    
    texts = [ch_summary_text.strip(), ch_desc_text.strip(), it_summary_text.strip(), it_desc_text.strip()]
    if len(set(texts)) == 1 and texts[0] != '':
        print('  [PASS] All 4 description/summary tags have IDENTICAL content')
    else:
        different_count = len(set(texts))
        bugs.append(f'14.1: 4-Place Content Mirroring FAILED — {different_count} different versions found')
        print(f'  [FAIL] Content NOT identical across all 4 tags ({different_count} variants found)')
        if ch_summary_text != ch_desc_text:
            print(f'         Channel summary vs Channel description: DIFFERENT')
        if it_summary_text != it_desc_text:
            print(f'         Item summary vs Item description: DIFFERENT')
        if ch_summary_text != it_summary_text:
            print(f'         Channel summary vs Item summary: DIFFERENT')
    
    # =============================================
    # PROMPT 13.12 — Special Chars in <title> (outside CDATA)
    # =============================================
    print('\n  --- PROMPT 13.12: Title Tag Safety ---')
    if ch_title is not None and it_title is not None:
        for label, title_text in [('Channel', ch_title.text), ('Item', it_title.text)]:
            unsafe_found = []
            if '₹' in title_text:
                unsafe_found.append('₹')
            if '\u2019' in title_text or '\u2018' in title_text:
                unsafe_found.append('smart quotes')
            if '—' in title_text:
                unsafe_found.append('em-dash (—)')
            if '&' in title_text and '&amp;' not in raw:
                unsafe_found.append('&')
            if unsafe_found:
                bugs.append(f'13.12: {label} title has unsafe chars: {", ".join(unsafe_found)}')
                print(f'  [FAIL] {label} title has: {", ".join(unsafe_found)} — Use Rs., -, etc.')
            else:
                print(f'  [PASS] {label} title: No unsafe special characters')
    
    # =============================================
    # SUMMARY
    # =============================================
    print(f'\n  {"="*50}')
    print(f'  RESULTS FOR {folder}/feed.xml:')
    print(f'  BUGS (Must Fix): {len(bugs)}')
    print(f'  WARNINGS (Recommended): {len(warnings)}')
    print(f'  {"="*50}')
    for i, b in enumerate(bugs, 1):
        print(f'  BUG #{i}: {b}')
    for i, w in enumerate(warnings, 1):
        print(f'  WARN #{i}: {w}')

# =============================================
# CROSS-FEED CHECKS (Prompt 13.2, 13.3, 13.4, 13.5, 13.10)
# =============================================
print(f'\n{"="*60}')
print(f'  CROSS-FEED SPAM NETWORK CHECKS (Prompt 13)')
print(f'{"="*60}')

# 13.2 — Unique Author Names
print('\n  --- 13.2: Unique Author Names ---')
author_names = [a[1] for a in all_authors]
if len(author_names) != len(set(author_names)):
    print(f'  [FAIL] DUPLICATE author names found! (Prompt 13.2: Spam Network Detection)')
    for a in all_authors:
        print(f'         {a[0]}: {a[1]}')
else:
    print(f'  [PASS] All author names are unique')
    for a in all_authors:
        print(f'         {a[0]}: {a[1]}')

# 13.3 — Unique <link> Tags
print('\n  --- 13.3: Unique <link> Tags ---')
link_urls = [l[1] for l in all_links]
if len(link_urls) != len(set(link_urls)):
    print(f'  [FAIL] DUPLICATE <link> URLs found! (Prompt 13.3: 100% spam footprint)')
    for l in all_links:
        print(f'         {l[0]}: {l[1]}')
else:
    print(f'  [PASS] All <link> URLs are unique')
    for l in all_links:
        print(f'         {l[0]}: {l[1]}')

# 13.4 — Vary pubDate
print('\n  --- 13.4: Vary pubDate ---')
pubdate_values = [p[1] for p in all_pubdates]
if len(pubdate_values) != len(set(pubdate_values)):
    print(f'  [FAIL] IDENTICAL pubDates found! (Prompt 13.4: Spam signal)')
    for p in all_pubdates:
        print(f'         {p[0]}: {p[1]}')
else:
    print(f'  [PASS] All pubDates are different')
    for p in all_pubdates:
        print(f'         {p[0]}: {p[1]}')

# 13.5 — Vary itunes:category
print('\n  --- 13.5: Vary itunes:category ---')
cat_values = [c[1] for c in all_categories]
if len(cat_values) != len(set(cat_values)):
    print(f'  [WARN] SAME category on multiple feeds (Prompt 13.5: looks bot-generated)')
    for c in all_categories:
        print(f'         {c[0]}: {c[1]}')
else:
    print(f'  [PASS] Categories are varied')
    for c in all_categories:
        print(f'         {c[0]}: {c[1]}')

# 13.10 — Unique Emails
print('\n  --- 13.10: One Email Per Feed ---')
email_values = [e[1] for e in all_emails]
if len(email_values) != len(set(email_values)):
    print(f'  [FAIL] SAME email on multiple feeds! (Prompt 13.10: Duplicate account abuse)')
    for e in all_emails:
        print(f'         {e[0]}: {e[1]}')
else:
    print(f'  [PASS] All emails are unique')
    for e in all_emails:
        print(f'         {e[0]}: {e[1]}')

print(f'\n{"="*60}')
print(f'  FULL VALIDATION COMPLETE')
print(f'{"="*60}')
