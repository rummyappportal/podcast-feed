import os
from PIL import Image

def resize_image(image_path, target_size=(1400, 1400)):
    try:
        if not os.path.exists(image_path):
            print(f"File not found: {image_path}")
            return
            
        with Image.open(image_path) as img:
            print(f"Original size of {os.path.basename(image_path)}: {img.size}")
            
            # Resize using high-quality filter
            resized_img = img.resize(target_size, Image.Resampling.LANCZOS)
            
            # Save back to the same file
            resized_img.save(image_path)
            print(f"Successfully resized {os.path.basename(image_path)} to {target_size}")
            
    except Exception as e:
        print(f"Error processing {image_path}: {e}")

if __name__ == "__main__":
    img1 = r"c:\Users\dinesh\Downloads\mojolocontentgudlines\podcast-feed-repo\kreditbee\cover.png"
    img2 = r"c:\Users\dinesh\Downloads\mojolocontentgudlines\podcast-feed-repo\kreditbee-account2\cover.jpg"
    
    resize_image(img1)
    resize_image(img2)
