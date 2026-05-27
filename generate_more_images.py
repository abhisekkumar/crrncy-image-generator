"""
Interactive script to generate additional CB images
Calculates totals and asks for confirmation before generating
Supports both original scenes and new diverse scenes (Asia, beaches, mountains, etc.)
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Check API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("Error: Missing GEMINI_API_KEY in .env file")
    sys.exit(1)

# Import generation functions from main script
from generate_cb_images import (
    TIMES_OF_DAY, SEASONS, GLOBAL_VISUAL_DNA, COMPOSITION_RULE,
    generate_image, OUTPUT_DIR
)

# ============================================================================
# ORIGINAL SCENES (European, Americas, Classic destinations)
# ============================================================================
ORIGINAL_SCENES = {
    # CLEAR WEATHER
    "morning_spring_clear": [
        {"id": "tuscany_spring_dawn", "prompt": "Tuscany Italian countryside rolling hills with cypress trees, spring wildflowers, golden sunrise, morning mist in valleys"},
        {"id": "amsterdam_tulips_morning", "prompt": "Amsterdam tulip fields in full bloom, windmills in distance, spring morning golden light, colorful flower rows"},
        {"id": "new_zealand_spring_morning", "prompt": "New Zealand Hobbiton-like green hills, spring lambs, morning dew on grass, snow-capped mountains distant"},
        {"id": "washington_dc_cherry_morning", "prompt": "Washington DC Tidal Basin cherry blossoms, Jefferson Memorial, spring sunrise reflection on water"},
    ],
    "morning_summer_clear": [
        {"id": "amalfi_coast_morning", "prompt": "Amalfi Coast Italy cliffside villages, turquoise Mediterranean sea, summer morning sun, lemon trees"},
        {"id": "bali_rice_terraces_morning", "prompt": "Bali rice terraces Tegallalang, morning golden light, palm trees, tropical summer atmosphere"},
        {"id": "iceland_midnight_sun", "prompt": "Iceland summer midnight sun landscape, green valleys, waterfalls, golden hour light at dawn"},
        {"id": "monaco_harbor_morning", "prompt": "Monaco Monte Carlo harbor, luxury yachts, summer morning sun, Mediterranean blue water"},
    ],
    "morning_autumn_clear": [
        {"id": "vermont_fall_farm", "prompt": "Vermont countryside red barn, autumn maple trees peak foliage, morning mist, rolling hills"},
        {"id": "scotland_highlands_autumn", "prompt": "Scottish Highlands heather moorland, autumn purple and gold, morning light, misty mountains"},
        {"id": "napa_valley_fall_morning", "prompt": "Napa Valley vineyards autumn colors, grape vines golden and red, morning fog, rolling hills"},
        {"id": "quebec_fall_morning", "prompt": "Quebec Canada autumn forest, maple trees red and orange, morning golden light, lake reflection"},
    ],
    "morning_winter_clear": [
        {"id": "hokkaido_snow_morning", "prompt": "Hokkaido Japan snow-covered village, traditional houses, winter sunrise, steam rising from onsen"},
        {"id": "banff_winter_morning", "prompt": "Banff Canada frozen Lake Louise, snow-covered mountains, winter sunrise, turquoise ice"},
        {"id": "lapland_winter_dawn", "prompt": "Finnish Lapland snow forest, reindeer, winter morning pink sky, frozen trees"},
        {"id": "salzburg_winter_morning", "prompt": "Salzburg Austria old town, snow-covered rooftops, winter morning, fortress on hill"},
    ],
    "afternoon_spring_clear": [
        {"id": "provence_lavender_spring", "prompt": "Provence France early lavender fields, spring afternoon sun, stone farmhouse, blue sky"},
        {"id": "cinque_terre_spring", "prompt": "Cinque Terre Italy colorful villages on cliffs, spring flowers, afternoon Mediterranean light"},
        {"id": "bruges_spring_afternoon", "prompt": "Bruges Belgium canals, spring flowers on bridges, swans, afternoon golden light"},
        {"id": "cherry_blossom_dc_afternoon", "prompt": "Washington DC cherry blossoms peak bloom, afternoon sun, petals floating, blue sky"},
    ],
    "afternoon_summer_clear": [
        {"id": "capri_blue_grotto", "prompt": "Capri Italy Faraglioni rocks, bright blue sea, summer afternoon sun, luxury boats"},
        {"id": "mykonos_afternoon", "prompt": "Mykonos Greece white buildings blue domes, summer afternoon, windmills, Aegean sea"},
        {"id": "lake_como_afternoon", "prompt": "Lake Como Italy villas, cypress trees, summer afternoon sun, Alps background"},
        {"id": "french_riviera_afternoon", "prompt": "French Riviera Nice coastline, azure sea, summer afternoon, palm trees, beach umbrellas"},
    ],
    "afternoon_autumn_clear": [
        {"id": "cotswolds_autumn", "prompt": "English Cotswolds stone villages, autumn golden trees, afternoon sun, rolling countryside"},
        {"id": "rhine_valley_autumn", "prompt": "Rhine Valley Germany castles on hills, autumn vineyards, afternoon golden light, river"},
        {"id": "aspen_fall_afternoon", "prompt": "Aspen Colorado golden aspen trees, mountain peaks, autumn afternoon sun, blue sky"},
        {"id": "seoul_palace_autumn", "prompt": "Seoul Gyeongbokgung Palace, autumn ginkgo trees golden, afternoon light, traditional architecture"},
    ],
    "afternoon_winter_clear": [
        {"id": "zermatt_matterhorn", "prompt": "Zermatt Switzerland Matterhorn peak, winter afternoon sun, snow-covered village, skiers"},
        {"id": "prague_winter_afternoon", "prompt": "Prague old town Charles Bridge, winter afternoon, snow dusting, golden spires"},
        {"id": "st_moritz_afternoon", "prompt": "St Moritz Switzerland frozen lake, winter sports, afternoon sun, luxury alpine resort"},
        {"id": "quebec_city_winter", "prompt": "Quebec City Chateau Frontenac, winter afternoon, snow-covered rooftops, St Lawrence River"},
    ],
    "evening_spring_clear": [
        {"id": "paris_spring_sunset", "prompt": "Paris Eiffel Tower spring sunset, cherry blossoms, Seine River golden reflections"},
        {"id": "amsterdam_sunset_spring", "prompt": "Amsterdam canals sunset, spring tulips on houseboats, golden hour reflections"},
        {"id": "vienna_spring_evening", "prompt": "Vienna Austria Belvedere gardens, spring flowers sunset, palace silhouette"},
        {"id": "barcelona_spring_sunset", "prompt": "Barcelona Park Guell sunset, spring evening, Gaudi mosaics, city view golden hour"},
    ],
    "evening_summer_clear": [
        {"id": "dubrovnik_sunset", "prompt": "Dubrovnik Croatia old town walls, summer sunset over Adriatic, orange rooftops"},
        {"id": "venice_summer_sunset", "prompt": "Venice Grand Canal sunset, gondolas, summer evening golden light, St Marks in distance"},
        {"id": "sydney_harbor_sunset", "prompt": "Sydney Harbor Opera House sunset, summer evening, harbor bridge silhouette"},
        {"id": "rio_sunset", "prompt": "Rio de Janeiro Sugarloaf sunset, summer evening, Guanabara Bay golden light"},
    ],
    "evening_autumn_clear": [
        {"id": "boston_fall_sunset", "prompt": "Boston skyline autumn sunset, fall foliage Charles River, golden hour reflection"},
        {"id": "munich_autumn_sunset", "prompt": "Munich Marienplatz autumn sunset, golden fall trees, historic buildings glowing"},
        {"id": "portland_fall_evening", "prompt": "Portland Oregon autumn sunset, Mount Hood silhouette, fall colors, city lights emerging"},
        {"id": "chicago_fall_sunset", "prompt": "Chicago skyline autumn sunset, Lake Michigan golden reflections, fall colors Millennium Park"},
    ],
    "evening_winter_clear": [
        {"id": "vienna_winter_sunset", "prompt": "Vienna Christmas markets sunset, winter evening lights, St Stephens Cathedral"},
        {"id": "copenhagen_winter_evening", "prompt": "Copenhagen Nyhavn winter sunset, colorful buildings snow-dusted, lights reflecting"},
        {"id": "boston_winter_sunset", "prompt": "Boston Back Bay winter sunset, snow-covered brownstones, golden hour"},
        {"id": "stockholm_winter_evening", "prompt": "Stockholm Gamla Stan winter sunset, snow on rooftops, lights emerging, frozen harbor"},
    ],
    "night_spring_clear": [
        {"id": "tokyo_spring_night", "prompt": "Tokyo Tower night cherry blossoms, spring night illumination, city lights"},
        {"id": "washington_night_spring", "prompt": "Washington DC monuments night, spring cherry blossoms illuminated, reflection pool"},
        {"id": "london_spring_night", "prompt": "London Tower Bridge night spring, Thames reflections, city lights, clear starry sky"},
        {"id": "shanghai_spring_night", "prompt": "Shanghai Bund skyline night spring, Pudong towers lit, Huangpu River reflections"},
    ],
    "night_summer_clear": [
        {"id": "las_vegas_night", "prompt": "Las Vegas Strip night summer, neon lights, Bellagio fountains, desert stars above"},
        {"id": "singapore_night_summer", "prompt": "Singapore Marina Bay night, Gardens by Bay Supertrees lit, summer night"},
        {"id": "hong_kong_victoria_night", "prompt": "Hong Kong Victoria Peak view night, city lights symphony, summer clear sky"},
        {"id": "dubai_night_summer", "prompt": "Dubai Burj Khalifa night, downtown lights, summer evening, fountain show"},
    ],
    "night_autumn_clear": [
        {"id": "kyoto_autumn_night", "prompt": "Kyoto temples autumn night illumination, red maple trees lit, reflection ponds"},
        {"id": "new_york_fall_night", "prompt": "New York Central Park autumn night, city skyline lights, fall trees silhouette"},
        {"id": "paris_autumn_night", "prompt": "Paris Louvre autumn night, illuminated pyramid, fall leaves, clear starry sky"},
        {"id": "toronto_fall_night", "prompt": "Toronto CN Tower autumn night, city lights, fall colors illuminated, Lake Ontario"},
    ],
    "night_winter_clear": [
        {"id": "reykjavik_aurora", "prompt": "Reykjavik Iceland northern lights winter night, city lights below, aurora dancing"},
        {"id": "nyc_christmas_night", "prompt": "New York Rockefeller Center Christmas tree night, winter lights, ice skating"},
        {"id": "london_winter_night", "prompt": "London Big Ben winter night, snow falling, Christmas lights, Thames reflections"},
        {"id": "moscow_winter_night", "prompt": "Moscow Red Square winter night, St Basils illuminated, snow, Christmas decorations"},
    ],
    # RAIN
    "morning_spring_rain": [
        {"id": "london_spring_rain", "prompt": "London Hyde Park spring rain morning, cherry blossoms wet, umbrellas, puddle reflections"},
        {"id": "seattle_spring_rain_am", "prompt": "Seattle Space Needle spring rain morning, Pike Place flowers wet, misty mountains"},
        {"id": "dublin_spring_rain", "prompt": "Dublin Ireland spring rain morning, Georgian doors, wet cobblestones, green parks"},
        {"id": "vancouver_spring_rain", "prompt": "Vancouver spring rain morning, Stanley Park wet cherry blossoms, mountains in mist"},
    ],
    "morning_summer_rain": [
        {"id": "bali_monsoon_morning", "prompt": "Bali tropical rain morning, rice terraces, warm summer rain, lush green"},
        {"id": "hawaii_rain_morning", "prompt": "Hawaii Kauai summer rain morning, rainbow forming, tropical flowers wet, waterfalls"},
        {"id": "singapore_rain_morning", "prompt": "Singapore Gardens by Bay summer rain morning, tropical storm, Supertrees wet"},
        {"id": "costa_rica_rain_morning", "prompt": "Costa Rica rainforest summer morning rain, cloud forest, exotic birds, misty"},
    ],
    "morning_autumn_rain": [
        {"id": "seattle_fall_rain", "prompt": "Seattle autumn rain morning, fall leaves in puddles, coffee shop warmth, Pike Place"},
        {"id": "portland_autumn_rain", "prompt": "Portland Oregon autumn rain morning, Japanese Garden wet maples, misty"},
        {"id": "dublin_autumn_rain", "prompt": "Dublin Trinity College autumn rain morning, wet cobblestones, golden leaves falling"},
        {"id": "edinburgh_fall_rain", "prompt": "Edinburgh Royal Mile autumn rain morning, wet stone, golden leaves, castle misty"},
    ],
    "morning_winter_rain": [
        {"id": "london_winter_rain_am", "prompt": "London winter rain morning, Thames grey, red buses reflections, bare trees wet"},
        {"id": "san_francisco_winter_rain", "prompt": "San Francisco winter rain morning, Golden Gate in fog, wet streets reflecting"},
        {"id": "paris_winter_rain_am", "prompt": "Paris winter rain morning, Champs Elysees wet, bare trees, grey elegant mood"},
        {"id": "melbourne_winter_rain", "prompt": "Melbourne winter rain morning, laneways wet, coffee culture, trams reflecting"},
    ],
    "afternoon_spring_rain": [
        {"id": "kyoto_spring_rain_pm", "prompt": "Kyoto spring rain afternoon, cherry blossoms falling in rain, temples wet, reflections"},
        {"id": "amsterdam_spring_rain", "prompt": "Amsterdam spring rain afternoon, tulips wet, canal reflections, cozy cafes"},
        {"id": "brussels_spring_rain", "prompt": "Brussels Grand Place spring rain afternoon, wet cobblestones reflecting gold buildings"},
        {"id": "wellington_spring_rain", "prompt": "Wellington New Zealand spring rain afternoon, harbor wet, hills green, cable car"},
    ],
    "afternoon_summer_rain": [
        {"id": "bangkok_monsoon", "prompt": "Bangkok summer monsoon rain afternoon, temples wet, Chao Phraya River, tropical"},
        {"id": "miami_summer_storm", "prompt": "Miami summer afternoon storm, Art Deco wet, palm trees rain, ocean grey"},
        {"id": "rio_summer_rain", "prompt": "Rio de Janeiro summer rain afternoon, Copacabana wet, dramatic clouds, warm rain"},
        {"id": "mumbai_monsoon_pm", "prompt": "Mumbai monsoon afternoon, Marine Drive wet, Arabian Sea rain, Gateway of India"},
    ],
    "afternoon_autumn_rain": [
        {"id": "boston_fall_rain", "prompt": "Boston autumn rain afternoon, Back Bay brownstones wet, fall leaves in puddles"},
        {"id": "prague_autumn_rain", "prompt": "Prague autumn rain afternoon, Charles Bridge wet, golden leaves falling, misty"},
        {"id": "vienna_fall_rain", "prompt": "Vienna autumn rain afternoon, Ringstrasse wet, yellow leaves, coffee house warmth"},
        {"id": "montreal_autumn_rain", "prompt": "Montreal autumn rain afternoon, Old Montreal wet cobblestones, fall colors, Notre Dame"},
    ],
    "afternoon_winter_rain": [
        {"id": "seattle_winter_rain_pm", "prompt": "Seattle winter rain afternoon, grey skies, Puget Sound, coffee shop windows wet"},
        {"id": "lisbon_winter_rain", "prompt": "Lisbon winter rain afternoon, trams wet streets, Alfama tiles reflecting"},
        {"id": "dublin_winter_rain", "prompt": "Dublin winter rain afternoon, Temple Bar wet cobblestones, pub warmth glowing"},
        {"id": "auckland_winter_rain", "prompt": "Auckland winter rain afternoon, harbor wet, Sky Tower in mist, green hills"},
    ],
    "evening_spring_rain": [
        {"id": "tokyo_spring_rain_eve", "prompt": "Tokyo Shibuya spring rain evening, neon reflections wet streets, cherry petals floating"},
        {"id": "paris_spring_rain_eve", "prompt": "Paris spring rain evening, Eiffel Tower lights in rain, wet boulevards shimmering"},
        {"id": "seoul_spring_rain", "prompt": "Seoul Gangnam spring rain evening, neon lights reflecting, cherry blossoms wet"},
        {"id": "london_spring_rain_eve", "prompt": "London West End spring rain evening, theatre lights reflecting, wet streets golden"},
    ],
    "evening_summer_rain": [
        {"id": "nyc_summer_rain_eve", "prompt": "New York Times Square summer rain evening, neon reflections, steam rising, dramatic"},
        {"id": "tokyo_summer_rain_eve", "prompt": "Tokyo Ginza summer rain evening, neon lights wet streets, umbrellas, warm humidity"},
        {"id": "hong_kong_rain_eve", "prompt": "Hong Kong summer rain evening, neon signs reflecting, wet streets, Victoria Harbor"},
        {"id": "singapore_rain_eve", "prompt": "Singapore Orchard Road summer rain evening, mall lights reflecting, tropical night"},
    ],
    "evening_autumn_rain": [
        {"id": "nyc_fall_rain_eve", "prompt": "New York autumn rain evening, Manhattan lights in puddles, yellow taxis, fall mood"},
        {"id": "chicago_fall_rain", "prompt": "Chicago autumn rain evening, Michigan Avenue wet, city lights reflecting, fall leaves"},
        {"id": "berlin_autumn_rain", "prompt": "Berlin autumn rain evening, Brandenburg Gate wet, city lights, golden leaves"},
        {"id": "san_fran_fall_rain", "prompt": "San Francisco autumn rain evening, cable car wet tracks, city lights in fog"},
    ],
    "evening_winter_rain": [
        {"id": "london_winter_rain_eve", "prompt": "London winter rain evening, Oxford Street Christmas lights reflecting, wet streets"},
        {"id": "paris_winter_rain_eve", "prompt": "Paris winter rain evening, Champs Elysees Christmas lights in rain, romantic"},
        {"id": "tokyo_winter_rain_eve", "prompt": "Tokyo winter rain evening, Shibuya crossing wet, neon reflections, cold mood"},
        {"id": "vancouver_winter_rain", "prompt": "Vancouver winter rain evening, Gastown steam clock, wet streets, harbor lights"},
    ],
    "night_spring_rain": [
        {"id": "osaka_spring_rain_night", "prompt": "Osaka Dotonbori spring rain night, neon reflections canal, cherry petals in water"},
        {"id": "shanghai_spring_rain", "prompt": "Shanghai Nanjing Road spring rain night, neon puddle reflections, umbrellas"},
        {"id": "taipei_spring_rain", "prompt": "Taipei night markets spring rain, lanterns reflecting wet streets, steam rising"},
        {"id": "hong_kong_spring_rain", "prompt": "Hong Kong Mong Kok spring rain night, neon signs wet, dense urban lights"},
    ],
    "night_summer_rain": [
        {"id": "bangkok_night_rain", "prompt": "Bangkok Khao San Road summer rain night, neon signs wet, tropical night"},
        {"id": "miami_night_storm", "prompt": "Miami South Beach summer storm night, Art Deco neon in rain, ocean lightning"},
        {"id": "tokyo_shibuya_rain", "prompt": "Tokyo Shibuya summer rain night, famous crossing wet, neon everywhere reflecting"},
        {"id": "las_vegas_rain_night", "prompt": "Las Vegas summer rain night, Strip lights reflecting wet streets, desert storm"},
    ],
    "night_autumn_rain": [
        {"id": "london_fall_rain_night", "prompt": "London autumn rain night, Piccadilly Circus lights in puddles, double deckers"},
        {"id": "chicago_fall_rain_night", "prompt": "Chicago autumn rain night, Loop elevated train, city lights wet streets"},
        {"id": "boston_fall_rain_night", "prompt": "Boston autumn rain night, Beacon Hill wet cobblestones, gas lamps glowing"},
        {"id": "toronto_fall_rain_night", "prompt": "Toronto autumn rain night, Yonge Street neon reflecting, CN Tower in mist"},
    ],
    "night_winter_rain": [
        {"id": "nyc_winter_rain_night", "prompt": "New York winter rain night, Times Square neon in rain, cold wet streets"},
        {"id": "seattle_winter_rain_night", "prompt": "Seattle winter rain night, Pike Place neon wet, harbor lights in mist"},
        {"id": "portland_winter_rain_night", "prompt": "Portland winter rain night, downtown bridges wet, river reflections"},
        {"id": "sf_winter_rain_night", "prompt": "San Francisco winter rain night, Chinatown lanterns wet, cable car tracks shining"},
    ],
    # CLOUDY
    "morning_spring_cloudy": [
        {"id": "london_cloudy_spring_am", "prompt": "London spring cloudy morning, soft diffused light, Hyde Park flowers, moody elegant"},
        {"id": "seattle_cloudy_spring", "prompt": "Seattle spring cloudy morning, cherry blossoms soft light, mountains hidden, cozy"},
        {"id": "dublin_cloudy_spring", "prompt": "Dublin spring cloudy morning, soft grey light, green everywhere, Georgian elegance"},
        {"id": "edinburgh_cloudy_spring", "prompt": "Edinburgh spring cloudy morning, Arthur's Seat misty, soft light, castle dramatic"},
    ],
    "morning_summer_cloudy": [
        {"id": "iceland_cloudy_summer", "prompt": "Iceland summer cloudy morning, dramatic clouds, green valleys, waterfalls, moody"},
        {"id": "scotland_cloudy_summer", "prompt": "Scottish Highlands summer cloudy morning, lochs moody, dramatic skies, heather"},
        {"id": "norway_cloudy_summer", "prompt": "Norway fjords summer cloudy morning, dramatic clouds, waterfalls, moody light"},
        {"id": "ireland_cloudy_summer", "prompt": "Ireland Cliffs of Moher summer cloudy morning, dramatic ocean, wild Atlantic"},
    ],
    "morning_autumn_cloudy": [
        {"id": "portland_cloudy_fall", "prompt": "Portland Oregon autumn cloudy morning, fall colors muted light, coffee culture"},
        {"id": "vancouver_cloudy_fall", "prompt": "Vancouver autumn cloudy morning, Stanley Park fall colors, mountains in clouds"},
        {"id": "oslo_cloudy_autumn", "prompt": "Oslo autumn cloudy morning, fjord misty, fall colors soft light, Nordic mood"},
        {"id": "helsinki_cloudy_fall", "prompt": "Helsinki autumn cloudy morning, harbor grey, fall trees golden, Nordic design"},
    ],
    "morning_winter_cloudy": [
        {"id": "london_cloudy_winter_am", "prompt": "London winter cloudy morning, grey elegant, Thames moody, bare trees silhouette"},
        {"id": "copenhagen_cloudy_winter", "prompt": "Copenhagen winter cloudy morning, Nyhavn muted colors, cozy hygge atmosphere"},
        {"id": "stockholm_cloudy_winter", "prompt": "Stockholm winter cloudy morning, Gamla Stan grey, frozen harbor, Nordic mood"},
        {"id": "amsterdam_cloudy_winter", "prompt": "Amsterdam winter cloudy morning, canals grey, bare trees, cozy houseboats"},
    ],
    "afternoon_spring_cloudy": [
        {"id": "paris_cloudy_spring", "prompt": "Paris spring cloudy afternoon, soft romantic light, Seine moody, cherry blossoms"},
        {"id": "bruges_cloudy_spring", "prompt": "Bruges spring cloudy afternoon, medieval charm, soft light, canals reflective"},
        {"id": "bath_cloudy_spring", "prompt": "Bath England spring cloudy afternoon, Georgian architecture, soft diffused light"},
        {"id": "prague_cloudy_spring", "prompt": "Prague spring cloudy afternoon, spires dramatic against clouds, Charles Bridge moody"},
    ],
    "afternoon_summer_cloudy": [
        {"id": "big_sur_cloudy", "prompt": "Big Sur California summer cloudy afternoon, dramatic coastal cliffs, fog rolling in"},
        {"id": "cornwall_cloudy_summer", "prompt": "Cornwall England summer cloudy afternoon, dramatic cliffs, wild ocean, moody"},
        {"id": "brittany_cloudy_summer", "prompt": "Brittany France summer cloudy afternoon, dramatic coastline, grey seas, stone villages"},
        {"id": "tasmania_cloudy_summer", "prompt": "Tasmania summer cloudy afternoon, wild coastline, dramatic clouds, rugged beauty"},
    ],
    "afternoon_autumn_cloudy": [
        {"id": "cotswolds_cloudy_fall", "prompt": "Cotswolds autumn cloudy afternoon, golden villages muted light, cozy stone cottages"},
        {"id": "lake_district_cloudy", "prompt": "English Lake District autumn cloudy afternoon, moody lakes, fall colors, dramatic"},
        {"id": "black_forest_cloudy", "prompt": "Black Forest Germany autumn cloudy afternoon, misty trees, dramatic valleys, moody"},
        {"id": "swiss_alps_cloudy_fall", "prompt": "Swiss Alps autumn cloudy afternoon, dramatic peaks in clouds, fall meadows"},
    ],
    "afternoon_winter_cloudy": [
        {"id": "london_cloudy_winter_pm", "prompt": "London winter cloudy afternoon, grey elegant Thames, St Pauls dome moody"},
        {"id": "vienna_cloudy_winter", "prompt": "Vienna winter cloudy afternoon, grey elegance, Ringstrasse dramatic, coffee house warmth"},
        {"id": "munich_cloudy_winter", "prompt": "Munich winter cloudy afternoon, Marienplatz grey, Alps hidden, cozy beer halls"},
        {"id": "zurich_cloudy_winter", "prompt": "Zurich winter cloudy afternoon, lake grey, old town elegant, Alps in clouds"},
    ],
    "evening_spring_cloudy": [
        {"id": "paris_cloudy_spring_eve", "prompt": "Paris spring cloudy evening, dramatic sunset through clouds, Eiffel silhouette"},
        {"id": "rome_cloudy_spring_eve", "prompt": "Rome spring cloudy evening, dramatic sky Vatican, soft golden light breaking through"},
        {"id": "florence_cloudy_spring", "prompt": "Florence spring cloudy evening, Duomo dramatic against clouds, golden light"},
        {"id": "lisbon_cloudy_spring", "prompt": "Lisbon spring cloudy evening, dramatic clouds over Tagus, golden light on tiles"},
    ],
    "evening_summer_cloudy": [
        {"id": "santorini_cloudy_sunset", "prompt": "Santorini summer cloudy sunset, dramatic clouds, blue domes, golden light through"},
        {"id": "amalfi_cloudy_sunset", "prompt": "Amalfi Coast summer cloudy sunset, dramatic Mediterranean clouds, villages glowing"},
        {"id": "croatia_cloudy_sunset", "prompt": "Croatian coast summer cloudy sunset, dramatic Adriatic clouds, islands silhouette"},
        {"id": "greek_islands_cloudy", "prompt": "Greek islands summer cloudy sunset, dramatic Aegean clouds, white buildings golden"},
    ],
    "evening_autumn_cloudy": [
        {"id": "nyc_cloudy_fall_eve", "prompt": "New York autumn cloudy evening, dramatic Manhattan skyline, golden light through clouds"},
        {"id": "chicago_cloudy_fall", "prompt": "Chicago autumn cloudy evening, dramatic lakefront, fall colors, city silhouette"},
        {"id": "seattle_cloudy_fall_eve", "prompt": "Seattle autumn cloudy evening, dramatic Puget Sound, fall colors, moody"},
        {"id": "boston_cloudy_fall_eve", "prompt": "Boston autumn cloudy evening, dramatic Charles River, fall colors, city lights"},
    ],
    "evening_winter_cloudy": [
        {"id": "paris_cloudy_winter_eve", "prompt": "Paris winter cloudy evening, dramatic grey sky, city lights emerging, elegant"},
        {"id": "london_cloudy_winter_eve", "prompt": "London winter cloudy evening, dramatic Thames, city lights reflecting, moody elegant"},
        {"id": "berlin_cloudy_winter", "prompt": "Berlin winter cloudy evening, dramatic sky, TV Tower silhouette, city lights"},
        {"id": "amsterdam_cloudy_winter_eve", "prompt": "Amsterdam winter cloudy evening, canal lights reflecting, dramatic grey sky"},
    ],
    "night_spring_cloudy": [
        {"id": "tokyo_cloudy_spring", "prompt": "Tokyo spring cloudy night, city lights glowing through clouds, cherry blossoms lit"},
        {"id": "seoul_cloudy_spring", "prompt": "Seoul spring cloudy night, Namsan Tower in clouds, city lights, cherry blossoms"},
        {"id": "osaka_cloudy_spring", "prompt": "Osaka spring cloudy night, castle lit, clouds dramatic, cherry trees illuminated"},
        {"id": "shanghai_cloudy_spring", "prompt": "Shanghai spring cloudy night, Bund lights in low clouds, Pudong glowing"},
    ],
    "night_summer_cloudy": [
        {"id": "hong_kong_cloudy_night", "prompt": "Hong Kong summer cloudy night, Victoria Peak clouds, city lights diffused"},
        {"id": "singapore_cloudy_night", "prompt": "Singapore summer cloudy night, Marina Bay clouds, Supertrees glowing through"},
        {"id": "dubai_cloudy_night", "prompt": "Dubai summer cloudy night, Burj Khalifa in clouds, city lights glowing"},
        {"id": "bangkok_cloudy_night", "prompt": "Bangkok summer cloudy night, temples lit, dramatic clouds, Chao Phraya lights"},
    ],
    "night_autumn_cloudy": [
        {"id": "nyc_cloudy_fall_night", "prompt": "New York autumn cloudy night, Empire State in low clouds, city lights moody"},
        {"id": "chicago_cloudy_fall_night", "prompt": "Chicago autumn cloudy night, Willis Tower in clouds, lake dark, city glowing"},
        {"id": "toronto_cloudy_fall", "prompt": "Toronto autumn cloudy night, CN Tower in clouds, city lights diffused"},
        {"id": "sf_cloudy_fall_night", "prompt": "San Francisco autumn cloudy night, Golden Gate in fog, city lights glowing"},
    ],
    "night_winter_cloudy": [
        {"id": "london_cloudy_winter_night", "prompt": "London winter cloudy night, Big Ben lights in clouds, Thames moody"},
        {"id": "paris_cloudy_winter_night", "prompt": "Paris winter cloudy night, Eiffel Tower lights in clouds, romantic moody"},
        {"id": "vienna_cloudy_winter_night", "prompt": "Vienna winter cloudy night, St Stephens in clouds, Christmas lights diffused"},
        {"id": "prague_cloudy_winter_night", "prompt": "Prague winter cloudy night, castle in clouds, Charles Bridge lights moody"},
    ],
}

# ============================================================================
# DIVERSE SCENES (Asia, India, China, Beaches, Mountains, Nature)
# ============================================================================
DIVERSE_SCENES = {
    # CLEAR WEATHER - Asia, India, China, Nature focused
    "morning_spring_clear": [
        {"id": "great_wall_china_spring", "prompt": "Great Wall of China spring morning, cherry blossoms along ancient walls, misty mountains, golden sunrise"},
        {"id": "kerala_backwaters_morning", "prompt": "Kerala India backwaters morning, houseboats, coconut palms, spring sunrise mist on water, tropical paradise"},
        {"id": "california_big_sur_morning", "prompt": "Big Sur California coastline spring morning, dramatic cliffs, Pacific Ocean, wildflowers, golden sunrise fog"},
        {"id": "austrian_alps_spring_dawn", "prompt": "Austrian Alps spring morning, snow-capped peaks, green meadows with wildflowers, traditional chalets, golden sunrise"},
    ],
    "morning_summer_clear": [
        {"id": "guilin_china_morning", "prompt": "Guilin China karst mountains summer morning, Li River, bamboo rafts, misty peaks, golden ethereal light"},
        {"id": "maldives_beach_morning", "prompt": "Maldives pristine beach summer morning, crystal turquoise water, white sand, overwater villas, sunrise"},
        {"id": "swiss_alps_summer_morning", "prompt": "Swiss Alps summer morning, green meadows, wildflowers, Matterhorn view, cows grazing, golden light"},
        {"id": "phi_phi_thailand_morning", "prompt": "Phi Phi Islands Thailand summer morning, limestone cliffs, emerald waters, longtail boats, tropical sunrise"},
    ],
    "morning_autumn_clear": [
        {"id": "jiuzhaigou_china_autumn", "prompt": "Jiuzhaigou Valley China autumn morning, turquoise lakes, fall foliage reflection, misty mountains, golden light"},
        {"id": "rajasthan_india_morning", "prompt": "Rajasthan India autumn morning, golden desert fort, camels, warm sunrise, ancient palace silhouette"},
        {"id": "yosemite_fall_morning", "prompt": "Yosemite National Park autumn morning, Half Dome, fall colors, morning mist in valley, golden light"},
        {"id": "hallstatt_austria_autumn", "prompt": "Hallstatt Austria autumn morning, lake reflection, fall foliage, alpine village, misty mountains"},
    ],
    "morning_winter_clear": [
        {"id": "harbin_china_winter", "prompt": "Harbin China winter morning, ice sculptures, snow-covered city, frozen Songhua River, winter sunrise"},
        {"id": "himalayas_nepal_winter", "prompt": "Himalayas Nepal winter morning, Everest view, snow peaks pink with sunrise, prayer flags, serene"},
        {"id": "lake_tahoe_winter_morning", "prompt": "Lake Tahoe California winter morning, snow-covered pines, frozen lake edge, Sierra Nevada sunrise"},
        {"id": "innsbruck_austria_winter", "prompt": "Innsbruck Austria winter morning, snow-covered Alps, traditional buildings, golden winter sunrise"},
    ],
    "afternoon_spring_clear": [
        {"id": "zhangjiajie_china_spring", "prompt": "Zhangjiajie China Avatar mountains spring afternoon, floating peaks, lush greenery, misty dramatic"},
        {"id": "taj_mahal_spring", "prompt": "Taj Mahal India spring afternoon, white marble glowing, reflecting pools, gardens in bloom"},
        {"id": "california_coast_spring", "prompt": "California Pacific Coast Highway spring afternoon, dramatic cliffs, wildflower blooms, turquoise ocean"},
        {"id": "dolomites_spring_afternoon", "prompt": "Dolomites Italy spring afternoon, dramatic peaks, green meadows, alpine flowers, blue sky"},
    ],
    "afternoon_summer_clear": [
        {"id": "halong_bay_vietnam", "prompt": "Ha Long Bay Vietnam summer afternoon, limestone karsts, emerald waters, traditional junk boats, blue sky"},
        {"id": "bora_bora_beach", "prompt": "Bora Bora beach summer afternoon, Mount Otemanu, crystal lagoon, overwater bungalows, paradise"},
        {"id": "grand_canyon_summer", "prompt": "Grand Canyon Arizona summer afternoon, dramatic red layers, vast canyon view, blue sky, golden light"},
        {"id": "phuket_beach_afternoon", "prompt": "Phuket Thailand beach summer afternoon, turquoise Andaman Sea, limestone cliffs, longtail boats"},
    ],
    "afternoon_autumn_clear": [
        {"id": "great_wall_autumn", "prompt": "Great Wall of China autumn afternoon, red and gold foliage, ancient stones, dramatic mountains"},
        {"id": "varanasi_ganges_autumn", "prompt": "Varanasi India Ganges River autumn afternoon, ghats, ancient temples, golden light on water"},
        {"id": "rocky_mountains_fall", "prompt": "Rocky Mountains Colorado autumn afternoon, golden aspens, snow-capped peaks, crystal clear lake"},
        {"id": "vienna_schonbrunn_autumn", "prompt": "Vienna Schonbrunn Palace autumn afternoon, golden gardens, fall foliage, baroque elegance"},
    ],
    "afternoon_winter_clear": [
        {"id": "beijing_forbidden_city_winter", "prompt": "Beijing Forbidden City winter afternoon, snow-covered rooftops, red walls, golden light, ancient majesty"},
        {"id": "jaipur_india_winter", "prompt": "Jaipur India Pink City winter afternoon, Hawa Mahal, warm golden light, clear blue sky"},
        {"id": "mammoth_mountain_winter", "prompt": "Mammoth Mountain California winter afternoon, snow-covered slopes, pine forests, Sierra Nevada peaks"},
        {"id": "salzburg_alps_winter", "prompt": "Salzburg Austria Alps winter afternoon, fortress above, snow-covered old town, dramatic peaks"},
    ],
    "evening_spring_clear": [
        {"id": "shanghai_bund_spring_sunset", "prompt": "Shanghai Bund spring sunset, Pudong skyline golden, Huangpu River reflections, cherry blossoms"},
        {"id": "udaipur_lake_sunset", "prompt": "Udaipur India Lake Pichola spring sunset, City Palace glowing, romantic golden light on water"},
        {"id": "monterey_california_sunset", "prompt": "Monterey California coastline spring sunset, cypress trees, dramatic cliffs, Pacific golden hour"},
        {"id": "tyrol_austria_sunset", "prompt": "Tyrol Austria Alps spring sunset, green valleys, snow peaks pink, traditional village golden"},
    ],
    "evening_summer_clear": [
        {"id": "beijing_summer_palace_sunset", "prompt": "Beijing Summer Palace sunset, Kunming Lake golden, pagodas silhouette, summer evening glow"},
        {"id": "goa_beach_sunset", "prompt": "Goa India beach summer sunset, Arabian Sea golden, palm trees silhouette, fishing boats"},
        {"id": "maui_beach_sunset", "prompt": "Maui Hawaii beach summer sunset, volcanic cliffs, palm trees, Pacific Ocean fire colors"},
        {"id": "seychelles_beach_sunset", "prompt": "Seychelles beach summer sunset, granite boulders, turquoise water gold, tropical paradise"},
    ],
    "evening_autumn_clear": [
        {"id": "hangzhou_west_lake_autumn", "prompt": "Hangzhou West Lake China autumn sunset, pagodas, weeping willows golden, reflection perfect"},
        {"id": "kerala_sunset_autumn", "prompt": "Kerala India autumn sunset, rice paddies golden, coconut palms silhouette, backwaters glowing"},
        {"id": "sedona_fall_sunset", "prompt": "Sedona Arizona autumn sunset, red rocks glowing, desert plants, dramatic sky fire colors"},
        {"id": "wachau_austria_autumn", "prompt": "Wachau Valley Austria autumn sunset, Danube River golden, vineyards, castles on hills"},
    ],
    "evening_winter_clear": [
        {"id": "xian_winter_sunset", "prompt": "Xi'an China ancient walls winter sunset, snow-dusted, lanterns lighting, golden hour glow"},
        {"id": "agra_taj_sunset_winter", "prompt": "Agra India Taj Mahal winter sunset, white marble pink and gold, Yamuna River reflections"},
        {"id": "death_valley_winter_sunset", "prompt": "Death Valley California winter sunset, dramatic desert colors, salt flats golden, mountains purple"},
        {"id": "vienna_belvedere_winter", "prompt": "Vienna Belvedere winter sunset, snow gardens, palace glowing gold, Alps silhouette"},
    ],
    "night_spring_clear": [
        {"id": "shanghai_pudong_night", "prompt": "Shanghai Pudong skyline spring night, Oriental Pearl Tower lit, Huangpu River reflections, modern China"},
        {"id": "jaipur_night_spring", "prompt": "Jaipur India Amber Fort spring night, illuminated walls, stars above, romantic ancient"},
        {"id": "san_francisco_night_spring", "prompt": "San Francisco Golden Gate Bridge spring night, city lights, bay reflections, fog rolling"},
        {"id": "hong_kong_peak_night", "prompt": "Hong Kong Victoria Peak spring night, city lights symphony, harbor glittering, skyscrapers"},
    ],
    "night_summer_clear": [
        {"id": "beijing_temple_heaven_night", "prompt": "Beijing Temple of Heaven summer night, illuminated ancient architecture, stars, peaceful"},
        {"id": "mumbai_marine_drive_night", "prompt": "Mumbai Marine Drive summer night, Queens Necklace lights, Arabian Sea, city skyline"},
        {"id": "joshua_tree_night", "prompt": "Joshua Tree California summer night, Milky Way stars, silhouette trees, desert dramatic"},
        {"id": "bali_temple_night", "prompt": "Bali Tanah Lot temple summer night, ocean waves, illuminated temple, stars above"},
    ],
    "night_autumn_clear": [
        {"id": "suzhou_gardens_night", "prompt": "Suzhou China classical gardens autumn night, illuminated pavilions, fall reflections, lanterns"},
        {"id": "varanasi_ghat_night", "prompt": "Varanasi India Ganges ghats autumn night, Ganga Aarti ceremony, fire lamps, spiritual glow"},
        {"id": "las_vegas_strip_fall", "prompt": "Las Vegas Strip autumn night, neon lights, fountain show, desert stars above"},
        {"id": "singapore_gardens_night", "prompt": "Singapore Gardens by Bay autumn night, Supertrees glowing, Marina Bay Sands, futuristic"},
    ],
    "night_winter_clear": [
        {"id": "harbin_ice_festival_night", "prompt": "Harbin China Ice Festival winter night, illuminated ice sculptures, colorful lights, magical"},
        {"id": "golden_temple_night_winter", "prompt": "Amritsar India Golden Temple winter night, illuminated gold reflection, serene spiritual"},
        {"id": "aspen_village_winter_night", "prompt": "Aspen Colorado village winter night, snow-covered streets, warm lights, mountains stars"},
        {"id": "zell_am_see_austria_night", "prompt": "Zell am See Austria winter night, frozen lake, Alps snow, village lights, stars"},
    ],
    # RAIN - Asia, India, China focused
    "morning_spring_rain": [
        {"id": "hangzhou_spring_rain", "prompt": "Hangzhou China West Lake spring rain morning, willows wet, pagodas misty, serene reflections"},
        {"id": "darjeeling_rain_morning", "prompt": "Darjeeling India tea plantations spring rain morning, misty hills, green terraces, Himalayas hidden"},
        {"id": "oregon_coast_rain_morning", "prompt": "Oregon coast spring rain morning, dramatic cliffs wet, waves crashing, moody Pacific"},
        {"id": "kyoto_bamboo_rain", "prompt": "Kyoto bamboo grove spring rain morning, wet green stalks, misty path, peaceful Japanese"},
    ],
    "morning_summer_rain": [
        {"id": "guilin_monsoon_morning", "prompt": "Guilin China karst mountains summer rain morning, Li River misty, bamboo rafts, ethereal"},
        {"id": "munnar_monsoon_morning", "prompt": "Munnar India tea hills summer monsoon morning, lush green terraces, mist rolling, tropical"},
        {"id": "kauai_rain_morning", "prompt": "Kauai Hawaii Na Pali coast summer rain morning, waterfalls cascading, rainbow forming, dramatic"},
        {"id": "bali_rice_rain", "prompt": "Bali Ubud rice terraces summer rain morning, emerald green wet, mist rising, tropical paradise"},
    ],
    "morning_autumn_rain": [
        {"id": "suzhou_autumn_rain", "prompt": "Suzhou China gardens autumn rain morning, wet pavilions, golden leaves falling, reflections"},
        {"id": "shimla_rain_autumn", "prompt": "Shimla India hill station autumn rain morning, colonial architecture wet, misty pines, moody"},
        {"id": "pacific_northwest_fall_rain", "prompt": "Pacific Northwest forest autumn rain morning, giant redwoods wet, ferns, misty ethereal"},
        {"id": "nikko_japan_rain_fall", "prompt": "Nikko Japan temples autumn rain morning, red torii wet, golden maples falling, sacred"},
    ],
    "morning_winter_rain": [
        {"id": "shanghai_winter_rain", "prompt": "Shanghai old town winter rain morning, wet lanes, traditional houses, grey moody elegant"},
        {"id": "hong_kong_winter_rain_am", "prompt": "Hong Kong harbor winter rain morning, grey Victoria Harbor, city misty, atmospheric"},
        {"id": "big_sur_winter_rain", "prompt": "Big Sur California winter rain morning, dramatic coast wet, waves powerful, moody fog"},
        {"id": "vancouver_mountains_rain", "prompt": "Vancouver winter rain morning, North Shore mountains misty, harbor grey, city reflections"},
    ],
    "afternoon_spring_rain": [
        {"id": "wuxi_spring_rain", "prompt": "Wuxi China cherry blossoms spring rain afternoon, petals in puddles, lakeside pavilions wet"},
        {"id": "coorg_india_rain", "prompt": "Coorg India coffee plantations spring rain afternoon, lush green hills, mist, Western Ghats"},
        {"id": "napa_valley_rain_spring", "prompt": "Napa Valley spring rain afternoon, vineyards wet, mustard flowers, rolling hills misty"},
        {"id": "chiang_mai_rain_spring", "prompt": "Chiang Mai Thailand temples spring rain afternoon, golden spires wet, tropical gardens lush"},
    ],
    "afternoon_summer_rain": [
        {"id": "zhangjiajie_rain_summer", "prompt": "Zhangjiajie China summer rain afternoon, Avatar mountains in mist, waterfalls, dramatic clouds"},
        {"id": "kerala_monsoon_afternoon", "prompt": "Kerala India monsoon afternoon, backwaters rain, palm trees swaying, houseboats, tropical warm"},
        {"id": "costa_rica_rainforest", "prompt": "Costa Rica cloud forest summer rain afternoon, misty canopy, exotic birds, waterfalls"},
        {"id": "phuket_rain_afternoon", "prompt": "Phuket Thailand summer rain afternoon, beach grey, palm trees bending, dramatic tropical storm"},
    ],
    "afternoon_autumn_rain": [
        {"id": "jiuzhaigou_rain_autumn", "prompt": "Jiuzhaigou Valley China autumn rain afternoon, turquoise lakes, fall colors wet, misty mountains"},
        {"id": "ooty_rain_autumn", "prompt": "Ooty India hill station autumn rain afternoon, tea estates wet, eucalyptus misty, colonial charm"},
        {"id": "acadia_fall_rain", "prompt": "Acadia National Park Maine autumn rain afternoon, rocky coast wet, fall foliage, moody Atlantic"},
        {"id": "alps_austria_rain_fall", "prompt": "Austrian Alps autumn rain afternoon, golden larches wet, misty peaks, alpine meadows"},
    ],
    "afternoon_winter_rain": [
        {"id": "beijing_hutong_rain", "prompt": "Beijing hutong alleys winter rain afternoon, grey wet lanes, traditional courtyard homes, moody"},
        {"id": "kolkata_winter_rain", "prompt": "Kolkata India winter rain afternoon, colonial buildings wet, yellow taxis, Victoria Memorial misty"},
        {"id": "carmel_california_rain", "prompt": "Carmel California winter rain afternoon, cypress trees wet, dramatic coastline, grey Pacific"},
        {"id": "lucerne_rain_winter", "prompt": "Lucerne Switzerland winter rain afternoon, lake grey, Chapel Bridge wet, Alps hidden in mist"},
    ],
    "evening_spring_rain": [
        {"id": "chengdu_spring_rain_eve", "prompt": "Chengdu China spring rain evening, lanterns reflecting wet streets, traditional tea houses glowing"},
        {"id": "mumbai_spring_rain_eve", "prompt": "Mumbai spring rain evening, Marine Drive lights in puddles, Arabian Sea grey, city glowing"},
        {"id": "san_diego_rain_evening", "prompt": "San Diego California spring rain evening, harbor lights wet, Coronado Bridge, city reflections"},
        {"id": "hanoi_spring_rain", "prompt": "Hanoi Vietnam old quarter spring rain evening, lanterns wet, motorbikes, French colonial charm"},
    ],
    "evening_summer_rain": [
        {"id": "shanghai_rain_summer_eve", "prompt": "Shanghai Bund summer rain evening, Pudong lights in rain, neon reflections, romantic dramatic"},
        {"id": "goa_monsoon_evening", "prompt": "Goa India monsoon evening, beach rain, shacks lit warmly, palm trees swaying, Arabian Sea"},
        {"id": "honolulu_rain_evening", "prompt": "Honolulu Hawaii summer rain evening, Waikiki lights wet, Diamond Head misty, tropical warm"},
        {"id": "kuala_lumpur_rain_eve", "prompt": "Kuala Lumpur Petronas Towers summer rain evening, twin towers in rain, city lights reflecting"},
    ],
    "evening_autumn_rain": [
        {"id": "nanjing_autumn_rain", "prompt": "Nanjing China autumn rain evening, city wall wet, ginkgo trees golden in rain, lanterns"},
        {"id": "delhi_rain_autumn_eve", "prompt": "Delhi India autumn rain evening, India Gate lights in puddles, grand avenue wet, dramatic"},
        {"id": "portland_fall_rain_eve", "prompt": "Portland Oregon autumn rain evening, bridges lit, Willamette River reflections, fall colors wet"},
        {"id": "taipei_fall_rain_eve", "prompt": "Taipei Taiwan autumn rain evening, Taipei 101 in rain, night markets steamy, neon reflections"},
    ],
    "evening_winter_rain": [
        {"id": "hong_kong_winter_rain_eve", "prompt": "Hong Kong Central winter rain evening, skyscrapers in rain, neon reflecting wet streets"},
        {"id": "chennai_winter_rain", "prompt": "Chennai India winter rain evening, Marina Beach wet, city lights, Bay of Bengal grey moody"},
        {"id": "seattle_winter_rain_eve", "prompt": "Seattle winter rain evening, Space Needle in mist, Pike Place lights wet, harbor grey"},
        {"id": "macau_winter_rain", "prompt": "Macau winter rain evening, casinos lit in rain, Portuguese colonial wet, atmospheric"},
    ],
    "night_spring_rain": [
        {"id": "guangzhou_spring_rain_night", "prompt": "Guangzhou China Canton Tower spring rain night, neon reflections Pearl River, modern China wet"},
        {"id": "bangalore_rain_night_spring", "prompt": "Bangalore India spring rain night, tech city lights in puddles, MG Road wet, modern India"},
        {"id": "la_spring_rain_night", "prompt": "Los Angeles spring rain night, downtown lights reflecting, palm trees wet, rare dramatic"},
        {"id": "ho_chi_minh_rain_night", "prompt": "Ho Chi Minh City spring rain night, motorbikes wet streets, neon signs reflecting, bustling"},
    ],
    "night_summer_rain": [
        {"id": "shenzhen_rain_night", "prompt": "Shenzhen China summer rain night, futuristic skyline in rain, neon city wet, tech hub"},
        {"id": "hyderabad_rain_night", "prompt": "Hyderabad India summer rain night, Charminar lit in rain, old city wet streets, historic"},
        {"id": "vegas_monsoon_night", "prompt": "Las Vegas summer storm night, Strip neon in rain, dramatic lightning, desert storm rare"},
        {"id": "jakarta_rain_night", "prompt": "Jakarta Indonesia summer rain night, city lights in monsoon, skyscrapers wet, tropical urban"},
    ],
    "night_autumn_rain": [
        {"id": "xian_autumn_rain_night", "prompt": "Xi'an China autumn rain night, Bell Tower illuminated in rain, ancient walls wet, atmospheric"},
        {"id": "pune_rain_night_autumn", "prompt": "Pune India autumn rain night, Shaniwar Wada lit in rain, historic fort wet, moody"},
        {"id": "denver_fall_rain_night", "prompt": "Denver Colorado autumn rain night, downtown lights wet, Rockies hidden, urban mountain west"},
        {"id": "seoul_fall_rain_night", "prompt": "Seoul Myeongdong autumn rain night, neon shopping streets wet, K-pop aesthetic, vibrant"},
    ],
    "night_winter_rain": [
        {"id": "beijing_winter_rain_night", "prompt": "Beijing winter rain night, Tiananmen area lights in rain, grand avenues wet, monumental"},
        {"id": "ahmedabad_winter_rain", "prompt": "Ahmedabad India winter rain night, Sabarmati Riverfront lit, heritage city wet, peaceful"},
        {"id": "phoenix_winter_rain_night", "prompt": "Phoenix Arizona winter rain night, desert city lights wet, rare dramatic Sonoran rain"},
        {"id": "busan_winter_rain_night", "prompt": "Busan South Korea winter rain night, Haeundae beach city lights, harbor wet, moody coastal"},
    ],
    # CLOUDY - Asia, Nature, Mountains focused
    "morning_spring_cloudy": [
        {"id": "huangshan_cloudy_spring", "prompt": "Huangshan Yellow Mountains China spring cloudy morning, peaks in clouds, pine trees, mystical"},
        {"id": "ladakh_cloudy_spring", "prompt": "Ladakh India monastery spring cloudy morning, dramatic Himalayas in clouds, prayer flags"},
        {"id": "mendocino_cloudy_spring", "prompt": "Mendocino California coast spring cloudy morning, dramatic cliffs, wildflowers, moody Pacific"},
        {"id": "hallstatt_cloudy_spring", "prompt": "Hallstatt Austria spring cloudy morning, lake reflections muted, Alps in clouds, village charming"},
    ],
    "morning_summer_cloudy": [
        {"id": "mount_emei_cloudy", "prompt": "Mount Emei China summer cloudy morning, Buddhist temples in clouds, lush forests, mystical"},
        {"id": "coorg_cloudy_summer", "prompt": "Coorg India coffee hills summer cloudy morning, plantations moody, Western Ghats in mist"},
        {"id": "olympic_peninsula_cloudy", "prompt": "Olympic Peninsula Washington summer cloudy morning, rainforest moody, dramatic coast, moss-covered"},
        {"id": "faroe_islands_cloudy", "prompt": "Faroe Islands summer cloudy morning, dramatic green cliffs, grey Atlantic, waterfalls, moody"},
    ],
    "morning_autumn_cloudy": [
        {"id": "wuyuan_cloudy_autumn", "prompt": "Wuyuan China autumn cloudy morning, ancient villages, fall foliage muted, misty valleys"},
        {"id": "manali_cloudy_autumn", "prompt": "Manali India autumn cloudy morning, Himalayas in clouds, fall colors valley, apple orchards"},
        {"id": "smoky_mountains_cloudy", "prompt": "Smoky Mountains autumn cloudy morning, fall colors muted, misty ridges, Appalachian moody"},
        {"id": "bavarian_alps_cloudy_fall", "prompt": "Bavarian Alps autumn cloudy morning, Neuschwanstein in mist, fall colors, dramatic clouds"},
    ],
    "morning_winter_cloudy": [
        {"id": "jilin_rime_cloudy", "prompt": "Jilin China rime ice winter cloudy morning, frozen trees white, river mist, grey moody magical"},
        {"id": "gulmarg_cloudy_winter", "prompt": "Gulmarg Kashmir winter cloudy morning, snow slopes, Himalayas hidden, ski resort peaceful"},
        {"id": "tahoe_cloudy_winter", "prompt": "Lake Tahoe winter cloudy morning, snow-covered pines, lake grey, Sierra Nevada moody"},
        {"id": "dolomites_cloudy_winter", "prompt": "Dolomites Italy winter cloudy morning, dramatic peaks in clouds, snow villages, moody alpine"},
    ],
    "afternoon_spring_cloudy": [
        {"id": "zhouzhuang_cloudy_spring", "prompt": "Zhouzhuang China water town spring cloudy afternoon, canals reflective, traditional houses, soft light"},
        {"id": "rishikesh_cloudy_spring", "prompt": "Rishikesh India Ganges spring cloudy afternoon, temples on river, Himalayan foothills in clouds"},
        {"id": "point_reyes_cloudy", "prompt": "Point Reyes California spring cloudy afternoon, dramatic headlands, wildflowers, Pacific moody"},
        {"id": "lake_bled_cloudy_spring", "prompt": "Lake Bled Slovenia spring cloudy afternoon, island church, Julian Alps in clouds, soft romantic"},
    ],
    "afternoon_summer_cloudy": [
        {"id": "yangshuo_cloudy_summer", "prompt": "Yangshuo China karst peaks summer cloudy afternoon, Li River grey, bamboo rafts, mystical"},
        {"id": "kodaikanal_cloudy", "prompt": "Kodaikanal India hills summer cloudy afternoon, misty pine forests, dramatic clouds, colonial"},
        {"id": "na_pali_cloudy", "prompt": "Na Pali Coast Hawaii summer cloudy afternoon, dramatic cliffs, waterfalls, moody Pacific"},
        {"id": "lofoten_cloudy_summer", "prompt": "Lofoten Islands Norway summer cloudy afternoon, dramatic peaks, fishing villages, moody Arctic"},
    ],
    "afternoon_autumn_cloudy": [
        {"id": "huzhou_cloudy_autumn", "prompt": "Huzhou China bamboo sea autumn cloudy afternoon, golden bamboo, misty forests, traditional pavilions"},
        {"id": "mussoorie_cloudy_fall", "prompt": "Mussoorie India autumn cloudy afternoon, hill station misty, fall colors, Himalayan views hidden"},
        {"id": "adirondacks_cloudy_fall", "prompt": "Adirondacks New York autumn cloudy afternoon, fall foliage muted, lakes grey, moody wilderness"},
        {"id": "tyrol_cloudy_autumn", "prompt": "Tyrol Austria autumn cloudy afternoon, golden larches, peaks in clouds, alpine villages cozy"},
    ],
    "afternoon_winter_cloudy": [
        {"id": "wuzhen_cloudy_winter", "prompt": "Wuzhen China water town winter cloudy afternoon, grey canals, traditional houses, lanterns soft"},
        {"id": "shimla_cloudy_winter", "prompt": "Shimla India winter cloudy afternoon, colonial buildings, Himalayas hidden, hill station moody"},
        {"id": "yosemite_cloudy_winter", "prompt": "Yosemite winter cloudy afternoon, granite walls in clouds, snow dramatic, waterfalls frozen"},
        {"id": "grindelwald_cloudy_winter", "prompt": "Grindelwald Switzerland winter cloudy afternoon, Eiger in clouds, snow village, Alps dramatic"},
    ],
    "evening_spring_cloudy": [
        {"id": "lijiang_cloudy_spring_eve", "prompt": "Lijiang China old town spring cloudy evening, dramatic clouds, lanterns lighting, traditional rooftops"},
        {"id": "udaipur_cloudy_spring", "prompt": "Udaipur India spring cloudy evening, Lake Palace dramatic clouds, golden light breaking through"},
        {"id": "highway_one_cloudy_sunset", "prompt": "Highway One California spring cloudy sunset, dramatic coast, golden light through clouds"},
        {"id": "cinque_terre_cloudy_eve", "prompt": "Cinque Terre Italy spring cloudy evening, dramatic Mediterranean clouds, villages glowing warm"},
    ],
    "evening_summer_cloudy": [
        {"id": "xiamen_cloudy_sunset", "prompt": "Xiamen China summer cloudy sunset, dramatic clouds over harbor, Gulangyu Island golden"},
        {"id": "andaman_cloudy_sunset", "prompt": "Andaman Islands India summer cloudy sunset, dramatic tropical clouds, beach golden, paradise"},
        {"id": "monterey_cloudy_sunset", "prompt": "Monterey Bay California summer cloudy sunset, dramatic clouds, cypress trees silhouette"},
        {"id": "amalfi_dramatic_clouds", "prompt": "Amalfi Coast summer cloudy sunset, dramatic Mediterranean sky, villages clinging to cliffs golden"},
    ],
    "evening_autumn_cloudy": [
        {"id": "chongqing_cloudy_fall", "prompt": "Chongqing China autumn cloudy evening, dramatic skyline through clouds, Yangtze River golden"},
        {"id": "jaipur_cloudy_autumn_eve", "prompt": "Jaipur India autumn cloudy evening, dramatic clouds over Pink City, palace golden light"},
        {"id": "sf_bay_cloudy_fall", "prompt": "San Francisco Bay autumn cloudy evening, Golden Gate dramatic clouds, city lights emerging"},
        {"id": "dubrovnik_cloudy_fall", "prompt": "Dubrovnik Croatia autumn cloudy evening, dramatic Adriatic clouds, old town walls golden"},
    ],
    "evening_winter_cloudy": [
        {"id": "hong_kong_cloudy_winter_eve", "prompt": "Hong Kong winter cloudy evening, dramatic Victoria Harbor, city lights through clouds"},
        {"id": "agra_cloudy_winter_eve", "prompt": "Agra India Taj Mahal winter cloudy evening, dramatic clouds, marble glowing soft pink"},
        {"id": "seattle_dramatic_winter", "prompt": "Seattle winter cloudy evening, dramatic Puget Sound clouds, Space Needle lights"},
        {"id": "edinburgh_cloudy_winter_eve", "prompt": "Edinburgh Scotland winter cloudy evening, castle dramatic against clouds, city lights"},
    ],
    "night_spring_cloudy": [
        {"id": "chengdu_cloudy_spring_night", "prompt": "Chengdu China spring cloudy night, city lights glowing through clouds, modern Sichuan"},
        {"id": "mumbai_cloudy_spring_night", "prompt": "Mumbai India spring cloudy night, Marine Drive lights diffused, Gateway of India glowing"},
        {"id": "la_downtown_cloudy", "prompt": "Los Angeles downtown spring cloudy night, city lights glowing through marine layer, dramatic"},
        {"id": "tokyo_tower_cloudy", "prompt": "Tokyo Tower spring cloudy night, red tower lights through clouds, city glowing below"},
    ],
    "night_summer_cloudy": [
        {"id": "pudong_cloudy_summer", "prompt": "Shanghai Pudong summer cloudy night, skyscrapers in low clouds, dramatic futuristic"},
        {"id": "chennai_cloudy_summer", "prompt": "Chennai India summer cloudy night, Marina Beach lights, Bay of Bengal clouds dramatic"},
        {"id": "manhattan_cloudy_summer", "prompt": "Manhattan summer cloudy night, Empire State in clouds, city lights glowing atmospheric"},
        {"id": "taipei_101_cloudy", "prompt": "Taipei 101 Taiwan summer cloudy night, tower piercing clouds, city lights below dramatic"},
    ],
    "night_autumn_cloudy": [
        {"id": "wuhan_cloudy_fall_night", "prompt": "Wuhan China autumn cloudy night, Yellow Crane Tower lit, Yangtze River, clouds dramatic"},
        {"id": "delhi_cloudy_autumn_night", "prompt": "Delhi India autumn cloudy night, India Gate illuminated, dramatic clouds, grand avenue"},
        {"id": "chicago_cloudy_dramatic", "prompt": "Chicago autumn cloudy night, Willis Tower in low clouds, lake dark, city glowing moody"},
        {"id": "osaka_castle_cloudy", "prompt": "Osaka Castle autumn cloudy night, illuminated through clouds, fall trees lit, dramatic"},
    ],
    "night_winter_cloudy": [
        {"id": "beijing_forbidden_cloudy", "prompt": "Beijing Forbidden City winter cloudy night, ancient walls lit, dramatic low clouds, majestic"},
        {"id": "varanasi_cloudy_winter", "prompt": "Varanasi India winter cloudy night, Ganges ghats lights, ceremony glowing through mist"},
        {"id": "vegas_winter_cloudy", "prompt": "Las Vegas winter cloudy night, Strip lights glowing through rare clouds, dramatic desert"},
        {"id": "paris_monuments_cloudy", "prompt": "Paris winter cloudy night, Eiffel Tower lights diffused, romantic moody City of Light"},
    ],
}


def get_current_counts():
    """Count existing images per category"""
    counts = {}
    base_dir = Path("cb_images")
    
    if not base_dir.exists():
        return counts
    
    for folder in base_dir.iterdir():
        if folder.is_dir() and folder.name != "generation_report.json":
            count = len(list(folder.glob("*.png")))
            counts[folder.name] = count
    
    return counts


def calculate_additions(images_per_scenario: int, scene_set: str):
    """Calculate total new images needed"""
    scenes = ORIGINAL_SCENES if scene_set == "original" else DIVERSE_SCENES
    total_scenarios = len(scenes)
    total_new_images = total_scenarios * images_per_scenario
    return total_scenarios, total_new_images


def main():
    print("=" * 60)
    print("CB Images - Generate Additional Images")
    print("=" * 60)
    print()
    
    # Show current counts
    print("Current image counts:")
    counts = get_current_counts()
    total_existing = 0
    for folder, count in sorted(counts.items()):
        print(f"  {folder}: {count}")
        total_existing += count
    print(f"\n  Total existing: {total_existing}")
    print()
    
    # Choose scene set
    print("Which scene set do you want to generate?")
    print("  1. Original (European, Americas, Classic)")
    print("  2. Diverse (Asia, India, China, Beaches, Mountains)")
    print("  3. Both (All scenes)")
    print()
    
    try:
        choice = input("Enter choice (1/2/3): ").strip()
    except:
        print("Cancelled.")
        return
    
    if choice == "1":
        scene_set = "original"
        scenes = ORIGINAL_SCENES
    elif choice == "2":
        scene_set = "diverse"
        scenes = DIVERSE_SCENES
    elif choice == "3":
        scene_set = "both"
        scenes = {**ORIGINAL_SCENES}
        for key, value in DIVERSE_SCENES.items():
            if key in scenes:
                scenes[key] = scenes[key] + value
            else:
                scenes[key] = value
    else:
        print("Invalid choice. Exiting.")
        return
    
    # Get number of images per scenario
    try:
        num_images = int(input("\nHow many images per scenario? (1-4): "))
    except ValueError:
        print("Invalid number. Exiting.")
        return
    
    if num_images < 1 or num_images > 4:
        print("Please enter a number between 1 and 4. Exiting.")
        return
    
    # Calculate
    total_scenarios = len(scenes)
    total_new = total_scenarios * num_images
    
    print()
    print("=" * 60)
    print("CALCULATION SUMMARY")
    print("=" * 60)
    print(f"  Scene set: {scene_set.upper()}")
    print(f"  Scenarios: {total_scenarios}")
    print(f"  Images per scenario: {num_images}")
    print(f"  Total NEW images to generate: {total_new}")
    print()
    print(f"  Existing images: {total_existing}")
    print(f"  After generation: {total_existing + total_new}")
    print()
    print("  API Limit: ~70 images/day per project")
    print(f"  Estimated time: {(total_new // 70) + 1} day(s)")
    print("=" * 60)
    print()
    
    # Ask for confirmation
    confirm = input("Proceed with generation? (yes/no): ").strip().lower()
    
    if confirm not in ["yes", "y"]:
        print("Generation cancelled.")
        return
    
    print()
    print("Starting generation...")
    print()
    
    # Generate images
    generated = 0
    failed = 0
    skipped = 0
    
    for scene_key, scene_list in scenes.items():
        # Parse the key to get time, season, weather
        parts = scene_key.split("_")
        time_of_day = parts[0]
        season = parts[1]
        weather = parts[2] if len(parts) > 2 else "clear"
        
        # Determine output folder
        if weather == "clear":
            output_folder = OUTPUT_DIR / time_of_day
        else:
            output_folder = OUTPUT_DIR / f"{time_of_day}_{weather}"
        
        output_folder.mkdir(parents=True, exist_ok=True)
        
        # Generate only the requested number of images
        for scene in scene_list[:num_images]:
            scene_id = scene["id"]
            scene_prompt = scene["prompt"]
            
            # Build filename
            filename = f"{time_of_day}_{season}_{scene_id}.png"
            output_path = output_folder / filename
            
            # Skip if exists
            if output_path.exists():
                print(f"  Skipping (exists): {filename}")
                skipped += 1
                continue
            
            # Build full prompt
            time_data = TIMES_OF_DAY.get(time_of_day, {})
            season_data = SEASONS.get(season, {})
            
            full_prompt = f"""
{GLOBAL_VISUAL_DNA}

