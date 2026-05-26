"""
Test script for Flux 2 Pro via Black Forest Labs API
Generates 5 test images to evaluate quality before full generation
"""

import os
import time
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BFL_API_KEY = os.getenv("BFL_API_KEY")
if not BFL_API_KEY:
    raise RuntimeError("Missing BFL_API_KEY in .env file")

OUTPUT_DIR = Path("cb_images_flux_test_2k")
OUTPUT_DIR.mkdir(exist_ok=True)

# Image settings (2K resolution)
WIDTH = 2048
HEIGHT = 1152

# Global visual style (same as main script)
VISUAL_STYLE = """
Ultra cinematic dark moody landscape photography,
rich vibrant colors with deep shadows,
dramatic high contrast like Hollywood film cinematography,
dark elegant mood with punchy saturated colors,
deep blacks and rich midtones,
cinematic color grading like Blade Runner or Interstellar,
luxury editorial National Geographic style,
volumetric god rays and atmospheric depth,
premium wide-angle cinematic composition,
Apple promotional imagery quality,
ultra detailed and sharp,
4K UHD resolution,
moody dramatic atmosphere,
photorealistic,
NO text, NO watermarks, NO labels, NO grids, NO collages,
SINGLE continuous image only
"""

# 5 diverse test prompts
TEST_PROMPTS = [
    {
        "id": "morning_spring_cherry_blossom",
        "prompt": f"""
{VISUAL_STYLE}

Japanese cherry blossom trees in full pink bloom along a river,
Mount Fuji in background,
golden sunrise with sun visible on horizon,
pink petals floating in air,
spring morning atmosphere,
deep purple and magenta sky fading to warm orange and gold
"""
    },
    {
        "id": "afternoon_summer_santorini",
        "prompt": f"""
{VISUAL_STYLE}

Santorini Greece blue domes and white buildings,
deep blue Aegean sea,
bright summer sun high in vivid blue sky,
iconic Mediterranean view,
luxury travel photography aesthetic,
deep saturated blue sky with bright white clouds
"""
    },
    {
        "id": "evening_autumn_nyc_sunset",
        "prompt": f"""
{VISUAL_STYLE}

New York City Manhattan skyline at sunset in autumn,
large orange sun setting behind skyscrapers,
Empire State Building silhouette,
golden fall trees in Central Park,
dramatic orange and magenta sky,
city lights beginning to emerge
"""
    },
    {
        "id": "night_winter_northern_lights",
        "prompt": f"""
{VISUAL_STYLE}

Northern Lights aurora borealis over snowy mountain landscape,
green and purple dancing lights in sky,
stars visible,
snow-covered peaks and frozen lake,
magical winter night,
deep navy and purple sky with silver moonlight
"""
    },
    {
        "id": "evening_rain_tokyo",
        "prompt": f"""
{VISUAL_STYLE}

Tokyo rainy evening,
neon lights reflecting in puddles on wet streets,
rain falling,
cherry blossoms with raindrops,
atmospheric Japanese urban night scene,
moody cinematic atmosphere,
warm lights contrasting with cool blue rain
"""
    },
]


def generate_image(prompt: str, output_path: Path) -> bool:
    """Generate image using Flux 2 Pro via BFL API"""
    
    print(f"  Submitting request to Flux 2 Pro...")
    
    # Submit generation request
    try:
        response = requests.post(
            "https://api.bfl.ai/v1/flux-2-pro",
            headers={
                "accept": "application/json",
                "x-key": BFL_API_KEY,
                "Content-Type": "application/json",
            },
            json={
                "prompt": prompt,
                "width": WIDTH,
                "height": HEIGHT,
            },
        )
        response.raise_for_status()
        result = response.json()
    except Exception as e:
        print(f"  Error submitting request: {e}")
        return False
    
    polling_url = result.get("polling_url")
    if not polling_url:
        print(f"  No polling URL returned")
        return False
    
    print(f"  Waiting for generation...")
    
    # Poll for result
    max_attempts = 60  # 5 minutes max
    for attempt in range(max_attempts):
        try:
            poll_response = requests.get(
                polling_url,
                headers={
                    "accept": "application/json",
                    "x-key": BFL_API_KEY,
                },
            )
            poll_response.raise_for_status()
            poll_result = poll_response.json()
        except Exception as e:
            print(f"  Polling error: {e}")
            time.sleep(5)
            continue
        
        status = poll_result.get("status")
        
        if status == "Ready":
            # Get the image URL
            sample_url = poll_result.get("result", {}).get("sample")
            if not sample_url:
                print(f"  No sample URL in result")
                return False
            
            # Download the image
            try:
                img_response = requests.get(sample_url)
                img_response.raise_for_status()
                
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, "wb") as f:
                    f.write(img_response.content)
                
                return True
            except Exception as e:
                print(f"  Error downloading image: {e}")
                return False
        
        elif status == "Failed":
            print(f"  Generation failed: {poll_result}")
            return False
        
        elif status in ["Pending", "Processing"]:
            time.sleep(5)
        
        else:
            print(f"  Unknown status: {status}")
            time.sleep(5)
    
    print(f"  Timeout waiting for generation")
    return False


def main():
    print("=" * 60)
    print("Flux 2 Pro Test - 5 Sample Images")
    print("=" * 60)
    print(f"Resolution: {WIDTH}x{HEIGHT}")
    print(f"Output: {OUTPUT_DIR.resolve()}")
    print()
    
    success_count = 0
    
    for i, test in enumerate(TEST_PROMPTS, 1):
        print(f"\n[{i}/5] Generating: {test['id']}")
        
        output_path = OUTPUT_DIR / f"{test['id']}.png"
        
        if output_path.exists():
            print(f"  Skipping (exists)")
            success_count += 1
            continue
        
        success = generate_image(test["prompt"], output_path)
        
        if success:
            print(f"  ✓ Saved: {output_path.name}")
            success_count += 1
        else:
            print(f"  ✗ Failed")
        
        # Small delay between requests
        if i < len(TEST_PROMPTS):
            time.sleep(2)
    
    print()
    print("=" * 60)
    print(f"Complete: {success_count}/5 images generated")
    print(f"Check: {OUTPUT_DIR.resolve()}")
    print("=" * 60)


if __name__ == "__main__":
    main()
