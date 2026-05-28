"""
Generate the remaining 8 missing images to fill gaps
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from generate_cb_images import (
    TIMES_OF_DAY, SEASONS, GLOBAL_VISUAL_DNA, COMPOSITION_RULE,
    generate_image, OUTPUT_DIR
)

# 8 specific missing images with new unique scenes
MISSING_IMAGES = [
    # AFTERNOON CLEAR - need 5 (one per season + 1 extra)
    {
        "folder": "afternoon",
        "time": "afternoon",
        "season": "spring",
        "id": "amsterdam_keukenhof",
        "prompt": "Keukenhof Gardens Netherlands spring afternoon, millions of tulips in bloom, windmills, canals, vibrant colors, blue sky"
    },
    {
        "folder": "afternoon",
        "time": "afternoon",
        "season": "summer",
        "id": "positano_italy",
        "prompt": "Positano Italy Amalfi Coast summer afternoon, colorful cliffside houses, turquoise Mediterranean, bright sun, luxury boats"
    },
    {
        "folder": "afternoon",
        "time": "afternoon",
        "season": "autumn",
        "id": "blue_ridge_parkway",
        "prompt": "Blue Ridge Parkway Virginia autumn afternoon, winding road through fall foliage, Appalachian Mountains, golden light"
    },
    {
        "folder": "afternoon",
        "time": "afternoon",
        "season": "winter",
        "id": "finnish_lake_winter",
        "prompt": "Finnish Lakeland winter afternoon, frozen lake, snow-covered pine forests, wooden sauna by shore, soft winter light"
    },
    {
        "folder": "afternoon",
        "time": "afternoon",
        "season": "spring",
        "id": "wisteria_japan",
        "prompt": "Ashikaga Flower Park Japan spring afternoon, purple wisteria tunnels in full bloom, magical light filtering through"
    },
    # NIGHT CLEAR - need 1
    {
        "folder": "night",
        "time": "night",
        "season": "summer",
        "id": "maldives_night_stars",
        "prompt": "Maldives overwater villa summer night, bioluminescent beach glowing blue, Milky Way stars, crystal clear water reflecting stars"
    },
    # NIGHT CLOUDY - need 2
    {
        "folder": "night_cloudy",
        "time": "night",
        "season": "autumn",
        "id": "london_fog_autumn",
        "prompt": "London autumn cloudy night, Tower Bridge lights diffused through fog, Thames moody, city lights glowing atmospheric"
    },
    {
        "folder": "night_cloudy",
        "time": "night",
        "season": "winter",
        "id": "tokyo_cloudy_winter",
        "prompt": "Tokyo Shinjuku winter cloudy night, neon signs glowing through low clouds, skyscrapers disappearing into mist, cyberpunk mood"
    },
]


def main():
    print("=" * 60)
    print("Generating 8 Missing Images")
    print("=" * 60)
    print()
    
    generated = 0
    failed = 0
    
    for i, img in enumerate(MISSING_IMAGES, 1):
        folder = OUTPUT_DIR / img["folder"]
        folder.mkdir(parents=True, exist_ok=True)
        
        filename = f"{img['time']}_{img['season']}_{img['id']}.png"
        output_path = folder / filename
        
        if output_path.exists():
            print(f"[{i}/8] Skipping (exists): {filename}")
            continue
        
        print(f"[{i}/8] Generating: {filename}")
        
        time_data = TIMES_OF_DAY.get(img["time"], {})
        season_data = SEASONS.get(img["season"], {})
        
        full_prompt = f"""
{GLOBAL_VISUAL_DNA}

{COMPOSITION_RULE}

SCENE: {img['prompt']}

TIME OF DAY - {img['time'].upper()}:
Lighting style: {time_data.get('lighting', '')}
Sky and color palette: {time_data.get('palette', '')}

SEASON - {img['season'].upper()}:
Seasonal characteristics: {season_data.get('elements', '')}
Overall atmosphere: {season_data.get('atmosphere', '')}

CRITICAL REQUIREMENTS:
- ONE SINGLE CONTINUOUS LANDSCAPE IMAGE that fills the ENTIRE frame edge-to-edge
- NO collages, NO grids, NO stacked images, NO duplicate images
- NO white borders, NO black borders, NO letterboxing, NO margins
- Image MUST fill the full canvas with NO empty space on any side
- NO text, watermarks, or overlays
- Pure seamless landscape photography only
"""
        
        success = generate_image(full_prompt, output_path)
        
        if success:
            generated += 1
            print(f"  ✓ Success")
        else:
            failed += 1
            print(f"  ✗ Failed")
    
    print()
    print("=" * 60)
    print(f"COMPLETE: {generated} generated, {failed} failed")
    print("=" * 60)


if __name__ == "__main__":
    main()