TIME OF DAY: {time_of_day}
{time_data.get('description', '')}
Lighting: {time_data.get('lighting', '')}
Sky: {time_data.get('sky', '')}

SEASON: {season}
{season_data.get('description', '')}
Atmosphere: {season_data.get('atmosphere', '')}

SCENE: {scene_prompt}

{COMPOSITION_RULE}

CRITICAL REQUIREMENTS:
- ONE SINGLE CONTINUOUS LANDSCAPE IMAGE that fills the ENTIRE frame edge-to-edge
- NO collages, NO grids, NO stacked images, NO duplicate images
- NO white borders, NO black borders, NO letterboxing, NO margins
- NO 2x1, 2x2, or any multi-panel layouts
- Image MUST fill the full canvas with NO empty space on any side
- NO text, watermarks, or overlays
- Pure seamless landscape photography only
"""
            
            print(f"  Generating: {filename}")
            
            success = generate_image(full_prompt, output_path)
            
            if success:
                generated += 1
                print(f"    ✓ Success ({generated} generated, {skipped} skipped)")
            else:
                failed += 1
                print(f"    ✗ Failed")
    
    print()
    print("=" * 60)
    print(f"COMPLETE: {generated} generated, {skipped} skipped, {failed} failed")
    print("=" * 60)


if __name__ == "__main__":
    main()
