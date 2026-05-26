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

MAX_IMAGES_PER_COMBINATION = 10  # Clear weather has 10, rain/cloudy have 2
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
# WEATHER MODIFIERS
# =========================

WEATHER_MODIFIERS = {
    "rain": {
        "atmosphere": "rain falling, wet surfaces reflecting lights, puddles on ground, moody atmospheric weather",
        "lighting": "diffused light through rain clouds, reflections on wet surfaces, dramatic rain atmosphere",
        "elements": "raindrops visible, wet textures, glistening surfaces, umbrellas optional",
    },
    "cloudy": {
        "atmosphere": "dramatic overcast sky, moody cloud formations, diffused soft lighting, atmospheric depth",
        "lighting": "soft diffused light through clouds, no harsh shadows, even illumination, dramatic sky",
        "elements": "dramatic cloud formations, varying grey tones in sky, moody atmospheric feel",
    },
}

# =========================
# SCENE DEFINITIONS
# =========================

SCENES = {
    # ==================== CLEAR WEATHER (Original + 5 more each) ====================
    "morning_spring": [
        {"id": "cherry_blossom_japan", "prompt": "Japanese cherry blossom trees in full pink bloom along a river, Mount Fuji in background, soft sunrise glow, pink petals floating in air"},
        {"id": "tulip_fields", "prompt": "Colorful Dutch tulip fields stretching to horizon, rows of red yellow and pink tulips, windmill in distance, golden sunrise light"},
        {"id": "english_garden", "prompt": "Lush English countryside garden in spring bloom, roses and wildflowers, morning dew on petals, soft golden sunrise through mist"},
        {"id": "mountain_meadow", "prompt": "Alpine meadow covered in spring wildflowers, purple and yellow blooms, snow-capped peaks in background, sunrise rays"},
        {"id": "paris_spring", "prompt": "Paris Eiffel Tower with blooming spring trees, cherry blossoms in foreground, soft pink sunrise sky, romantic morning"},
        {"id": "korean_temple", "prompt": "Korean Buddhist temple surrounded by pink cherry blossoms at sunrise, traditional architecture, misty mountains behind, peaceful morning"},
        {"id": "tuscany_spring", "prompt": "Tuscan countryside at sunrise in spring, rolling green hills, cypress trees, blooming poppies, golden morning light"},
        {"id": "vancouver_spring", "prompt": "Vancouver Stanley Park at sunrise, cherry blossoms in bloom, mountains and ocean visible, spring morning mist"},
        {"id": "austrian_alps", "prompt": "Austrian Alpine village in spring, flower boxes on chalets, green meadows, snow peaks catching sunrise light"},
        {"id": "spanish_countryside", "prompt": "Spanish olive groves at sunrise in spring, wildflowers blooming, golden light across hills, Mediterranean morning"},
    ],
    "morning_summer": [
        {"id": "bali_rice_terraces", "prompt": "Bali rice terraces at sunrise, lush green paddies, palm trees, golden sun rising through tropical mist, exotic paradise"},
        {"id": "greek_islands", "prompt": "Greek island whitewashed buildings at sunrise, deep blue Aegean sea, bright morning sun, Mediterranean summer vibes"},
        {"id": "hawaii_beach", "prompt": "Hawaiian beach at sunrise, palm trees silhouetted, turquoise water, golden sun rising over Pacific ocean, tropical paradise"},
        {"id": "swiss_alps_summer", "prompt": "Swiss Alps green summer meadows, cows grazing, wooden chalets, bright morning sun, clear blue sky beginning"},
        {"id": "california_coast", "prompt": "Big Sur California dramatic coastline at sunrise, rocky cliffs, crashing waves, golden sunlight on Pacific ocean"},
        {"id": "maldives_sunrise", "prompt": "Maldives overwater villa at sunrise, crystal turquoise water, golden sun rising, tropical paradise morning"},
        {"id": "croatia_coast", "prompt": "Croatian Dalmatian coast at sunrise, clear Adriatic sea, ancient coastal town, summer morning light"},
        {"id": "thailand_islands", "prompt": "Thai limestone islands at sunrise, emerald water, longtail boats, tropical summer morning, exotic paradise"},
        {"id": "sardinia_beach", "prompt": "Sardinia Italy pink sand beach at sunrise, crystal clear Mediterranean, rocky coastline, summer morning glow"},
        {"id": "fiji_lagoon", "prompt": "Fiji tropical lagoon at sunrise, palm trees, turquoise water, golden sun rays, South Pacific paradise morning"},
    ],
    "morning_autumn": [
        {"id": "vermont_fall", "prompt": "Vermont fall foliage at sunrise, brilliant red orange yellow maple trees, white church steeple, misty New England morning"},
        {"id": "kyoto_autumn", "prompt": "Kyoto Japan autumn temple with red maple leaves, traditional pagoda, golden morning light, zen garden atmosphere"},
        {"id": "bavarian_forest", "prompt": "German Bavarian forest in autumn colors, golden and red trees, morning fog between hills, fairytale castle in distance"},
        {"id": "scottish_highlands", "prompt": "Scottish Highlands in autumn, purple heather and golden bracken, misty mountains, dramatic sunrise breaking through clouds"},
        {"id": "colorado_aspens", "prompt": "Colorado aspen trees in golden fall color, white bark trunks, mountain backdrop, warm sunrise light filtering through leaves"},
        {"id": "quebec_fall", "prompt": "Quebec Canada countryside in fall, brilliant maple colors, traditional farmhouse, morning mist over fields"},
        {"id": "alps_autumn", "prompt": "Swiss Alps in autumn colors, golden larch trees, mountain lakes reflecting fall foliage, crisp morning sunrise"},
        {"id": "oregon_forest", "prompt": "Oregon Columbia River Gorge in fall, waterfalls through autumn forest, golden morning light, misty atmosphere"},
        {"id": "new_hampshire", "prompt": "New Hampshire White Mountains fall foliage, covered bridge, brilliant autumn colors, sunrise through morning fog"},
        {"id": "michigan_autumn", "prompt": "Michigan Upper Peninsula fall colors, Lake Superior shoreline, golden and red trees, peaceful autumn sunrise"},
    ],
    "morning_winter": [
        {"id": "swiss_village_snow", "prompt": "Swiss Alpine village covered in fresh snow at sunrise, wooden chalets with snow roofs, pink alpenglow on mountains"},
        {"id": "norwegian_fjord", "prompt": "Norwegian fjord in winter, snow-covered cliffs, calm icy water reflecting pink sunrise, Nordic winter wonderland"},
        {"id": "canadian_rockies", "prompt": "Canadian Rockies frozen lake at sunrise, snow-covered peaks, ice blue tones, golden sun touching mountain tops"},
        {"id": "finnish_lapland", "prompt": "Finnish Lapland snowy forest at sunrise, snow-laden pine trees, soft pink and blue winter sky, pristine white landscape"},
        {"id": "nyc_winter_morning", "prompt": "Central Park New York covered in fresh snow at sunrise, Manhattan skyline in background, frozen pond, winter magic"},
        {"id": "iceland_winter", "prompt": "Iceland snowy landscape at sunrise, frozen waterfalls, pink and purple winter sky, dramatic volcanic mountains"},
        {"id": "hokkaido_snow", "prompt": "Hokkaido Japan winter morning, snow-covered fields, traditional farmhouses, pink sunrise over snowy mountains"},
        {"id": "patagonia_winter", "prompt": "Patagonia mountains in winter at sunrise, snow-covered peaks, frozen lakes, dramatic winter morning light"},
        {"id": "scottish_winter", "prompt": "Scottish Highlands covered in snow at sunrise, frozen lochs, snow-dusted mountains, winter morning mist"},
        {"id": "minnesota_winter", "prompt": "Minnesota frozen lake at sunrise, snow-covered pine forest, pink and gold winter sky, pristine wilderness"},
    ],
    "afternoon_spring": [
        {"id": "provence_lavender", "prompt": "Provence France lavender fields beginning to bloom, rolling purple hills, bright spring sun, rustic stone farmhouse"},
        {"id": "amsterdam_canals", "prompt": "Amsterdam canals lined with blooming trees, colorful houseboats, spring flowers, bright afternoon sunshine"},
        {"id": "cherry_blossom_dc", "prompt": "Washington DC cherry blossoms around Tidal Basin, Jefferson Memorial, bright blue spring sky, pink blossoms everywhere"},
        {"id": "new_zealand_spring", "prompt": "New Zealand countryside in spring, green rolling hills, sheep grazing, lupine flowers, dramatic clouds and sunshine"},
        {"id": "lake_como", "prompt": "Lake Como Italy in spring, blooming gardens, elegant villas, bright blue water, Alps in background, luxury European afternoon"},
        {"id": "cotswolds_spring", "prompt": "English Cotswolds village in spring, honey-colored stone cottages, blooming gardens, bright afternoon sunshine"},
        {"id": "keukenhof_gardens", "prompt": "Keukenhof Gardens Netherlands, millions of tulips in bloom, bright spring colors, afternoon sunshine"},
        {"id": "japanese_garden", "prompt": "Traditional Japanese garden in spring, koi pond, cherry blossoms, bright afternoon light, zen tranquility"},
        {"id": "swiss_spring", "prompt": "Swiss mountain meadow in spring, wildflowers blooming, snow-capped Alps, bright afternoon sun, green valleys"},
        {"id": "italian_lakes", "prompt": "Italian Lake Maggiore in spring, blooming azaleas, elegant villas, bright blue water, afternoon sunshine"},
    ],
    "afternoon_summer": [
        {"id": "santorini_blue", "prompt": "Santorini Greece blue domes and white buildings, deep blue Aegean sea, bright summer sun, iconic Mediterranean view"},
        {"id": "maldives_overwater", "prompt": "Maldives overwater bungalows, crystal clear turquoise lagoon, bright tropical sun, white sand visible through water"},
        {"id": "amalfi_coast", "prompt": "Amalfi Coast Italy colorful cliffside villages, deep blue Mediterranean, bright summer afternoon, luxury coastal scenery"},
        {"id": "monaco_harbor", "prompt": "Monaco harbor with luxury yachts, Monte Carlo buildings, bright Mediterranean sun, glamorous Riviera atmosphere"},
        {"id": "sydney_harbor", "prompt": "Sydney Opera House and Harbour Bridge, bright blue Australian summer day, sparkling harbor water, iconic skyline"},
        {"id": "cinque_terre", "prompt": "Cinque Terre Italy colorful villages on cliffs, deep blue Ligurian sea, bright summer afternoon, Italian Riviera"},
        {"id": "bora_bora", "prompt": "Bora Bora lagoon with Mount Otemanu, crystal clear water, overwater bungalows, bright tropical afternoon"},
        {"id": "dubrovnik", "prompt": "Dubrovnik Croatia old town walls, deep blue Adriatic, bright summer afternoon, historic Mediterranean beauty"},
        {"id": "capri_island", "prompt": "Capri Italy Faraglioni rocks, deep blue Mediterranean, luxury yachts, bright summer sunshine"},
        {"id": "seychelles", "prompt": "Seychelles granite boulders on pristine beach, turquoise water, palm trees, bright tropical afternoon"},
    ],
    "afternoon_autumn": [
        {"id": "central_park_fall", "prompt": "New York Central Park autumn foliage, golden and red trees, Manhattan buildings behind, warm afternoon light"},
        {"id": "napa_valley", "prompt": "Napa Valley California vineyards in fall colors, golden grapevines, rolling hills, warm autumn afternoon sunshine"},
        {"id": "bruges_autumn", "prompt": "Bruges Belgium medieval town in autumn, golden trees along canals, historic buildings, warm afternoon glow"},
        {"id": "new_england_coast", "prompt": "New England coastal town in autumn, red and orange trees, lighthouse, dramatic autumn clouds, golden hour light"},
        {"id": "black_forest", "prompt": "German Black Forest in autumn colors, misty valleys, colorful trees, traditional houses, warm afternoon atmosphere"},
        {"id": "lake_bled_fall", "prompt": "Lake Bled Slovenia in autumn, island church, golden trees reflecting in water, warm afternoon light"},
        {"id": "rhine_valley", "prompt": "Rhine Valley Germany castles in autumn, vineyards in fall colors, river winding through, warm afternoon"},
        {"id": "maine_coast", "prompt": "Maine rocky coastline in autumn, lighthouses, brilliant fall foliage meeting ocean, golden afternoon light"},
        {"id": "virginia_fall", "prompt": "Virginia Shenandoah Valley fall colors, Blue Ridge Mountains, golden afternoon light, rolling autumn hills"},
        {"id": "lombardy_autumn", "prompt": "Lombardy Italy countryside in autumn, golden vineyards, cypress trees, warm afternoon glow"},
    ],
    "afternoon_winter": [
        {"id": "zermatt_matterhorn", "prompt": "Zermatt Switzerland with Matterhorn, snow-covered village, bright winter sun, crisp blue sky, Alpine winter paradise"},
        {"id": "stockholm_winter", "prompt": "Stockholm Sweden old town in winter, snow-covered rooftops, frozen harbor, bright winter afternoon, Nordic charm"},
        {"id": "lake_tahoe", "prompt": "Lake Tahoe winter scene, snow-covered pines, bright blue sky, sunlight sparkling on snow, mountain backdrop"},
        {"id": "prague_snow", "prompt": "Prague Czech Republic covered in snow, Charles Bridge, historic spires, bright winter afternoon, fairytale city"},
        {"id": "aspen_ski", "prompt": "Aspen Colorado ski resort, snow-covered slopes, bright sunshine, blue sky, luxury mountain town, winter sports paradise"},
        {"id": "hallstatt_winter", "prompt": "Hallstatt Austria covered in snow, lake reflections, Alpine village, bright winter afternoon, fairytale scene"},
        {"id": "quebec_city_winter", "prompt": "Quebec City Chateau Frontenac in snow, frozen St Lawrence, bright winter sun, French Canadian charm"},
        {"id": "innsbruck_winter", "prompt": "Innsbruck Austria snow-covered old town, Alps towering behind, bright winter afternoon, Tyrolean beauty"},
        {"id": "st_moritz", "prompt": "St Moritz Switzerland frozen lake, luxury resort, bright winter sunshine, crisp Alpine air"},
        {"id": "banff_winter", "prompt": "Banff Canada snow-covered town, Rocky Mountains, frozen Bow River, bright winter afternoon light"},
    ],
    "evening_spring": [
        {"id": "paris_sunset", "prompt": "Paris Eiffel Tower at sunset in spring, blooming trees, pink and orange sky, Seine River reflections, romantic evening"},
        {"id": "kyoto_sunset", "prompt": "Kyoto bamboo forest at sunset in spring, golden light through tall bamboo, cherry blossoms nearby, zen atmosphere"},
        {"id": "florence_evening", "prompt": "Florence Italy at sunset, Duomo dome silhouette, spring flowers on rooftops, warm orange and pink sky, Renaissance beauty"},
        {"id": "vancouver_sunset", "prompt": "Vancouver skyline at sunset, cherry blossoms in foreground, mountains behind, spring evening colors, Pacific Northwest"},
        {"id": "amsterdam_sunset", "prompt": "Amsterdam canals at golden hour in spring, blooming trees reflected in water, warm sunset light on historic buildings"},
        {"id": "lisbon_sunset", "prompt": "Lisbon Portugal at sunset in spring, colorful buildings, Tagus River golden light, blooming jacaranda trees"},
        {"id": "budapest_evening", "prompt": "Budapest Hungary at sunset, Parliament building golden light, Danube River reflections, spring evening"},
        {"id": "san_francisco_spring", "prompt": "San Francisco Golden Gate at sunset, spring wildflowers, orange and pink sky, iconic bridge silhouette"},
        {"id": "seville_sunset", "prompt": "Seville Spain at sunset, Plaza de Espana, orange trees in bloom, warm golden evening light"},
        {"id": "porto_evening", "prompt": "Porto Portugal Douro River at sunset, colorful Ribeira district, wine boats, spring evening glow"},
    ],
    "evening_summer": [
        {"id": "mykonos_sunset", "prompt": "Mykonos Greece iconic windmills at sunset, orange sun over Aegean sea, whitewashed buildings glowing, summer magic"},
        {"id": "la_sunset", "prompt": "Los Angeles skyline at sunset, palm trees silhouetted, dramatic orange and purple sky, Hollywood sign in distance"},
        {"id": "ibiza_beach", "prompt": "Ibiza beach club at sunset, large orange sun sinking into Mediterranean, silhouetted palms, summer party atmosphere"},
        {"id": "cape_town", "prompt": "Cape Town Table Mountain at sunset, dramatic orange sky, city lights beginning, South African summer evening"},
        {"id": "miami_beach", "prompt": "Miami South Beach at sunset, Art Deco buildings, palm trees, orange and pink sky, Ocean Drive vibes"},
        {"id": "positano_sunset", "prompt": "Positano Italy at sunset, colorful buildings cascading down cliff, orange Mediterranean sky, summer evening"},
        {"id": "bali_sunset", "prompt": "Bali Uluwatu temple at sunset, dramatic clifftop silhouette, orange sun sinking into Indian Ocean"},
        {"id": "malibu_sunset", "prompt": "Malibu California beach at sunset, surfers, dramatic orange and purple sky, Pacific coast summer evening"},
        {"id": "rio_sunset", "prompt": "Rio de Janeiro at sunset, Sugarloaf Mountain silhouette, orange sky over Guanabara Bay, tropical evening"},
        {"id": "barcelona_sunset", "prompt": "Barcelona beach at sunset, W Hotel silhouette, Mediterranean golden hour, summer evening vibes"},
    ],
    "evening_autumn": [
        {"id": "nyc_fall_sunset", "prompt": "New York City at sunset in autumn, golden fall trees in Central Park, orange sky behind skyscrapers, city lights emerging"},
        {"id": "edinburgh_sunset", "prompt": "Edinburgh Castle at sunset in autumn, dramatic Scottish sky, golden foliage, historic silhouette, moody atmosphere"},
        {"id": "tokyo_autumn", "prompt": "Tokyo skyline at sunset in autumn, fall colors in parks, Mt Fuji in distance, warm golden hour, modern meets traditional"},
        {"id": "boston_fall", "prompt": "Boston harbor at sunset in fall, autumn foliage, historic buildings, dramatic clouds, New England charm"},
        {"id": "munich_sunset", "prompt": "Munich Germany at sunset in autumn, Bavarian architecture, golden fall trees, warm evening light, beer garden atmosphere"},
        {"id": "prague_autumn", "prompt": "Prague at sunset in autumn, golden fall trees along Vltava, castle silhouette, warm evening light"},
        {"id": "seattle_fall", "prompt": "Seattle skyline at sunset in fall, Mt Rainier visible, fall colors, golden evening light, Pacific Northwest autumn"},
        {"id": "toronto_autumn", "prompt": "Toronto skyline at sunset in autumn, CN Tower, fall colors in parks, golden hour light over Lake Ontario"},
        {"id": "portland_fall", "prompt": "Portland Oregon at sunset in fall, Mt Hood visible, autumn colors, golden evening light, Pacific Northwest charm"},
        {"id": "stockholm_autumn", "prompt": "Stockholm at sunset in autumn, golden trees, water reflections, historic buildings glowing, Nordic fall evening"},
    ],
    "evening_winter": [
        {"id": "nyc_winter_sunset", "prompt": "New York City winter sunset, snow in Central Park, golden light on buildings, pink and orange sky, cold but beautiful"},
        {"id": "vienna_christmas", "prompt": "Vienna Austria at sunset in winter, markets glowing, snow falling, historic buildings lit up, holiday magic"},
        {"id": "london_winter", "prompt": "London Big Ben and Thames at winter sunset, moody pink and purple sky, city lights reflecting on river"},
        {"id": "chicago_winter", "prompt": "Chicago skyline winter sunset, frozen Lake Michigan, dramatic orange sky, snow-covered parks, midwest winter beauty"},
        {"id": "tokyo_winter", "prompt": "Tokyo skyline at winter sunset, Mt Fuji snow-capped in distance, city lights emerging, crisp winter evening"},
        {"id": "moscow_winter", "prompt": "Moscow Red Square at winter sunset, St Basil's colorful domes, snow falling, golden evening light"},
        {"id": "copenhagen_winter", "prompt": "Copenhagen Nyhavn at winter sunset, colorful buildings, snow on rooftops, warm lights glowing, hygge atmosphere"},
        {"id": "edinburgh_winter", "prompt": "Edinburgh at winter sunset, castle on rock, snow dusted rooftops, dramatic Scottish winter sky"},
        {"id": "reykjavik_winter", "prompt": "Reykjavik Iceland at winter sunset, colorful rooftops, snow covered, dramatic pink and purple Arctic sky"},
        {"id": "salzburg_winter", "prompt": "Salzburg Austria at winter sunset, fortress on hill, snow-covered old town, golden evening light"},
    ],
    "night_spring": [
        {"id": "paris_night", "prompt": "Paris Eiffel Tower lit up at night in spring, blooming trees illuminated, crescent moon, romantic city of lights"},
        {"id": "tokyo_night_spring", "prompt": "Tokyo street at night with cherry blossoms, neon lights, spring evening, Japanese urban night scene"},
        {"id": "rome_night", "prompt": "Rome Colosseum illuminated at night in spring, full moon rising, historic atmosphere, warm street lights"},
        {"id": "dc_monuments", "prompt": "Washington DC monuments at night in spring, cherry blossoms lit up, reflecting pool, moonlight, patriotic beauty"},
        {"id": "barcelona_night", "prompt": "Barcelona Sagrada Familia illuminated at night in spring, architecture glowing, stars above, magical atmosphere"},
        {"id": "sydney_night_spring", "prompt": "Sydney Opera House lit up at night in spring, harbor reflections, full moon, iconic Australian night"},
        {"id": "shanghai_night", "prompt": "Shanghai Pudong skyline at night in spring, Oriental Pearl Tower, city lights reflecting in Huangpu River"},
        {"id": "dubai_night_spring", "prompt": "Dubai Burj Khalifa at night in spring, city lights, crescent moon, modern Arabian night"},
        {"id": "london_night_spring", "prompt": "London Tower Bridge lit up at night in spring, Thames reflections, full moon rising, historic charm"},
        {"id": "hong_kong_night", "prompt": "Hong Kong Victoria Harbour at night, city skyline lit up, light show reflections, spring night"},
    ],
    "night_summer": [
        {"id": "santorini_night", "prompt": "Santorini Greece at night in summer, warm lights from hillside buildings, full moon over Aegean, romantic Mediterranean night"},
        {"id": "nyc_summer_night", "prompt": "New York City Times Square area at night in summer, bright city lights, energy and excitement, urban summer night"},
        {"id": "bali_night", "prompt": "Bali rice terraces at night, lanterns glowing, tropical stars above, palm trees silhouetted, exotic summer night"},
        {"id": "hawaii_night", "prompt": "Hawaii beach at night, palm trees under starry sky, Milky Way visible, warm tropical evening, paradise night"},
        {"id": "singapore_night", "prompt": "Singapore Marina Bay at night, Gardens by the Bay lit up, futuristic skyline, modern Asian metropolis"},
        {"id": "vegas_night", "prompt": "Las Vegas strip at night, neon lights, fountains, summer night energy, entertainment capital"},
        {"id": "cancun_night", "prompt": "Cancun Mexico hotel zone at night, Caribbean waters, resort lights, tropical summer night"},
        {"id": "monaco_night", "prompt": "Monaco Monte Carlo at night, casino lights, luxury yachts, Mediterranean summer night glamour"},
        {"id": "athens_night", "prompt": "Athens Acropolis lit up at night in summer, ancient ruins glowing, city lights below, Greek summer night"},
        {"id": "marrakech_night", "prompt": "Marrakech Jemaa el-Fnaa square at night, lanterns, bustling atmosphere, exotic Moroccan summer night"},
    ],
    "night_autumn": [
        {"id": "london_autumn_night", "prompt": "London Tower Bridge at night in autumn, warm city lights, fog rolling in, atmospheric autumn night"},
        {"id": "kyoto_night_fall", "prompt": "Kyoto temple illuminated at night with fall foliage, red maples lit up, lanterns glowing, autumn magic"},
        {"id": "boston_night", "prompt": "Boston skyline at night in autumn, fall colors still visible, harbor reflections, historic waterfront"},
        {"id": "amsterdam_night", "prompt": "Amsterdam canals at night in autumn, warm lights reflecting in water, foggy autumn atmosphere, cozy Dutch evening"},
        {"id": "seattle_night", "prompt": "Seattle Space Needle at night in autumn, city lights, Mt Rainier faintly visible, Pacific Northwest night"},
        {"id": "bruges_night", "prompt": "Bruges Belgium at night in autumn, medieval buildings lit up, canal reflections, atmospheric fall night"},
        {"id": "vancouver_night_fall", "prompt": "Vancouver at night in autumn, city lights, mountains silhouette, fall atmosphere, Canadian night"},
        {"id": "munich_night", "prompt": "Munich at night in autumn, Marienplatz lit up, fall atmosphere, warm Bavarian night"},
        {"id": "dublin_night", "prompt": "Dublin Temple Bar at night in autumn, warm pub lights, cobblestone streets, Irish autumn night"},
        {"id": "vienna_autumn_night", "prompt": "Vienna at night in autumn, opera house lit up, fall trees, elegant Austrian night"},
    ],
    "night_winter": [
        {"id": "northern_lights", "prompt": "Northern Lights aurora borealis over snowy landscape, green and purple dancing lights, stars visible, magical winter night"},
        {"id": "nyc_christmas", "prompt": "New York City Rockefeller tree lit up at night, skating rink, snow falling, holiday magic"},
        {"id": "vienna_night", "prompt": "Vienna opera house at night in winter, snow falling, warm golden lights, decorations, European winter elegance"},
        {"id": "tokyo_shibuya_winter", "prompt": "Tokyo Shibuya crossing at night in winter, neon lights reflecting on wet streets, bustling energy, Japanese winter night"},
        {"id": "swiss_village_night", "prompt": "Swiss Alpine village at night in winter, warm chalet windows glowing, snow-covered roofs, starry sky, cozy mountain night"},
        {"id": "prague_night_winter", "prompt": "Prague old town at night in winter, snow falling, warm lights, historic atmosphere, fairytale winter night"},
        {"id": "london_winter_night", "prompt": "London at night in winter, Big Ben and Parliament lit up, snow falling, holiday decorations"},
        {"id": "montreal_winter_night", "prompt": "Montreal old town at night in winter, snow covered, warm lights, French Canadian winter charm"},
        {"id": "stockholm_winter_night", "prompt": "Stockholm Gamla Stan at night in winter, snow-covered medieval streets, warm lights, Nordic winter night"},
        {"id": "munich_winter_night", "prompt": "Munich market at night in winter, decorated stalls, snow falling, warm glowing lights, German winter magic"},
    ],

    # ==================== RAINY WEATHER (2 images each) ====================
    "morning_spring_rain": [
        {"id": "tokyo_rain_spring", "prompt": "Tokyo streets in spring rain at dawn, cherry blossom petals in puddles, neon reflections on wet pavement, moody atmospheric morning"},
        {"id": "paris_rain_morning", "prompt": "Paris rainy spring morning, wet cobblestones, Eiffel Tower through rain, blooming trees with raindrops, romantic moody atmosphere"},
    ],
    "morning_summer_rain": [
        {"id": "bali_monsoon", "prompt": "Bali rice terraces during monsoon rain at sunrise, dramatic rain clouds, lush green paddies, tropical storm atmosphere"},
        {"id": "hawaii_rain_morning", "prompt": "Hawaiian rainforest at rainy morning, tropical downpour, lush green, misty mountains, rainbow forming"},
    ],
    "morning_autumn_rain": [
        {"id": "london_rain_fall", "prompt": "London rainy autumn morning, Big Ben through rain, wet fallen leaves on pavement, moody atmospheric British weather"},
        {"id": "portland_rain_autumn", "prompt": "Portland Oregon rainy fall morning, colorful leaves in puddles, misty atmosphere, Pacific Northwest autumn rain"},
    ],
    "morning_winter_rain": [
        {"id": "seattle_winter_rain", "prompt": "Seattle rainy winter morning, Pike Place Market, wet streets, Space Needle through drizzle, moody Pacific Northwest"},
        {"id": "vancouver_winter_rain", "prompt": "Vancouver rainy winter morning, mountains hidden in clouds, wet city streets, moody atmospheric Pacific coast"},
    ],
    "afternoon_spring_rain": [
        {"id": "amsterdam_rain_spring", "prompt": "Amsterdam canals during spring rain, raindrops on water, blooming trees, cyclists with umbrellas, Dutch rainy afternoon"},
        {"id": "kyoto_rain_afternoon", "prompt": "Kyoto temple in spring rain, cherry blossoms with raindrops, wet stone paths, zen rainy atmosphere"},
    ],
    "afternoon_summer_rain": [
        {"id": "nyc_summer_storm", "prompt": "New York City sudden summer thunderstorm, rain on Times Square, wet streets reflecting lights, dramatic storm clouds"},
        {"id": "singapore_rain", "prompt": "Singapore Marina Bay during tropical afternoon rain, dramatic rain clouds, city lights beginning, monsoon atmosphere"},
    ],
    "afternoon_autumn_rain": [
        {"id": "boston_rain_fall", "prompt": "Boston rainy autumn afternoon, wet fall leaves on brick sidewalks, historic buildings through rain, New England atmosphere"},
        {"id": "dublin_rain_autumn", "prompt": "Dublin Ireland rainy autumn afternoon, cobblestone streets wet, warm pub lights glowing through rain, Irish weather"},
    ],
    "afternoon_winter_rain": [
        {"id": "london_winter_rain", "prompt": "London rainy winter afternoon, wet Oxford Street, holiday decorations through rain, moody British winter"},
        {"id": "san_francisco_rain", "prompt": "San Francisco rainy winter afternoon, wet hills, cable cars, Golden Gate in fog and rain, moody coastal weather"},
    ],
    "evening_spring_rain": [
        {"id": "tokyo_rain_evening", "prompt": "Tokyo rainy spring evening, neon lights reflecting in puddles, cherry blossoms in rain, atmospheric Japanese night"},
        {"id": "rome_rain_sunset", "prompt": "Rome rainy spring evening, wet ancient streets, warm light through rain, Colosseum in background, romantic atmosphere"},
    ],
    "evening_summer_rain": [
        {"id": "miami_storm_sunset", "prompt": "Miami summer thunderstorm at sunset, dramatic lightning on horizon, rain over ocean, Art Deco buildings, tropical storm drama"},
        {"id": "bangkok_rain_evening", "prompt": "Bangkok rainy summer evening, wet streets with tuk tuks, neon signs reflecting, tropical monsoon atmosphere"},
    ],
    "evening_autumn_rain": [
        {"id": "paris_rain_autumn", "prompt": "Paris rainy autumn evening, wet Champs-Élysées, golden leaves in puddles, warm cafe lights through rain, romantic moody"},
        {"id": "vancouver_rain_fall", "prompt": "Vancouver rainy autumn evening, city lights reflecting on wet streets, mountains hidden in rain clouds, moody Pacific Northwest"},
    ],
    "evening_winter_rain": [
        {"id": "tokyo_winter_rain", "prompt": "Tokyo rainy winter evening, wet Shibuya streets, neon reflecting in puddles, umbrellas, Japanese winter night"},
        {"id": "seattle_rain_evening", "prompt": "Seattle rainy winter evening, Pike Place neon reflecting on wet streets, Space Needle through drizzle, moody atmosphere"},
    ],
    "night_spring_rain": [
        {"id": "seoul_rain_night", "prompt": "Seoul rainy spring night, neon lights reflecting on wet streets, cherry blossoms in rain, Korean urban night scene"},
        {"id": "nyc_rain_night_spring", "prompt": "New York City rainy spring night, Times Square lights in puddles, taxis, umbrellas, cinematic urban rain"},
    ],
    "night_summer_rain": [
        {"id": "hong_kong_rain", "prompt": "Hong Kong rainy summer night, neon signs reflecting on wet streets, dramatic atmosphere, Asian metropolis in rain"},
        {"id": "la_rain_night", "prompt": "Los Angeles rare rainy summer night, Sunset Boulevard wet reflections, palm trees in rain, cinematic LA noir"},
    ],
    "night_autumn_rain": [
        {"id": "london_rain_night_fall", "prompt": "London rainy autumn night, Tower Bridge through rain, wet streets reflecting lights, atmospheric British night"},
        {"id": "chicago_rain_autumn", "prompt": "Chicago rainy autumn night, Magnificent Mile wet reflections, city lights through rain, moody midwest night"},
    ],
    "night_winter_rain": [
        {"id": "paris_rain_winter_night", "prompt": "Paris rainy winter night, Eiffel Tower through rain, wet boulevards with lights, romantic moody atmosphere"},
        {"id": "tokyo_rain_winter_night", "prompt": "Tokyo rainy winter night, Akihabara neon in rain puddles, atmospheric Japanese cyberpunk vibes"},
    ],

    # ==================== CLOUDY WEATHER (2 images each) ====================
    "morning_spring_cloudy": [
        {"id": "scottish_cloudy_spring", "prompt": "Scottish Highlands cloudy spring morning, dramatic overcast sky, green hills, moody atmospheric landscape"},
        {"id": "iceland_cloudy_spring", "prompt": "Iceland dramatic cloudy spring morning, low clouds over green moss fields, volcanic landscape, moody atmosphere"},
    ],
    "morning_summer_cloudy": [
        {"id": "norway_cloudy_summer", "prompt": "Norwegian fjords cloudy summer morning, dramatic low clouds in valley, deep blue water, moody Scandinavian landscape"},
        {"id": "ireland_cloudy_morning", "prompt": "Ireland Cliffs of Moher cloudy summer morning, dramatic overcast, emerald green grass, Atlantic mist, wild beauty"},
    ],
    "morning_autumn_cloudy": [
        {"id": "vermont_cloudy_fall", "prompt": "Vermont cloudy autumn morning, overcast sky, brilliant fall colors pop against grey clouds, moody New England"},
        {"id": "bavaria_cloudy_autumn", "prompt": "Bavarian Alps cloudy autumn morning, fog in valleys, fall colors, dramatic cloud formations, German moody landscape"},
    ],
    "morning_winter_cloudy": [
        {"id": "alps_cloudy_winter", "prompt": "Swiss Alps cloudy winter morning, dramatic grey sky, snow-covered peaks emerging from clouds, moody Alpine scene"},
        {"id": "hokkaido_cloudy_winter", "prompt": "Hokkaido Japan cloudy winter morning, grey sky, snow-covered landscape, muted tones, peaceful winter atmosphere"},
    ],
    "afternoon_spring_cloudy": [
        {"id": "english_cloudy_spring", "prompt": "English Lake District cloudy spring afternoon, overcast sky, green hills, dramatic clouds, British landscape"},
        {"id": "patagonia_cloudy_spring", "prompt": "Patagonia dramatic cloudy spring afternoon, Torres del Paine, dramatic storm clouds, wild landscape"},
    ],
    "afternoon_summer_cloudy": [
        {"id": "new_zealand_cloudy", "prompt": "New Zealand South Island cloudy summer afternoon, dramatic mountain clouds, green valleys, epic landscape"},
        {"id": "faroe_islands_cloudy", "prompt": "Faroe Islands dramatic cloudy summer afternoon, green cliffs, dramatic sky, North Atlantic moody beauty"},
    ],
    "afternoon_autumn_cloudy": [
        {"id": "scotland_cloudy_autumn", "prompt": "Scottish Highlands cloudy autumn afternoon, dramatic sky over golden hills, lochs, moody atmospheric beauty"},
        {"id": "oregon_cloudy_fall", "prompt": "Oregon coast cloudy autumn afternoon, dramatic Pacific sky, fall colors, rugged coastline, moody Pacific Northwest"},
    ],
    "afternoon_winter_cloudy": [
        {"id": "iceland_cloudy_winter", "prompt": "Iceland cloudy winter afternoon, grey dramatic sky, snow-covered volcanic landscape, moody Nordic beauty"},
        {"id": "norway_cloudy_winter", "prompt": "Norwegian mountains cloudy winter afternoon, dramatic grey sky, fjords, snow-covered peaks, Nordic drama"},
    ],
    "evening_spring_cloudy": [
        {"id": "paris_cloudy_evening", "prompt": "Paris cloudy spring evening, dramatic grey sky, Eiffel Tower silhouette, moody romantic atmosphere"},
        {"id": "san_francisco_cloudy", "prompt": "San Francisco cloudy spring evening, fog rolling over Golden Gate, dramatic clouds, moody coastal atmosphere"},
    ],
    "evening_summer_cloudy": [
        {"id": "seattle_cloudy_summer", "prompt": "Seattle cloudy summer evening, overcast sky, Space Needle, Puget Sound, moody Pacific Northwest atmosphere"},
        {"id": "reykjavik_cloudy_summer", "prompt": "Reykjavik Iceland cloudy summer evening, dramatic sky, midnight sun behind clouds, colorful houses"},
    ],
    "evening_autumn_cloudy": [
        {"id": "amsterdam_cloudy_fall", "prompt": "Amsterdam cloudy autumn evening, dramatic grey sky, canal reflections, fall trees, moody Dutch atmosphere"},
        {"id": "edinburgh_cloudy_autumn", "prompt": "Edinburgh cloudy autumn evening, castle against dramatic sky, golden foliage, moody Scottish atmosphere"},
    ],
    "evening_winter_cloudy": [
        {"id": "london_cloudy_winter", "prompt": "London cloudy winter evening, dramatic grey sky, Thames, Big Ben silhouette, moody British atmosphere"},
        {"id": "stockholm_cloudy_winter", "prompt": "Stockholm cloudy winter evening, grey sky, city lights emerging, old town, moody Nordic atmosphere"},
    ],
    "night_spring_cloudy": [
        {"id": "tokyo_cloudy_night_spring", "prompt": "Tokyo cloudy spring night, city lights diffused through clouds, cherry blossoms, atmospheric urban night"},
        {"id": "nyc_cloudy_night_spring", "prompt": "New York cloudy spring night, Manhattan lights through overcast sky, moody urban atmosphere"},
    ],
    "night_summer_cloudy": [
        {"id": "chicago_cloudy_summer_night", "prompt": "Chicago cloudy summer night, city skyline, lights glowing through low clouds, Lake Michigan, urban atmosphere"},
        {"id": "hong_kong_cloudy_night", "prompt": "Hong Kong cloudy summer night, city lights through haze, Victoria Peak view, dramatic urban atmosphere"},
    ],
    "night_autumn_cloudy": [
        {"id": "paris_cloudy_autumn_night", "prompt": "Paris cloudy autumn night, Eiffel Tower lights through overcast, moody romantic atmosphere"},
        {"id": "seattle_cloudy_autumn_night", "prompt": "Seattle cloudy autumn night, city lights through clouds, Space Needle, moody Pacific Northwest urban night"},
    ],
    "night_winter_cloudy": [
        {"id": "moscow_cloudy_winter_night", "prompt": "Moscow cloudy winter night, Red Square lights through snow clouds, dramatic winter urban atmosphere"},
        {"id": "berlin_cloudy_winter_night", "prompt": "Berlin cloudy winter night, Brandenburg Gate lit up through overcast, moody German winter atmosphere"},
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


def build_prompt(scene: dict, time_of_day: str, season: str, weather: str = None) -> str:
    time_info = TIMES_OF_DAY[time_of_day]
    season_info = SEASONS[season]

    weather_section = ""
    if weather and weather in WEATHER_MODIFIERS:
        weather_info = WEATHER_MODIFIERS[weather]
        weather_section = f"""

WEATHER CONDITION - {weather.upper()}:
Atmosphere: {weather_info['atmosphere']}
Lighting effect: {weather_info['lighting']}
Weather elements: {weather_info['elements']}"""

    prompt = f"""
{GLOBAL_VISUAL_DNA}

{COMPOSITION_RULE}

SCENE DESCRIPTION:
{scene['prompt']}

TIME OF DAY - {time_of_day.upper()}:
Lighting style: {time_info['lighting']}
{"Sun or Moon position: " + time_info['sun_position'] if not weather else "Light diffused through " + weather + " conditions"}
Sky and color palette: {time_info['palette']}

SEASON - {season.upper()}:
Seasonal characteristics: {season_info['elements']}
Overall atmosphere: {season_info['atmosphere']}
Sky style: {season_info['sky']}{weather_section}

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
- NO COLLAGES, NO GRIDS, NO 2x2 LAYOUTS, NO MULTIPLE IMAGES - SINGLE IMAGE ONLY
- NO split screens or side-by-side comparisons
- Pure natural landscape scenery only - ONE SINGLE CONTINUOUS IMAGE
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
        parts = key.split("_")
        time_of_day = parts[0]
        season = parts[1]
        weather = None
        if len(parts) > 2:
            weather = parts[2]  # "rain" or "cloudy"
        for scene in scenes[:MAX_IMAGES_PER_COMBINATION]:
            all_combinations.append((time_of_day, season, weather, scene))

    print(f"Total images to generate: {len(all_combinations)}")
    print("=" * 60)
    print()

    for time_of_day, season, weather, scene in tqdm(all_combinations, desc="Generating"):
        scene_id = scene["id"]
        if weather:
            filename = f"{time_of_day}_{season}_{weather}_{scene_id}.png"
            subfolder = f"{time_of_day}_{weather}"
        else:
            filename = f"{time_of_day}_{season}_{scene_id}.png"
            subfolder = time_of_day
        output_path = OUTPUT_DIR / subfolder / filename

        if output_path.exists():
            tqdm.write(f"  Skipping (exists): {filename}")
            report.append({
                "time": time_of_day,
                "season": season,
                "weather": weather or "clear",
                "scene": scene["id"],
                "filename": filename,
                "status": "skipped_existing",
            })
            continue

        prompt = build_prompt(scene, time_of_day, season, weather)

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
                "weather": weather or "clear",
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
                "weather": weather or "clear",
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
