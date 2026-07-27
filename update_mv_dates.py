import os
import re

base_dir = r"c:\Users\dinesh\Downloads\mojolocontentgudlines\podcast-feed-repo"

updates = {
    "moneyview-mveqhrbq": "Mon, 27 Jul 2026 10:00:00 GMT",
    "moneyview-rnpzh7jm-11jul2026": "Mon, 27 Jul 2026 11:00:00 GMT",
    "moneyview-rnpzh7jm-business": "Mon, 27 Jul 2026 12:00:00 GMT",
    "moneyview-rnpzh7jm-medical": "Mon, 27 Jul 2026 13:00:00 GMT",
    "moneyview-rnpzh7jm-student": "Mon, 27 Jul 2026 14:00:00 GMT",
    "moneyview-yapukznv": "Mon, 27 Jul 2026 15:00:00 GMT",
    "moneyview-yapukznv-2": "Mon, 27 Jul 2026 16:00:00 GMT",
    "moneyview-zyw": "Mon, 27 Jul 2026 17:00:00 GMT"
}

for folder, new_date in updates.items():
    feed_path = os.path.join(base_dir, folder, "feed.xml")
    if not os.path.exists(feed_path):
        continue
        
    with open(feed_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Replace the pubDate using regex
    new_content = re.sub(r'<pubDate>.*?</pubDate>', f'<pubDate>{new_date}</pubDate>', content)
    
    with open(feed_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"Updated: {folder} -> {new_date}")
