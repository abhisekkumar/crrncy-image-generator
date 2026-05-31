"""
Generate 1 more afternoon_cloudy image
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from generate_cb_images import (
    TIMES_OF_DAY, SEASONS, GLOBAL_VISUAL_DNA, COMPOSITION_RULE,
    generate_image, OUTPUT_DIR
)

MISSING_IMAGES = [
    {
        "folder": "afternoon_cloudy",
        "time": "afternoon",
        "season": "summer",
        "id": "patagonia_cloudy_afternoon",
        "prompt": "Patagonia Torres del Paine summer AFTERNOON cloudy, BRIGHT OVERCAST DAYLIGHT diffused through dramatic clouds, turquoise lake, rugged peaks, midday grey light, NOT sunset NOT evening"
    },
]


def main():
    print("Generating 1 More Afternoon Cloudy Image")
    
    for img in MISSING_IMAGES:
        folder = OUTPUT_DIR / img["folder"]
        filename = f"{img['time']}_{img['season']}_{img['id']}.png"
        output_path = folder / filename
        
        if output_path.exists():
            print(f"Skipping (exists): {filename}")
            return
        
        print(f"Generating: {filename}")
        
        time_data = TIMES_OF_DAY.get(img["time"], {})
        season_data = SEASONS.get(img["season"], {})
        
        full_prompt = f"""
{GLOBAL_VISUAL_DNA}

{COMPOSITION_RULE}

SCENE: {img['prompt']}

TIME OF DAY - AFTERNOON (NOT EVENING):
- MIDDAY/AFTERNOON with sun HIGH in sky (hidden by clouds)
- BRIGHT DIFFUSED daylight through overcast
- NO warm sunset colors - use COOL grey tones
- Sky grey/white overcast, NOT sunset colors
- Feels like 2pm, NOT 7pm

SEASON - {img['season'].upper()}:
{season_data.get('atmosphere', '')}

CRITICAL FORMAT:
- ONE SINGLE photograph filling 100% canvas
- NO borders of any color
- FULL BLEED to all edges
"""
        
        success = generate_image(full_prompt, output_path)
        print(f"  {'✓ Success' if success else '✗ Failed'}")


if __name__ == "__main__":
    main()
