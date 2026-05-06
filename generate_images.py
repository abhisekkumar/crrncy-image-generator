import os
import re
import json
import time
import shutil
from pathlib import Path

import pandas as pd
from PIL import Image
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

CSV_PATH = Path("products.csv")

BASE_OUTPUT_DIR = Path("output")
TEMP_DIR = BASE_OUTPUT_DIR / "_temp"
FINAL_DIR = BASE_OUTPUT_DIR / "final"
REVIEW_DIR = BASE_OUTPUT_DIR / "needs_review"
FAILED_DIR = BASE_OUTPUT_DIR / "failed"

# Options:
# "gemini_image" = Nano Banana / Gemini image models via generate_content()
# "imagen" = Imagen models via generate_images()
GENERATION_PROVIDER = "gemini_image"

# Nano Banana 2
GENERATION_MODEL = "gemini-3.1-flash-image-preview"

# Fallback options:
# GENERATION_MODEL = "gemini-2.5-flash-image"
# GENERATION_PROVIDER = "imagen"
# GENERATION_MODEL = "imagen-4.0-generate-001"

VERIFY_MODEL = "gemini-2.5-flash"

IMAGE_ASPECT_RATIO = "1:1"
IMAGE_SIZE = "1K"

MAX_REGEN_ATTEMPTS = 3
VERIFY_THRESHOLD = 0.75
SLEEP_BETWEEN_PRODUCTS = 1.0
SLEEP_BETWEEN_ATTEMPTS = 1.5


# =========================
# HELPERS
# =========================

def safe_filename(text: str, max_len: int = 120) -> str:
    text = str(text).lower().strip()
    text = text.replace("&", "and")
    text = re.sub(r"[^\w\s\-+]", "", text)
    text = re.sub(r"\s+", "_", text)
    text = re.sub(r"_+", "_", text)
    return text[:max_len].strip("_")


def normalize_json_response(text: str) -> dict:
    text = text.strip().replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            return json.loads(text[start:end + 1])
        raise


def category_background(category: str) -> str:
    category = str(category).lower().strip()

    mapping = {
        "sunscreen": "soft warm ivory-to-pale-yellow luxury gradient background",
        "serum": "soft champagne and cream luxury gradient background",
        "treatment": "soft champagne and pearl gradient background",
        "moisturizer": "soft beige, cream, and pearl gradient background",
        "body": "warm cream, beige, and soft sunlit gradient background",
        "body_care": "warm cream, beige, and soft sunlit gradient background",
        "cleanser": "clean white to pale blue gradient background",
        "toner": "clean white to pale blue gradient background",
        "lip": "soft blush pink to ivory gradient background",
        "lip_care": "soft blush pink to ivory gradient background",
        "makeup": "soft blush pink to ivory premium studio gradient background",
        "haircare": "soft pearl gray to champagne gradient background",
        "eye": "soft ivory and pale lavender gradient background",
        "eye_care": "soft ivory and pale lavender gradient background",
        "mask": "soft cream and spa-like pastel gradient background",
    }

    return mapping.get(category, "clean white and soft cream gradient background")


def build_prompt(
    product_id: str,
    brand: str,
    product: str,
    category: str,
    attempt: int = 1,
) -> str:
    bg = category_background(category)

    correction = ""
    if attempt > 1:
        correction = f"""
IMPORTANT CORRECTION:
The previous generated image may not have matched the exact product.

Generate ONLY this product:
Brand: {brand}
Product: {product}
Category: {category}

Make the packaging visually consistent with this brand and product.
Do not invent another brand.
Do not create a product grid.
Do not add captions outside the package.
"""

    return f"""
Generate a professional standalone HD product photo of {brand} {product}.

Internal product ID: {product_id}
Category: {category}

Style:
Premium beauty/skincare e-commerce product photography.
Sephora / Ulta / luxury studio product image style.
Clean, realistic, premium, modern.

Composition:
Single product only.
Product centered as the hero.
Slight 3/4 angle.
Clear front-facing packaging.
No people.
No hands.
No props.
No extra products.
No product grid.
No captions, numbers, labels, or text outside the product packaging.

Background:
{bg}.
Minimal, clean, premium.

Lighting:
Soft diffused studio lighting.
Soft realistic shadow beneath product.
Subtle reflection optional.
Sharp focus.
High-resolution commercial product image.

Output:
Square 1:1 image.
E-commerce ready.

Important:
Do NOT place the product ID as visible text in the image.
The product ID is only for file naming and tracking.
{correction}
"""


