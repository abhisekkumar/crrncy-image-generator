import os
import re
import json
import time
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
from tqdm import tqdm
from google import genai
from google.genai import types


# =========================
# CONFIG
# =========================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError(
        "Missing GEMINI_API_KEY. Create a .env file and add GEMINI_API_KEY=your_key_here"
    )

client = genai.Client(api_key=API_KEY)

OUTPUT_DIR = Path("cb_images")

GENERATION_MODEL = "imagen-4.0-generate-001"
GENERATION_PROVIDER = "imagen"  # Use "gemini" or "imagen"

# Alternative models:
# GENERATION_MODEL = "gemini-2.0-flash-exp-image-generation"  # Gemini Flash
# GENERATION_MODEL = "gemini-3.1-flash-image-preview"  # Nano Banana 2

IMAGE_ASPECT_RATIO = "16:9"

MAX_IMAGES_PER_COMBINATION = 5
MAX_RETRIES = 2
SLEEP_BETWEEN_IMAGES = 2.0


# =========================
# VISUAL DNA & RULES
# =========================

GLOBAL_VISUAL_DNA = """
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
deep rich color palette,
pure landscape scenery only
"""

COMPOSITION_RULE = """
Cinematic wide landscape composition,
horizon placed in upper third of frame,
lower portion of image should be softer with atmospheric haze or gradient,
avoid busy cluttered details in lower third of frame,
balanced lighting across the scene,
soft depth of field in foreground,
clean open sky area in upper portion
"""

# =========================
# TIME OF DAY DEFINITIONS
# =========================

TIMES_OF_DAY = {
    "morning": {
        "lighting": "large visible sun rising on horizon, golden hour sunrise, dramatic sun rays bursting through",
        "palette": "deep purple and magenta sky at top fading to bright orange and gold at horizon, pink clouds catching sunlight",
        "mood": "peaceful awakening, new day energy, dramatic sunrise moment",
        "sun_position": "sun visible on or just above the horizon, sunrise moment captured",
    },
    "afternoon": {
        "lighting": "bright high sun, strong directional sunlight, clear bright day",
        "palette": "deep rich blue sky, bright white cumulus clouds, strong sunlight creating shadows",
        "mood": "energetic, productive, peak daylight, vibrant and alive",
        "sun_position": "sun high in sky, bright and visible, strong daylight",
    },
    "evening": {
        "lighting": "large setting sun at horizon, golden hour, warm orange light flooding scene",
        "palette": "intense orange and magenta sunset, deep purple clouds, fiery red and gold sky",
        "mood": "romantic, reflective, dramatic sunset moment, cinematic",
        "sun_position": "large sun setting at horizon, sunset moment with sun visible",
    },
    "night": {
        "lighting": "visible crescent or full moon, starry sky, warm glowing lights from buildings",
        "palette": "deep navy and purple sky, silver moonlight, warm yellow window glows contrasting with cool blue",
        "mood": "serene, dreamy, peaceful night, luxurious calm",
        "sun_position": "moon clearly visible in sky, stars visible, no sun",
    },
}

# =========================
# SEASONAL MODIFIERS
# =========================

SEASONS = {
    "spring": {
        "elements": "pink cherry blossoms in full bloom, fresh bright green leaves, colorful wildflowers, light morning dew",
        "atmosphere": "soft pink and lavender tones, fresh renewal energy, flowers everywhere visible",
        "sky": "soft pastel sky with gentle pink and blue hues",
    },
    "summer": {
        "elements": "lush deep green foliage, bright vibrant colors, clear visibility, intense sunlight",
        "atmosphere": "hot summer day feeling, deep blue skies, high contrast bright scene",
        "sky": "deep vivid blue sky with bright white clouds, strong visible sun",
    },
    "autumn": {
        "elements": "bright orange and red fall foliage, golden yellow leaves, trees with autumn colors",
        "atmosphere": "warm cozy amber tones, rich orange and burgundy everywhere, fall harvest mood",
        "sky": "warm golden and orange sky tones, softer diffused light",
    },
    "winter": {
        "elements": "snow covering everything, bare trees with snow, frost on surfaces, icy blue tones",
        "atmosphere": "cold crisp winter day, everything covered in white snow, cool blue shadows",
        "sky": "pale winter sky, cool blue and silver tones, soft diffused winter light",
    },
}

