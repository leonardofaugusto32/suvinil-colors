import json
import math
from typing import List, Tuple
from PIL import Image, ImageDraw, ImageFont
import os
import io

def parse_rgb(rgb_str: str) -> Tuple[int, int, int]:
    """
    Parse RGB string in format (R,G,B) or R,G,B into tuple of integers.
    """
    # Remove parentheses and spaces
    clean_str = rgb_str.replace('(', '').replace(')', '').replace(' ', '')
    r, g, b = map(int, clean_str.split(','))
    return (r, g, b)

def calculate_color_distance(color1: Tuple[int, int, int], color2: Tuple[int, int, int]) -> float:
    """
    Calculate Euclidean distance between two RGB colors.
    """
    r1, g1, b1 = color1
    r2, g2, b2 = color2
    return math.sqrt((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2)

def create_color_visualization(target_rgb: Tuple[int, int, int], similar_colors: List[dict], output_file: str = 'color_comparison.png', img_bytes: io.BytesIO = None):
    """
    Create a visual comparison of the target color and similar colors.
    
    Args:
        target_rgb: The target RGB color
        similar_colors: List of similar colors
        output_file: Path to save the image (optional)
        img_bytes: BytesIO object to save the image to (optional)
    """
    # Image dimensions and layout
    width = 1000
    color_block_width = 800
    color_height = 120
    text_height = 30
    padding = 40
    spacing = 60
    
    # Calculate total height needed
    section_height = color_height + text_height + spacing
    total_sections = len(similar_colors) + 1  # +1 for target color
    height = (section_height * total_sections) + padding * 2
    
    # Create image with white background
    img = Image.new('RGB', (width, height), (245, 245, 245))  # Slight off-white for better contrast
    draw = ImageDraw.Draw(img)
    
    try:
        # Try to load a font (fallback to default if not available)
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
    except:
        font = ImageFont.load_default()
    
    # Calculate left margin to center color blocks
    left_margin = (width - color_block_width) // 2
    
    # Draw target color
    y = padding
    # Draw color block
    draw.rectangle(
        [left_margin, y, left_margin + color_block_width, y + color_height],
        fill=target_rgb,
        outline=(200, 200, 200),  # Subtle border
        width=2
    )
    
    # Center and draw text
    text = f"Cor Original RGB{target_rgb}"
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_x = (width - text_width) // 2
    draw.text((text_x, y + color_height + 10), text, fill=(50, 50, 50), font=font)
    
    # Draw similar colors
    for i, color in enumerate(similar_colors):
        y = padding + (i + 1) * section_height
        color_rgb = parse_rgb(color['rgb'])
        
        # Draw color block
        draw.rectangle(
            [left_margin, y, left_margin + color_block_width, y + color_height],
            fill=color_rgb,
            outline=(200, 200, 200),  # Subtle border
            width=2
        )
        
        # Prepare text lines
        text1 = f"{color['name']} - {color['code']}"
        text2 = f"RGB{color['rgb']} - Distância: {color['distance']:.2f}"
        
        # Center and draw first line
        text1_bbox = draw.textbbox((0, 0), text1, font=font)
        text1_width = text1_bbox[2] - text1_bbox[0]
        text1_x = (width - text1_width) // 2
        draw.text((text1_x, y + color_height + 10), text1, fill=(50, 50, 50), font=font)
    
    # Add subtle background grid (optional)
    grid_spacing = 20
    grid_color = (240, 240, 240)
    for x in range(0, width, grid_spacing):
        draw.line([(x, 0), (x, height)], fill=grid_color)
    for y in range(0, height, grid_spacing):
        draw.line([(0, y), (width, y)], fill=grid_color)
    
    # Save with high quality settings
    save_params = {
        'format': 'PNG',
        'quality': 95,
        'dpi': (300, 300),
        'optimize': True
    }
    
    if output_file:
        img.save(output_file, **save_params)
        print(f"\nVisualização salva em: {output_file}")
        try:
            os.system(f"open {output_file}")  # macOS
        except:
            pass
    
    if img_bytes is not None:
        img.save(img_bytes, **save_params)

def find_similar_colors(target_rgb: Tuple[int, int, int], colors_data: dict, num_results: int = 5) -> List[dict]:
    """
    Find the most similar colors to the target RGB color.
    """
    color_distances = []
    
    # Process each hue and its colors
    for hue_data in colors_data['items']:
        for color in hue_data['colors']:
            # Parse the RGB string from Suvinil's format
            color_rgb = parse_rgb(color['rgb'])
            
            # Calculate distance
            distance = calculate_color_distance(target_rgb, color_rgb)
            
            # Store color info with distance
            color_info = {
                'name': color['name'],
                'code': color['code'],
                'rgb': color['rgb'],
                'distance': distance
            }
            color_distances.append(color_info)
    
    # Sort by distance and get top N results
    return sorted(color_distances, key=lambda x: x['distance'])[:num_results]

def main():
    print("\n=== 👁️ OLHO DA MEL - Encontrar Cores Similares Suvinil 👁️ ===")
    print("Digite os valores RGB no formato: R,G,B")
    print("Exemplo: 158,76,29")
    
    # Get RGB input from user
    while True:
        try:
            rgb_input = input("\nRGB: ")
            target_rgb = parse_rgb(rgb_input)
            
            # Validate RGB values
            if not all(0 <= x <= 255 for x in target_rgb):
                raise ValueError("Valores RGB devem estar entre 0 e 255")
            break
        except ValueError as e:
            print(f"Erro: {str(e)}")
            print("Por favor, tente novamente no formato R,G,B")
    
    try:
        # Load color data
        with open('suvinil_colors.json', 'r', encoding='utf-8') as f:
            colors_data = json.load(f)
        
        # Find similar colors
        similar_colors = find_similar_colors(target_rgb, colors_data)
        
        # Display results
        print("\nCores mais próximas encontradas:")
        print("-" * 50)
        for i, color in enumerate(similar_colors, 1):
            print(f"{i}. {color['name']}")
            print(f"   Código: {color['code']}")
            print(f"   RGB: {color['rgb']}")
            print(f"   Distância: {color['distance']:.2f}")
            print("-" * 50)
        
        # Create and show visual comparison
        create_color_visualization(target_rgb, similar_colors)
            
    except FileNotFoundError:
        print("\nErro: Arquivo suvinil_colors.json não encontrado.")
        print("Execute primeiro o script try.py para gerar o arquivo de cores.")
    except Exception as e:
        print(f"\nErro inesperado: {str(e)}")

if __name__ == "__main__":
    main() 