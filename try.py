import requests
import json
from typing import Dict, List
import logging
from datetime import datetime
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'suvinil_api_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)

def get_all_colors(hue_ids: List[int], per_page: int = 1000) -> Dict:
    """
    Fetch all colors from all pages of Suvinil's API.
    
    Args:
        hue_ids: List of hue IDs to fetch
        per_page: Number of items per page (default: 1000)
    
    Returns:
        Dict containing all colors from all pages
    """
    url = 'https://gateway.suvinil.com.br/institucional/colors/ncs/hue'
    
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        'origin': 'https://www.suvinil.com.br',
        'priority': 'u=1, i',
        'referer': 'https://www.suvinil.com.br/',
        'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko)',
        'x-api-key': 'Da8vbICbPu26uOrjsQFKk4Q1T0G7Sg5r3N4oDU4c'
    }
    
    all_data = {'items': []}
    
    # Search across all color fans (1 through 5 to be safe)
    for color_fan_id in range(1, 6):
        params = {
            'hueIds': json.dumps(hue_ids),
            'page': 1,
            'perPage': per_page,
            'colorFanId': color_fan_id
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            if 'items' in data:
                all_data['items'].extend(data['items'])
                logging.info(f'Successfully fetched colors for color fan {color_fan_id}')
            
        except requests.exceptions.RequestException as e:
            logging.error(f'Error fetching data for color fan {color_fan_id}: {str(e)}')
            continue
    
    return all_data

def save_results(data: Dict, filename: str = 'suvinil_colors.json'):
    """Save the results to a JSON file."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logging.info(f"Results saved to {filename}")
    except Exception as e:
        logging.error(f"Error saving results: {str(e)}")

def convert_to_excel(json_file: str = 'suvinil_colors.json', excel_file: str = 'suvinil_colors.xlsx'):
    """
    Convert the JSON data to Excel format.
    
    Args:
        json_file: Input JSON filename
        excel_file: Output Excel filename
    """
    try:
        # Read the JSON file
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Create a list to store all colors
        all_colors = []
        
        # Process each hue and its colors
        for hue_data in data['items']:
            hue_id = hue_data['hueId']
            hue_slug = hue_data['hueSlug']
            main_hue = hue_data['mainHue']
            
            # Process each color in the hue
            for color in hue_data['colors']:
                color_info = {
                    'Hue ID': hue_id,
                    'Hue Name': hue_slug,
                    'Main Hue': main_hue,
                    'Color ID': color['id'],
                    'Name': color['name'],
                    'Code': color['code'],
                    'RGB': color['rgb'],
                    'NCS': color['ncs'],
                    'Slug': color['slug'],
                    'Yearly Color': color.get('yearlyColor', '')
                }
                all_colors.append(color_info)
        
        # Convert to DataFrame
        df = pd.DataFrame(all_colors)
        
        # Sort by Hue ID and Color ID
        df = df.sort_values(['Hue ID', 'Color ID'])
        
        # Save to Excel with auto-adjusted column widths
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Suvinil Colors')
            worksheet = writer.sheets['Suvinil Colors']
            for idx, col in enumerate(df.columns):
                max_length = max(
                    df[col].astype(str).apply(len).max(),
                    len(str(col))
                ) + 2
                worksheet.column_dimensions[chr(65 + idx)].width = max_length
        
        logging.info(f"Excel file created successfully: {excel_file}")
        
    except Exception as e:
        logging.error(f"Error converting to Excel: {str(e)}")
        raise

def main():
    # List of all possible hue IDs
    hue_ids = list(range(1, 16))  # 1 through 15
    
    # Get all colors
    data = get_all_colors(hue_ids)
    
    # Save to JSON
    with open('suvinil_colors.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # Convert to Excel
    convert_to_excel()
    
    logging.info('Process completed successfully!')

if __name__ == "__main__":
    main()