# =========================
# SCENE DEFINITIONS
# =========================

SCENES = {
    "morning_spring": [
        {"id": "cherry_blossom_japan", "prompt": "Japanese cherry blossom trees in full pink bloom along a river, Mount Fuji in background, soft sunrise glow, pink petals floating in air"},
        {"id": "tulip_fields", "prompt": "Colorful Dutch tulip fields stretching to horizon, rows of red yellow and pink tulips, windmill in distance, golden sunrise light"},
        {"id": "english_garden", "prompt": "Lush English countryside garden in spring bloom, roses and wildflowers, morning dew on petals, soft golden sunrise through mist"},
        {"id": "mountain_meadow", "prompt": "Alpine meadow covered in spring wildflowers, purple and yellow blooms, snow-capped peaks in background, sunrise rays"},
        {"id": "paris_spring", "prompt": "Paris Eiffel Tower with blooming spring trees, cherry blossoms in foreground, soft pink sunrise sky, romantic morning"},
    ],
    "morning_summer": [
        {"id": "bali_rice_terraces", "prompt": "Bali rice terraces at sunrise, lush green paddies, palm trees, golden sun rising through tropical mist, exotic paradise"},
        {"id": "greek_islands", "prompt": "Greek island whitewashed buildings at sunrise, deep blue Aegean sea, bright morning sun, Mediterranean summer vibes"},
        {"id": "hawaii_beach", "prompt": "Hawaiian beach at sunrise, palm trees silhouetted, turquoise water, golden sun rising over Pacific ocean, tropical paradise"},
        {"id": "swiss_alps_summer", "prompt": "Swiss Alps green summer meadows, cows grazing, wooden chalets, bright morning sun, clear blue sky beginning"},
        {"id": "california_coast", "prompt": "Big Sur California dramatic coastline at sunrise, rocky cliffs, crashing waves, golden sunlight on Pacific ocean"},
    ],
    "morning_autumn": [
        {"id": "vermont_fall", "prompt": "Vermont fall foliage at sunrise, brilliant red orange yellow maple trees, white church steeple, misty New England morning"},
        {"id": "kyoto_autumn", "prompt": "Kyoto Japan autumn temple with red maple leaves, traditional pagoda, golden morning light, zen garden atmosphere"},
        {"id": "bavarian_forest", "prompt": "German Bavarian forest in autumn colors, golden and red trees, morning fog between hills, fairytale castle in distance"},
        {"id": "scottish_highlands", "prompt": "Scottish Highlands in autumn, purple heather and golden bracken, misty mountains, dramatic sunrise breaking through clouds"},
        {"id": "colorado_aspens", "prompt": "Colorado aspen trees in golden fall color, white bark trunks, mountain backdrop, warm sunrise light filtering through leaves"},
    ],
    "morning_winter": [
        {"id": "swiss_village_snow", "prompt": "Swiss Alpine village covered in fresh snow at sunrise, wooden chalets with snow roofs, pink alpenglow on mountains"},
        {"id": "norwegian_fjord", "prompt": "Norwegian fjord in winter, snow-covered cliffs, calm icy water reflecting pink sunrise, Nordic winter wonderland"},
        {"id": "canadian_rockies", "prompt": "Canadian Rockies frozen lake at sunrise, snow-covered peaks, ice blue tones, golden sun touching mountain tops"},
        {"id": "finnish_lapland", "prompt": "Finnish Lapland snowy forest at sunrise, snow-laden pine trees, soft pink and blue winter sky, pristine white landscape"},
        {"id": "nyc_winter_morning", "prompt": "Central Park New York covered in fresh snow at sunrise, Manhattan skyline in background, frozen pond, winter magic"},
    ],
    "afternoon_spring": [
        {"id": "provence_lavender", "prompt": "Provence France lavender fields beginning to bloom, rolling purple hills, bright spring sun, rustic stone farmhouse"},
        {"id": "amsterdam_canals", "prompt": "Amsterdam canals lined with blooming trees, colorful houseboats, spring flowers, bright afternoon sunshine"},
        {"id": "cherry_blossom_dc", "prompt": "Washington DC cherry blossoms around Tidal Basin, Jefferson Memorial, bright blue spring sky, pink blossoms everywhere"},
        {"id": "new_zealand_spring", "prompt": "New Zealand countryside in spring, green rolling hills, sheep grazing, lupine flowers, dramatic clouds and sunshine"},
        {"id": "lake_como", "prompt": "Lake Como Italy in spring, blooming gardens, elegant villas, bright blue water, Alps in background, luxury European afternoon"},
    ],
    "afternoon_summer": [
        {"id": "santorini_blue", "prompt": "Santorini Greece blue domes and white buildings, deep blue Aegean sea, bright summer sun, iconic Mediterranean view"},
        {"id": "maldives_overwater", "prompt": "Maldives overwater bungalows, crystal clear turquoise lagoon, bright tropical sun, white sand visible through water"},
        {"id": "amalfi_coast", "prompt": "Amalfi Coast Italy colorful cliffside villages, deep blue Mediterranean, bright summer afternoon, luxury coastal scenery"},
        {"id": "monaco_harbor", "prompt": "Monaco harbor with luxury yachts, Monte Carlo buildings, bright Mediterranean sun, glamorous Riviera atmosphere"},
        {"id": "sydney_harbor", "prompt": "Sydney Opera House and Harbour Bridge, bright blue Australian summer day, sparkling harbor water, iconic skyline"},
    ],
    "afternoon_autumn": [
        {"id": "central_park_fall", "prompt": "New York Central Park autumn foliage, golden and red trees, Manhattan buildings behind, warm afternoon light"},
        {"id": "napa_valley", "prompt": "Napa Valley California vineyards in fall colors, golden grapevines, rolling hills, warm autumn afternoon sunshine"},
        {"id": "bruges_autumn", "prompt": "Bruges Belgium medieval town in autumn, golden trees along canals, historic buildings, warm afternoon glow"},
        {"id": "new_england_coast", "prompt": "New England coastal town in autumn, red and orange trees, lighthouse, dramatic autumn clouds, golden hour light"},
        {"id": "black_forest", "prompt": "German Black Forest in autumn colors, misty valleys, colorful trees, traditional houses, warm afternoon atmosphere"},
    ],
    "afternoon_winter": [
        {"id": "zermatt_matterhorn", "prompt": "Zermatt Switzerland with Matterhorn, snow-covered village, bright winter sun, crisp blue sky, Alpine winter paradise"},
        {"id": "stockholm_winter", "prompt": "Stockholm Sweden old town in winter, snow-covered rooftops, frozen harbor, bright winter afternoon, Nordic charm"},
        {"id": "lake_tahoe", "prompt": "Lake Tahoe winter scene, snow-covered pines, bright blue sky, sunlight sparkling on snow, mountain backdrop"},
        {"id": "prague_snow", "prompt": "Prague Czech Republic covered in snow, Charles Bridge, historic spires, bright winter afternoon, fairytale city"},
        {"id": "aspen_ski", "prompt": "Aspen Colorado ski resort, snow-covered slopes, bright sunshine, blue sky, luxury mountain town, winter sports paradise"},
    ],
    "evening_spring": [
        {"id": "paris_sunset", "prompt": "Paris Eiffel Tower at sunset in spring, blooming trees, pink and orange sky, Seine River reflections, romantic evening"},
        {"id": "kyoto_sunset", "prompt": "Kyoto bamboo forest at sunset in spring, golden light through tall bamboo, cherry blossoms nearby, zen atmosphere"},
        {"id": "florence_evening", "prompt": "Florence Italy at sunset, Duomo dome silhouette, spring flowers on rooftops, warm orange and pink sky, Renaissance beauty"},
        {"id": "vancouver_sunset", "prompt": "Vancouver skyline at sunset, cherry blossoms in foreground, mountains behind, spring evening colors, Pacific Northwest"},
        {"id": "amsterdam_sunset", "prompt": "Amsterdam canals at golden hour in spring, blooming trees reflected in water, warm sunset light on historic buildings"},
    ],
    "evening_summer": [
        {"id": "mykonos_sunset", "prompt": "Mykonos Greece iconic windmills at sunset, orange sun over Aegean sea, whitewashed buildings glowing, summer magic"},
        {"id": "la_sunset", "prompt": "Los Angeles skyline at sunset, palm trees silhouetted, dramatic orange and purple sky, Hollywood sign in distance"},
        {"id": "ibiza_beach", "prompt": "Ibiza beach club at sunset, large orange sun sinking into Mediterranean, silhouetted palms, summer party atmosphere"},
        {"id": "cape_town", "prompt": "Cape Town Table Mountain at sunset, dramatic orange sky, city lights beginning, South African summer evening"},
        {"id": "miami_beach", "prompt": "Miami South Beach at sunset, Art Deco buildings, palm trees, orange and pink sky, Ocean Drive vibes"},
    ],
    "evening_autumn": [
        {"id": "nyc_fall_sunset", "prompt": "New York City at sunset in autumn, golden fall trees in Central Park, orange sky behind skyscrapers, city lights emerging"},
        {"id": "edinburgh_sunset", "prompt": "Edinburgh Castle at sunset in autumn, dramatic Scottish sky, golden foliage, historic silhouette, moody atmosphere"},
        {"id": "tokyo_autumn", "prompt": "Tokyo skyline at sunset in autumn, fall colors in parks, Mt Fuji in distance, warm golden hour, modern meets traditional"},
        {"id": "boston_fall", "prompt": "Boston harbor at sunset in fall, autumn foliage, historic buildings, dramatic clouds, New England charm"},
        {"id": "munich_sunset", "prompt": "Munich Germany at sunset in autumn, Bavarian architecture, golden fall trees, warm evening light, beer garden atmosphere"},
    ],
    "evening_winter": [
        {"id": "nyc_winter_sunset", "prompt": "New York City winter sunset, snow in Central Park, golden light on buildings, pink and orange sky, cold but beautiful"},
        {"id": "vienna_christmas", "prompt": "Vienna Austria at sunset in winter, Christmas markets glowing, snow falling, historic buildings lit up, holiday magic"},
        {"id": "london_winter", "prompt": "London Big Ben and Thames at winter sunset, moody pink and purple sky, city lights reflecting on river"},
        {"id": "chicago_winter", "prompt": "Chicago skyline winter sunset, frozen Lake Michigan, dramatic orange sky, snow-covered parks, midwest winter beauty"},
        {"id": "tokyo_winter", "prompt": "Tokyo skyline at winter sunset, Mt Fuji snow-capped in distance, city lights emerging, crisp winter evening"},
    ],
    "night_spring": [
        {"id": "paris_night", "prompt": "Paris Eiffel Tower lit up at night in spring, blooming trees illuminated, crescent moon, romantic city of lights"},
        {"id": "tokyo_night_spring", "prompt": "Tokyo street at night with cherry blossoms, neon lights, spring evening, Japanese urban night scene"},
        {"id": "rome_night", "prompt": "Rome Colosseum illuminated at night in spring, full moon rising, historic atmosphere, warm street lights"},
        {"id": "dc_monuments", "prompt": "Washington DC monuments at night in spring, cherry blossoms lit up, reflecting pool, moonlight, patriotic beauty"},
        {"id": "barcelona_night", "prompt": "Barcelona Sagrada Familia illuminated at night in spring, Gaudi architecture glowing, stars above, magical atmosphere"},
    ],
    "night_summer": [
        {"id": "santorini_night", "prompt": "Santorini Greece at night in summer, warm lights from hillside buildings, full moon over Aegean, romantic Mediterranean night"},
        {"id": "nyc_summer_night", "prompt": "New York City Times Square area at night in summer, bright city lights, energy and excitement, urban summer night"},
        {"id": "bali_night", "prompt": "Bali temple at night, torches glowing, tropical stars above, palm trees silhouetted, exotic summer night"},
        {"id": "hawaii_night", "prompt": "Hawaii beach at night, palm trees under starry sky, Milky Way visible, warm tropical evening, paradise night"},
        {"id": "singapore_night", "prompt": "Singapore Marina Bay at night, Gardens by the Bay lit up, futuristic skyline, modern Asian metropolis"},
    ],
    "night_autumn": [
        {"id": "london_autumn_night", "prompt": "London Tower Bridge at night in autumn, warm city lights, fog rolling in, atmospheric autumn night"},
        {"id": "kyoto_night_fall", "prompt": "Kyoto temple illuminated at night with fall foliage, red maples lit up, lanterns glowing, autumn magic"},
        {"id": "boston_night", "prompt": "Boston skyline at night in autumn, fall colors still visible, harbor reflections, historic waterfront"},
        {"id": "amsterdam_night", "prompt": "Amsterdam canals at night in autumn, warm lights reflecting in water, foggy autumn atmosphere, cozy Dutch evening"},
        {"id": "seattle_night", "prompt": "Seattle Space Needle at night in autumn, city lights, Mt Rainier faintly visible, Pacific Northwest night"},
    ],
    "night_winter": [
        {"id": "northern_lights", "prompt": "Northern Lights aurora borealis over snowy landscape, green and purple dancing lights, stars visible, magical winter night"},
        {"id": "nyc_christmas", "prompt": "New York City Rockefeller Center Christmas tree lit up at night, skating rink, snow falling, holiday magic"},
        {"id": "vienna_night", "prompt": "Vienna opera house at night in winter, snow falling, warm golden lights, Christmas decorations, European winter elegance"},
        {"id": "tokyo_shibuya_winter", "prompt": "Tokyo Shibuya crossing at night in winter, neon lights reflecting on wet streets, bustling energy, Japanese winter night"},
        {"id": "swiss_village_night", "prompt": "Swiss Alpine village at night in winter, warm chalet windows glowing, snow-covered roofs, starry sky, cozy mountain night"},
    ],
}