# =========================
# IMAGE GENERATION
# =========================

def generate_image_with_gemini_image(prompt: str, output_path: Path) -> bool:
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
            return False

        output_path.parent.mkdir(parents=True, exist_ok=True)

        for part in response.candidates[0].content.parts:
            inline_data = getattr(part, "inline_data", None)

            if inline_data and inline_data.data:
                with open(output_path, "wb") as f:
                    f.write(inline_data.data)
                return True

        return False

    except Exception as e:
        print(f"\nGemini image generation error: {e}")
        return False


def generate_image_with_imagen(prompt: str, output_path: Path) -> bool:
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
            return False

        image_bytes = response.generated_images[0].image.image_bytes

        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "wb") as f:
            f.write(image_bytes)

        return True

    except Exception as e:
        print(f"\nImagen generation error: {e}")
        return False


def generate_image(prompt: str, output_path: Path) -> bool:
    if GENERATION_PROVIDER == "gemini_image":
        return generate_image_with_gemini_image(prompt, output_path)

    if GENERATION_PROVIDER == "imagen":
        return generate_image_with_imagen(prompt, output_path)

    raise ValueError(f"Unsupported GENERATION_PROVIDER: {GENERATION_PROVIDER}")


# =========================
# IMAGE VERIFICATION
# =========================

def verify_image(
    image_path: Path,
    product_id: str,
    brand: str,
    product: str,
    category: str,
) -> dict:
    img = Image.open(image_path)

    prompt = f"""
You are a strict visual QA inspector for generated beauty product images.

Expected product:
Product ID: {product_id}
Brand: {brand}
Product: {product}
Category: {category}

Check whether the image is relevant for a product catalog.

Return ONLY valid JSON in this exact schema:
{{
  "product_id": "{product_id}",
  "is_relevant": true,
  "brand_match": true,
  "product_match": true,
  "category_match": true,
  "single_product": true,
  "no_external_captions": true,
  "confidence": 0.0,
  "issues": []
}}

Rules:
- brand_match should be false if the brand label is missing, misspelled, or clearly wrong.
- product_match should be false if the visible product name is missing, wrong, or clearly a different item.
- category_match should be false if the product form is wrong, for example cleanser when expected sunscreen.
- single_product should be false if there is a grid, collage, multiple products, or comparison layout.
- no_external_captions should be false if there are labels, index numbers, or text outside the product packaging.
- Be strict but practical.
- If exact small label text is not fully readable but the brand/product/category strongly match, confidence can still be high.
"""

    try:
        response = client.models.generate_content(
            model=VERIFY_MODEL,
            contents=[prompt, img],
        )

        result = normalize_json_response(response.text)

        defaults = {
            "product_id": product_id,
            "is_relevant": False,
            "brand_match": False,
            "product_match": False,
            "category_match": False,
            "single_product": False,
            "no_external_captions": False,
            "confidence": 0.0,
            "issues": [],
        }

        for key, value in defaults.items():
            result.setdefault(key, value)

        return result

    except Exception as e:
        return {
            "product_id": product_id,
            "is_relevant": False,
            "brand_match": False,
            "product_match": False,
            "category_match": False,
            "single_product": False,
            "no_external_captions": False,
            "confidence": 0.0,
            "issues": [f"Verification error: {str(e)}"],
        }


def passes_verification(result: dict) -> bool:
    confidence = float(result.get("confidence", 0.0))

    return (
        result.get("is_relevant") is True
        and result.get("brand_match") is True
        and result.get("category_match") is True
        and result.get("single_product") is True
        and result.get("no_external_captions") is True
        and confidence >= VERIFY_THRESHOLD
    )


