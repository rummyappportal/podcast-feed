import os
import re

updates = {
    r"c:\Users\dinesh\Downloads\mojolocontentgudlines\podcast-feed-repo\kreditbee\feed.xml": "Mon, 27 Jul 2026 08:00:00 GMT",
    r"c:\Users\dinesh\Downloads\mojolocontentgudlines\podcast-feed-repo\kreditbee-account2\feed.xml": "Mon, 27 Jul 2026 10:00:00 GMT",
    r"c:\Users\dinesh\Downloads\mojolocontentgudlines\podcast-feed-repo\bachat\feed.xml": "Mon, 27 Jul 2026 12:00:00 GMT",
    r"c:\Users\dinesh\Downloads\mojolocontentgudlines\podcast-feed-repo\branch\feed.xml": "Mon, 27 Jul 2026 14:00:00 GMT"
}

for filepath, new_date in updates.items():
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace the pubDate using regex
        new_content = re.sub(r'<pubDate>.*?</pubDate>', f'<pubDate>{new_date}</pubDate>', content)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated: {os.path.basename(os.path.dirname(filepath))} -> {new_date}")
    except Exception as e:
        print(f"Error updating {filepath}: {e}")