# =========================
# HELPERS
# =========================

def safe_filename(text: str, max_len: int = 80) -> str:
    text = str(text).lower().strip()
    text = text.replace("&", "and")
    text = re.sub(r"[^\w\s\-]", "", text)
    text = re.sub(r"\s+", "_", text)
    text = re.sub(r"_+", "_", text)
    return text[:max_len].strip("_")


def build_prompt(scene: dict, time_of_day: str, season: str) -> str:
    time_info = TIMES_OF_DAY[time_of_day]
    season_info = SEASONS[season]

    prompt = f"""
{GLOBAL_VISUAL_DNA}

{COMPOSITION_RULE}

SCENE DESCRIPTION:
{scene['prompt']}

TIME OF DAY - {time_of_day.upper()}:
Lighting style: {time_info['lighting']}
Sun or Moon position: {time_info['sun_position']}
Sky and color palette: {time_info['palette']}

SEASON - {season.upper()}:
Seasonal characteristics: {season_info['elements']}
Overall atmosphere: {season_info['atmosphere']}
Sky style: {season_info['sky']}

CRITICAL REQUIREMENTS:
- Photorealistic cinematic landscape photography
- 4K UHD resolution with rich detail
- Professional color grading like high-end film
- Rich saturated colors, NOT faint or washed out
- Deep blacks and vibrant highlights
- Strong contrast and dynamic range
- Sun or moon MUST be clearly visible in the sky as specified
- Seasonal elements MUST be prominently visible (snow in winter, fall colors in autumn, flowers in spring, etc.)
- Each season must look distinctly different
- NOT generic AI wallpaper look
- NOT flat or desaturated
- Premium editorial travel photography aesthetic
- Clean, uncluttered scenery

ABSOLUTELY FORBIDDEN:
- No text, words, letters, numbers, or writing of any kind
- No timestamps, dates, clocks, or time displays
- No watermarks, signatures, or logos
- No titles, captions, labels, or annotations
- No phone screens, app interfaces, cards, buttons, or digital elements
- No rectangles, frames, borders, or geometric overlays
- Pure natural landscape scenery only
"""
    return prompt