def make_paths(product_id: str, brand: str, product: str, category: str):
    filename = f"{product_id}_{safe_filename(brand)}_{safe_filename(product)}.png"
    category_folder = safe_filename(category)

    temp_path = TEMP_DIR / category_folder / filename
    final_path = FINAL_DIR / category_folder / filename
    review_path = REVIEW_DIR / category_folder / filename
    failed_path = FAILED_DIR / category_folder / filename

    return temp_path, final_path, review_path, failed_path


# =========================
# MAIN
# =========================

def main():
    if not CSV_PATH.exists():
        raise FileNotFoundError("products.csv not found.")

    df = pd.read_csv(CSV_PATH)

    required = {"product_id", "brand", "product", "category"}
    missing = required - set(df.columns)

    if missing:
        raise ValueError(f"products.csv missing columns: {missing}")

    BASE_OUTPUT_DIR.mkdir(exist_ok=True)
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    FAILED_DIR.mkdir(parents=True, exist_ok=True)

    report = []

    print(f"\nUsing generation provider: {GENERATION_PROVIDER}")
    print(f"Using generation model: {GENERATION_MODEL}")
    print(f"Using verification model: {VERIFY_MODEL}\n")

    for row_number, row in tqdm(df.iterrows(), total=len(df)):
        product_id = str(row["product_id"]).strip()
        brand = str(row["brand"]).strip()
        product = str(row["product"]).strip()
        category = str(row["category"]).strip()

        temp_path, final_path, review_path, failed_path = make_paths(
            product_id,
            brand,
            product,
            category,
        )

        if final_path.exists():
            report.append({
                "product_id": product_id,
                "brand": brand,
                "product": product,
                "category": category,
                "status": "skipped_existing_final",
                "confidence": None,
                "issues": "",
                "path": str(final_path),
            })
            continue

        accepted = False
        best_result = None
        best_temp_path = None

        for attempt in range(1, MAX_REGEN_ATTEMPTS + 1):
            prompt = build_prompt(
                product_id,
                brand,
                product,
                category,
                attempt,
            )

            attempt_temp_path = temp_path.with_name(
                temp_path.stem + f"_attempt_{attempt}.png"
            )

            success = generate_image(prompt, attempt_temp_path)

            if not success:
                best_result = {
                    "product_id": product_id,
                    "confidence": 0.0,
                    "issues": ["generation_failed"],
                }
                time.sleep(SLEEP_BETWEEN_ATTEMPTS)
                continue

            result = verify_image(
                attempt_temp_path,
                product_id,
                brand,
                product,
                category,
            )

            best_result = result
            best_temp_path = attempt_temp_path

            confidence = float(result.get("confidence", 0.0))

            print(
                f"\nQA {product_id}: {brand} - {product} | "
                f"attempt {attempt} | confidence={confidence} | "
                f"pass={passes_verification(result)}"
            )

            if passes_verification(result):
                final_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(attempt_temp_path), str(final_path))
                accepted = True
                break

            time.sleep(SLEEP_BETWEEN_ATTEMPTS)

        if accepted:
            report.append({
                "product_id": product_id,
                "brand": brand,
                "product": product,
                "category": category,
                "status": "final",
                "confidence": best_result.get("confidence"),
                "issues": json.dumps(best_result.get("issues", []), ensure_ascii=False),
                "path": str(final_path),
            })
        else:
            if best_temp_path and best_temp_path.exists():
                review_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(best_temp_path), str(review_path))
                output_path = review_path
                status = "needs_review"
            else:
                output_path = failed_path
                status = "failed"

            report.append({
                "product_id": product_id,
                "brand": brand,
                "product": product,
                "category": category,
                "status": status,
                "confidence": best_result.get("confidence") if best_result else 0,
                "issues": json.dumps(
                    best_result.get("issues", []),
                    ensure_ascii=False,
                ) if best_result else "",
                "path": str(output_path),
            })

        pd.DataFrame(report).to_csv(
            BASE_OUTPUT_DIR / "generation_report.csv",
            index=False,
        )

        time.sleep(SLEEP_BETWEEN_PRODUCTS)

    print("\nDone.")
    print(f"Final images: {FINAL_DIR.resolve()}")
    print(f"Needs review: {REVIEW_DIR.resolve()}")
    print(f"Report: {(BASE_OUTPUT_DIR / 'generation_report.csv').resolve()}")


if __name__ == "__main__":
    main()