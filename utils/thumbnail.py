import os
from PIL import Image, ImageDraw

def create_standard_thumbnail():
    """Create a standard thumbnail image for the emulator"""
    output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "standard_thumbnail.png")
    
    # If the thumbnail already exists, don't recreate it
    if os.path.exists(output_path):
        return output_path
    
    try:
        # Create a new image with a blue background
        size = (200, 200)
        background_color = (0, 100, 200)
        img = Image.new('RGB', size, background_color)
        draw = ImageDraw.Draw(img)
        
        # Draw some shapes to make it recognizable
        width, height = size
        
        # Draw border
        border_color = (255, 255, 255)
        border_width = 10
        draw.rectangle([0, 0, width-1, height-1], outline=border_color, width=border_width)
        
        # Draw diagonal lines
        draw.line([(0, 0), (width, height)], fill=(255, 0, 0), width=5)
        draw.line([(0, height), (width, 0)], fill=(255, 0, 0), width=5)
        
        # Draw center circle
        draw.ellipse([width//4, height//4, 3*width//4, 3*height//4], outline=(0, 255, 0), width=5)
        
        # Save the image
        img.save(output_path, 'PNG')
        print(f"Standard thumbnail created at: {output_path}")
        return output_path
    except Exception as e:
        print(f"Error creating thumbnail: {str(e)}")
        return None