def generate_image_gemini(prompt: str, output_path: Path) -> bool:
    try:
        response = client.models.generate_content(
            model=GENERATION_MODEL,
            contents=[prompt],
            config=types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"],
                image_config=types.ImageConfig(
                    aspect_ratio=IMAGE_ASPECT_RATIO,
                ),
            ),
        )

        if not response.candidates:
            print(f"\n  No candidates returned")
            return False

        output_path.parent.mkdir(parents=True, exist_ok=True)

        for part in response.candidates[0].content.parts:
            inline_data = getattr(part, "inline_data", None)

            if inline_data and inline_data.data:
                with open(output_path, "wb") as f:
                    f.write(inline_data.data)
                return True

        print(f"\n  No image data in response")
        return False

    except Exception as e:
        print(f"\n  Generation error: {e}")
        return False


def generate_image_imagen(prompt: str, output_path: Path) -> bool:
    try:
        response = client.models.generate_images(
            model=GENERATION_MODEL,
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio=IMAGE_ASPECT_RATIO,
            ),
        )

        if not response.generated_images:
            print(f"\n  No images generated")
            return False

        image_bytes = response.generated_images[0].image.image_bytes

        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "wb") as f:
            f.write(image_bytes)

        return True

    except Exception as e:
        print(f"\n  Generation error: {e}")
        return False


