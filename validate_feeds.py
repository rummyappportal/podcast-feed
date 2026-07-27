import xml.etree.ElementTree as ET
import os
import re

files = [
    r'c:\Users\dinesh\Downloads\mojolocontentgudlines\podcast-feed-repo\kreditbee\feed.xml',
    r'c:\Users\dinesh\Downloads\mojolocontentgudlines\podcast-feed-repo\kreditbee-account2\feed.xml'
]

for f in files:
    folder = os.path.basename(os.path.dirname(f))
    print(f'=== Checking: {folder}/feed.xml ===')
    try:
        tree = ET.parse(f)
        root = tree.getroot()
        print('  [PASS] XML Parsing: Valid XML (no crash)')
        
        ns = {'itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd'}
        channel = root.find('channel')
        
        # Check channel-level tags
        print('  --- Channel Tags ---')
        channel_checks = [
            ('title', channel.find('title')),
            ('link', channel.find('link')),
            ('language', channel.find('language')),
            ('itunes:author', channel.find('itunes:author', ns)),
            ('itunes:summary', channel.find('itunes:summary', ns)),
            ('description', channel.find('description')),
            ('itunes:explicit', channel.find('itunes:explicit', ns)),
            ('itunes:image', channel.find('itunes:image', ns)),
            ('itunes:category', channel.find('itunes:category', ns)),
            ('itunes:type', channel.find('itunes:type', ns)),
            ('itunes:owner', channel.find('itunes:owner', ns)),
            ('copyright', channel.find('copyright')),
        ]
        
        bugs_found = []
        
        for tag_name, tag_el in channel_checks:
            if tag_el is not None:
                if tag_el.text:
                    val = tag_el.text[:50]
                    print(f'  [PASS] {tag_name}: {val}...' if len(str(tag_el.text)) > 50 else f'  [PASS] {tag_name}: {val}')
                elif tag_el.attrib:
                    print(f'  [PASS] {tag_name}: {dict(tag_el.attrib)}')
                else:
                    print(f'  [PASS] {tag_name}: (has children)')
            else:
                if tag_name == 'copyright':
                    print(f'  [WARN] {tag_name}: MISSING (recommended by guidelines)')
                    bugs_found.append(f'MISSING: {tag_name}')
                else:
                    print(f'  [FAIL] {tag_name}: MISSING!')
                    bugs_found.append(f'MISSING: {tag_name}')
        
        # Check item-level tags
        item = channel.find('item')
        if item is not None:
            print('  --- Item Tags ---')
            item_checks = [
                ('title', item.find('title')),
                ('link', item.find('link')),
                ('itunes:author', item.find('itunes:author', ns)),
                ('itunes:duration', item.find('itunes:duration', ns)),
                ('itunes:summary', item.find('itunes:summary', ns)),
                ('description', item.find('description')),
                ('enclosure', item.find('enclosure')),
                ('guid', item.find('guid')),
                ('pubDate', item.find('pubDate')),
                ('itunes:explicit', item.find('itunes:explicit', ns)),
                ('itunes:episodeType', item.find('itunes:episodeType', ns)),
                ('itunes:image', item.find('itunes:image', ns)),
                ('author', item.find('author')),
            ]
            for tag_name, tag_el in item_checks:
                if tag_el is not None:
                    if tag_el.text:
                        val = tag_el.text[:50]
                        print(f'  [PASS] {tag_name}: {val}...' if len(str(tag_el.text)) > 50 else f'  [PASS] {tag_name}: {val}')
                    elif tag_el.attrib:
                        print(f'  [PASS] {tag_name}: {dict(tag_el.attrib)}')
                    else:
                        print(f'  [PASS] {tag_name}: (present)')
                else:
                    print(f'  [FAIL] {tag_name}: MISSING!')
                    bugs_found.append(f'ITEM MISSING: {tag_name}')
            
            # Check enclosure length
            enc = item.find('enclosure')
            if enc is not None:
                url = enc.get('url', '')
                length = enc.get('length', '0')
                print(f'  [INFO] enclosure URL: {url}')
                if int(length) < 500000:
                    print(f'  [WARN] enclosure length={length} (too small! Guidelines say >= 500000)')
                    bugs_found.append(f'enclosure length too small: {length}')
                else:
                    print(f'  [PASS] enclosure length: {length}')
        
        # Check language
        lang = channel.find('language')
        if lang is not None and lang.text != 'en-us':
            print(f'  [WARN] language="{lang.text}" but guidelines PROMPT 13.7 says "en-us"')
            bugs_found.append(f'language should be "en-us" not "{lang.text}"')
        
        # Check itunes:explicit
        expl = channel.find('itunes:explicit', ns)
        if expl is not None and expl.text != 'no':
            print(f'  [WARN] itunes:explicit="{expl.text}" but guidelines PROMPT 13.7 says "no"')
            bugs_found.append(f'itunes:explicit should be "no" not "{expl.text}"')
        
        # Check item explicit too
        if item is not None:
            item_expl = item.find('itunes:explicit', ns)
            if item_expl is not None and item_expl.text != 'no':
                print(f'  [WARN] Item itunes:explicit="{item_expl.text}" but should be "no"')
                bugs_found.append(f'Item itunes:explicit should be "no" not "{item_expl.text}"')
        
        # Check sub-category
        cat = channel.find('itunes:category', ns)
        if cat is not None:
            sub = cat.find('itunes:category', ns)
            if sub is None:
                print(f'  [WARN] itunes:category has no sub-category (guidelines 14.4 says needed)')
                bugs_found.append('itunes:category missing sub-category')
        
        # Check googleplay namespace
        gp_ns = {'googleplay': 'http://www.google.com/schemas/play-podcasts/1.0'}
        gp_author = channel.find('googleplay:author', gp_ns)
        if gp_author is None:
            print(f'  [WARN] googleplay:author MISSING (Prompt 14.3)')
            bugs_found.append('MISSING: googleplay:author')
        
        # Check xmlns:googleplay in raw file
        with open(f, 'r', encoding='utf-8') as fh:
            raw = fh.read()
        if 'xmlns:googleplay' not in raw:
            print(f'  [WARN] xmlns:googleplay namespace NOT declared in RSS tag (Prompt 14.2)')
            bugs_found.append('MISSING: xmlns:googleplay namespace')
        
        # Check <image> tag (standard RSS)
        img_tag = channel.find('image')
        if img_tag is None:
            print(f'  [WARN] <image> tag MISSING (Prompt 14.3)')
            bugs_found.append('MISSING: <image> tag')
        
        # Summary
        print(f'\n  === TOTAL BUGS/WARNINGS FOUND: {len(bugs_found)} ===')
        for i, b in enumerate(bugs_found, 1):
            print(f'  BUG #{i}: {b}')
        print()
        
    except ET.ParseError as e:
        print(f'  [FATAL] XML Parse Error: {e}')
        print()
