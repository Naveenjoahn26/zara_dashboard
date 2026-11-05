import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SAMPLE_DATA_PATH = BASE_DIR / "sample_sales_data.csv"

CATEGORIES = {
    "Outerwear": [
        ("BASIC PUFFER JACKET", 49.99, 129.99),
        ("FAUX LEATHER BOMBER JACKET", 79.99, 159.99),
        ("WOOL BLEND OVERCOAT", 129.99, 249.99),
        ("DOUBLE FACED SHEARLING JACKET", 99.99, 189.99),
        ("WATER-REPELLENT TRENCH COAT", 89.99, 179.99),
        ("QUILLED LIGHTWEIGHT VEST", 39.99, 79.99),
    ],
    "Suits & Blazers": [
        ("SLIM FIT SUIT JACKET", 119.00, 199.00),
        ("TUXEDO JACKET WITH SATIN LAPEL", 149.00, 229.00),
        ("SUIT JACKET IN 100% LINEN", 139.00, 189.00),
        ("STRUCTURED CHECK BLAZER", 109.00, 169.00),
        ("STRETCH PERFORMANCE BLAZER", 99.00, 159.00),
    ],
    "Knitwear": [
        ("100% MERINO WOOL SWEATER", 49.90, 89.90),
        ("CHUNKY CABLE KNIT SWEATER", 59.90, 99.90),
        ("FINE KNIT TURTLENECK", 39.90, 69.90),
        ("CASHMERE BLEND CARDIGAN", 79.90, 149.90),
        ("OVERSIZED WAFFLE CREWNECK", 45.90, 75.90),
    ],
    "Shirts & Tops": [
        ("OXFORD COTTON SHIRT", 35.90, 65.90),
        ("REGULAR FIT LINEN SHIRT", 45.90, 79.90),
        ("HEAVYWEIGHT BASIC TEE", 19.90, 35.90),
        ("PRINTED VISCOSE RESORT SHIRT", 39.90, 69.90),
        ("SLIM FIT STRETCH POPLIN SHIRT", 39.90, 69.90),
    ],
    "Denim & Pants": [
        ("STRAIGHT FIT VINTAGE JEANS", 49.90, 89.90),
        ("SLIM FIT WASHED DENIM", 49.90, 79.90),
        ("WIDE LEG PLEATED TROUSERS", 59.90, 99.90),
        ("RELAXED FIT CARGO PANTS", 49.90, 85.90),
        ("CROPPED CHINO TROUSERS", 39.90, 69.90),
    ],
    "Footwear": [
        ("LEATHER CHELSEA BOOTS", 89.90, 169.00),
        ("MINIMALIST LEATHER SNEAKERS", 69.90, 119.00),
        ("SUEDE LOAFERS WITH BUCKLE", 79.90, 139.00),
        ("CHUNKY DERBY SHOES", 79.90, 149.00),
        ("RUNNING STYLE TRAINERS", 59.90, 99.90),
    ],
    "Accessories": [
        ("LEATHER CROSSBODY BAG", 49.90, 99.90),
        ("100% CASHMERE SCARF", 39.90, 79.90),
        ("WOVEN LEATHER BELT", 29.90, 49.90),
        ("POLARIZED ACETATE SUNGLASSES", 39.90, 69.90),
        ("STRUCTURED BACKPACK", 59.90, 119.00),
    ]
}

SECTIONS = ["MAN", "WOMAN", "KIDS"]
POSITIONS = ["Aisle", "End-cap", "Front of Store"]
PROMOTIONS = ["Yes", "No"]
SEASONAL = ["Yes", "No"]


def generate_sales_dataset(num_records: int = 3000, output_path: Path = SAMPLE_DATA_PATH) -> Path:
    """Generate a realistic sales dataset spanning 15 months (Jan 2023 - Mar 2024)."""
    random.seed(42)

    start_date = datetime(2023, 1, 1, 9, 0, 0)
    total_days = 455  # ~15 months

    records = []
    product_id_counter = 100000

    categories_list = list(CATEGORIES.keys())

    # Generate transactions
    for i in range(num_records):
        product_id_counter += 1
        product_id = product_id_counter

        # Pick category and product
        cat = random.choices(
            categories_list,
            weights=[25, 18, 18, 15, 12, 8, 4],  # Outerwear & Suits popular in Zara
            k=1
        )[0]
        prod_name, min_p, max_p = random.choice(CATEGORIES[cat])

        # Random date with holiday/season weighting
        day_offset = random.randint(0, total_days)
        base_dt = start_date + timedelta(days=day_offset)

        # Q4 / Black Friday / Holiday boost (Nov - Dec)
        is_holiday = base_dt.month in [11, 12]
        is_summer_sale = base_dt.month in [6, 7]

        # Price and quantity
        price = round(random.uniform(min_p, max_p), 2)

        # Quantity/volume
        base_vol = random.randint(10, 80)
        if is_holiday:
            base_vol = int(base_vol * random.uniform(1.5, 2.8))
        elif is_summer_sale:
            base_vol = int(base_vol * random.uniform(1.2, 1.9))

        volume = base_vol
        hour = random.randint(8, 21)
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        dt = base_dt.replace(hour=hour, minute=minute, second=second)

        promotion = random.choices(PROMOTIONS, weights=[0.35, 0.65])[0]
        if is_holiday or is_summer_sale:
            promotion = "Yes"

        seasonal = "Yes" if cat in ["Outerwear", "Knitwear"] and base_dt.month in [10, 11, 12, 1, 2] else "No"
        position = random.choice(POSITIONS)
        section = random.choices(SECTIONS, weights=[0.45, 0.45, 0.10])[0]

        records.append({
            "Product ID": product_id,
            "Product Position": position,
            "Promotion": promotion,
            "Product Category": cat,
            "Seasonal": seasonal,
            "Sales Volume": volume,
            "brand": "Zara",
            "url": f"https://www.zara.com/us/en/{prod_name.lower().replace(' ', '-')}-p{product_id}.html",
            "sku": f"{product_id}-001-01",
            "name": prod_name,
            "description": f"High quality {cat.lower()} designed with premium materials.",
            "price": price,
            "currency": "USD",
            "scraped_at": dt.strftime("%Y-%m-%d %H:%M:%S"),
            "terms": cat.lower(),
            "section": section
        })

    # Sort chronologically
    records.sort(key=lambda x: x["scraped_at"])

    # Write to CSV with semicolon separator (matching Zara format)
    fieldnames = [
        "Product ID", "Product Position", "Promotion", "Product Category",
        "Seasonal", "Sales Volume", "brand", "url", "sku", "name",
        "description", "price", "currency", "scraped_at", "terms", "section"
    ]

    with open(output_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        writer.writerows(records)

    print(f"Generated {len(records)} sales records at: {output_path}")
    return output_path


if __name__ == "__main__":
    generate_sales_dataset()