def generate_image(prompt: str, output_path: Path) -> bool:
    if GENERATION_PROVIDER == "imagen":
        return generate_image_imagen(prompt, output_path)
    else:
        return generate_image_gemini(prompt, output_path)


# =========================
# MAIN
# =========================

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    report = []
    total_generated = 0
    total_failed = 0

    print("=" * 60)
    print("CRRNCY Dashboard Background Generator")
    print("=" * 60)
    print(f"\nProvider: {GENERATION_PROVIDER}")
    print(f"Model: {GENERATION_MODEL}")
    print(f"Aspect Ratio: {IMAGE_ASPECT_RATIO}")
    print(f"Output Directory: {OUTPUT_DIR.resolve()}")
    print(f"Max per combination: {MAX_IMAGES_PER_COMBINATION}")
    print()

    all_combinations = []
    for key, scenes in SCENES.items():
        parts = key.split("_", 1)
        time_of_day = parts[0]
        season = parts[1]
        for scene in scenes[:MAX_IMAGES_PER_COMBINATION]:
            all_combinations.append((time_of_day, season, scene))

    print(f"Total images to generate: {len(all_combinations)}")
    print("=" * 60)
    print()

    for time_of_day, season, scene in tqdm(all_combinations, desc="Generating"):
        scene_id = scene["id"]
        filename = f"{time_of_day}_{season}_{scene_id}.png"
        output_path = OUTPUT_DIR / time_of_day / filename

        if output_path.exists():
            tqdm.write(f"  Skipping (exists): {filename}")
            report.append({
                "time": time_of_day,
                "season": season,
                "scene": scene["id"],
                "filename": filename,
                "status": "skipped_existing",
            })
            continue

        prompt = build_prompt(scene, time_of_day, season)

        success = False
        for attempt in range(1, MAX_RETRIES + 1):
            success = generate_image(prompt, output_path)
            if success:
                break
            if attempt < MAX_RETRIES:
                tqdm.write(f"  Retry {attempt + 1}/{MAX_RETRIES} for {filename}")
                time.sleep(SLEEP_BETWEEN_IMAGES)

        if success:
            total_generated += 1
            report.append({
                "time": time_of_day,
                "season": season,
                "scene": scene["id"],
                "filename": filename,
                "status": "generated",
            })
            tqdm.write(f"  Generated: {filename}")
        else:
            total_failed += 1
            report.append({
                "time": time_of_day,
                "season": season,
                "scene": scene["id"],
                "filename": filename,
                "status": "failed",
            })
            tqdm.write(f"  FAILED: {filename}")

        time.sleep(SLEEP_BETWEEN_IMAGES)

    report_path = OUTPUT_DIR / "generation_report.json"
    with open(report_path, "w") as f:
        json.dump({
            "generated_at": datetime.now().isoformat(),
            "model": GENERATION_MODEL,
            "total_generated": total_generated,
            "total_failed": total_failed,
            "total_skipped": len(all_combinations) - total_generated - total_failed,
            "images": report,
        }, f, indent=2)

    print()
    print("=" * 60)
    print("GENERATION COMPLETE")
    print("=" * 60)
    print(f"Generated: {total_generated}")
    print(f"Failed: {total_failed}")
    print(f"Skipped: {len(all_combinations) - total_generated - total_failed}")
    print(f"\nOutput: {OUTPUT_DIR.resolve()}")
    print(f"Report: {report_path.resolve()}")


if __name__ == "__main__":
    main()
