# CRRNCY Image Generator

Automated product image generator for the CRRNCY beauty & skincare catalog. Reads a CSV of products, generates professional e-commerce-ready product photos using Google's Gemini / Imagen models, and runs automated visual QA to verify each image before accepting it.

## Features

- **Batch generation** — processes an entire product catalog from a single CSV
- **Dual provider support** — Gemini image models (`gemini-3.1-flash-image-preview`, `gemini-2.5-flash-image`) and Imagen (`imagen-4.0-generate-001`)
- **Automated visual QA** — every generated image is verified by a separate Gemini model that checks brand match, product match, category match, single-product composition, and absence of external captions
- **Auto-retry** — images that fail QA are regenerated up to 3 times with corrective prompts
- **Smart sorting** — accepted images go to `output/final/`, borderline images to `output/needs_review/`, and failures to `output/failed/`
- **Incremental runs** — already-accepted images are skipped on re-run
- **Generation report** — a CSV report is written after every product so progress is never lost

## Prerequisites

- Python 3.10+
- A [Google AI Studio](https://aistudio.google.com/) API key with access to Gemini / Imagen models

## Setup

```bash
# Clone the repository
git clone https://github.com/abhisekkumar/crrncy-image-generator.git
cd crrncy-image-generator

# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # macOS / Linux
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Configure your API key
cp .env.example .env
# Open .env and replace the placeholder with your real Gemini API key
```

## Usage

```bash
python generate_images.py
```

The script reads `products.csv` and generates one image per product row.

### Configuration

All tunables live at the top of `generate_images.py`:

| Variable | Default | Description |
|---|---|---|
| `GENERATION_PROVIDER` | `"gemini_image"` | `"gemini_image"` or `"imagen"` |
| `GENERATION_MODEL` | `"gemini-3.1-flash-image-preview"` | Model name for image generation |
| `VERIFY_MODEL` | `"gemini-2.5-flash"` | Model name for visual QA verification |
| `IMAGE_ASPECT_RATIO` | `"1:1"` | Aspect ratio for generated images |
| `MAX_REGEN_ATTEMPTS` | `3` | Max retries per product on QA failure |
| `VERIFY_THRESHOLD` | `0.75` | Minimum confidence score to accept |
| `SLEEP_BETWEEN_PRODUCTS` | `1.0` | Seconds between products (rate limiting) |
| `SLEEP_BETWEEN_ATTEMPTS` | `1.5` | Seconds between retry attempts |

### Product CSV Format

`products.csv` must contain these columns:

```
product_id,brand,product,category
CRRNCY-PRD-001,AmLactin,Rough & Bumpy Skin Daily Smoothing Cream,body
```

Supported categories: `sunscreen`, `serum`, `treatment`, `moisturizer`, `body`, `body_care`, `cleanser`, `toner`, `lip`, `lip_care`, `makeup`, `haircare`, `eye`, `eye_care`, `mask`.

Each category maps to a curated background gradient for a consistent, premium look.

## Output Structure

```
output/
├── final/              # ✅ Accepted images (passed QA)
│   ├── body/
│   ├── cleanser/
│   ├── serum/
│   └── ...
├── needs_review/       # ⚠️  Best attempt saved but did not pass QA
├── failed/             # ❌ Generation failed entirely
├── _temp/              # 🔄 Temporary files during generation
└── generation_report.csv   # 📊 Full QA report for all products
```

Each image is named:
```
{product_id}_{brand}_{product}.png
```

Example: `CRRNCY-PRD-001_amlactin_rough_bumpy_skin_daily_smoothing_cream.png`

## How It Works

```
┌─────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ products.csv │───▶│ Prompt Builder   │───▶│ Image Generator │
└─────────────┘    │ (category-aware  │    │ (Gemini/Imagen) │
                   │  backgrounds)    │    └────────┬────────┘
                   └──────────────────┘             │
                                                    ▼
                   ┌──────────────────┐    ┌─────────────────┐
                   │ Sort & Save      │◀───│ Visual QA       │
                   │ (final/review/   │    │ (Gemini verify) │
                   │  failed)         │    └─────────────────┘
                   └──────────────────┘
```

1. **Read** the product catalog from CSV
2. **Build** a detailed studio-photography prompt per product (with category-specific background)
3. **Generate** the image via the configured provider
4. **Verify** the image with a separate Gemini model acting as a strict QA inspector
5. **Accept or retry** — if QA passes, save to `final/`; otherwise retry with corrective prompts up to `MAX_REGEN_ATTEMPTS`
6. **Sort** the best attempt into `final/`, `needs_review/`, or `failed/`
7. **Report** results incrementally to `generation_report.csv`

## License

Private — all rights reserved.
