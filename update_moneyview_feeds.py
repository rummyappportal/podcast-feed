import os
import re

base_dir = r"c:\Users\dinesh\Downloads\mojolocontentgudlines\podcast-feed-repo"

moneyview_folders = [
    "moneyview-mveqhrbq",
    "moneyview-rnpzh7jm-11jul2026",
    "moneyview-rnpzh7jm-business",
    "moneyview-rnpzh7jm-medical",
    "moneyview-rnpzh7jm-student",
    "moneyview-yapukznv",
    "moneyview-yapukznv-2",
    "moneyview-zyw"
]

for folder in moneyview_folders:
    feed_path = os.path.join(base_dir, folder, "feed.xml")
    if not os.path.exists(feed_path):
        print(f"Skipping {folder}, feed.xml not found")
        continue
        
    with open(feed_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Extract existing CDATA block from channel description
    # Use re.DOTALL to match across newlines
    match = re.search(r'<description><!\[CDATA\[(.*?)\]\]></description>', content, re.DOTALL)
    if not match:
        print(f"Failed to find CDATA in {folder}")
        continue
        
    cdata = match.group(1)
    
    # Do not re-process if we already added the bite-sized answer
    if "The 100% verified Money View promo code" in cdata:
        print(f"{folder} already updated.")
        continue
        
    # Extract promo code dynamically
    # E.g., REFERRAL CODE: MVEQHRBQ or PROMO CODE: RNPZH7JM
    code_match = re.search(r'(?:REFERRAL|PROMO) CODE:\s*([A-Z0-9]+)', cdata)
    if not code_match:
        # Fallback to folder name if regex fails
        fallback_code = folder.split('-')[1].upper()
        print(f"Warning: Could not extract code from text in {folder}, using fallback {fallback_code}")
        extracted_code = fallback_code
    else:
        extracted_code = code_match.group(1)
        
    # 1. Upgrade headings
    cdata = cdata.replace("<h3>", "<h2>").replace("</h3>", "</h2>")
    
    # 2. Prepare Bite-Sized Answer
    bite_sized_answer = f"""<p>The 100% verified Money View promo code for personal loans is <b>{extracted_code}</b>. By applying this exact code during the final e-sign stage of your loan application, you are guaranteed to receive a flat cashback directly into your registered bank account. This exclusive discount is specifically designed to help borrowers recover the heavy processing fees typically deducted from large loan amounts. It is currently active for all new users in 2026 and provides the highest available cash reward on the platform without altering your approved interest rate or EMI schedule.</p>
<hr/>
"""
    
    # Prepend it
    new_cdata = bite_sized_answer + cdata
    
    # 3. Mirror the new CDATA block across all 4 summary/description tags
    wrapped_cdata = f"<![CDATA[{new_cdata}]]>"
    
    # Replace channel summary
    content = re.sub(r'<itunes:summary><!\[CDATA\[.*?\]\]></itunes:summary>', f'<itunes:summary>{wrapped_cdata}</itunes:summary>', content, flags=re.DOTALL, count=1)
    
    # Replace channel description
    content = re.sub(r'<description><!\[CDATA\[.*?\]\]></description>', f'<description>{wrapped_cdata}</description>', content, flags=re.DOTALL, count=1)
    
    # Replace item summary
    content = re.sub(r'<itunes:summary><!\[CDATA\[.*?\]\]></itunes:summary>', f'<itunes:summary>{wrapped_cdata}</itunes:summary>', content, flags=re.DOTALL, count=1)
    
    # Replace item description
    content = re.sub(r'<description><!\[CDATA\[.*?\]\]></description>', f'<description>{wrapped_cdata}</description>', content, flags=re.DOTALL, count=1)
    
    with open(feed_path, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print(f"Successfully updated {folder} (Code injected: {extracted_code})")
