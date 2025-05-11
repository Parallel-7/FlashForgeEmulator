from PIL import Image, ImageDraw, ImageFont
import os

def create_standard_thumbnail(path, size=(200, 200)):
    """
    Create a standard thumbnail image that follows valid PNG format.
    This will create a simple geometric pattern that should be easily recognizable.
    """
    # Create a new image with a blue background
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
    img.save(path, 'PNG')
    print(f"Standard thumbnail created at: {path}")

if __name__ == "__main__":
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "standard_thumbnail.png")
    create_standard_thumbnail(output_path)
