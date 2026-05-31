import os, time, requests, threading
from concurrent.futures import ThreadPoolExecutor, as_completed




CAR_NAMES = [
    "Audi A4", "Audi A6", "Audi A8", "Audi Q7",
    "BMW 3 Series", "BMW 5 Series", "BMW 6 Series", "BMW 7 Series",
    "BMW X1", "BMW X3", "BMW X4", "BMW X5", "BMW Z4",
    "Bentley Continental",
    "Datsun GO", "Datsun RediGO", "Datsun redi-GO",
    "Ferrari GTC4Lusso", "Force Gurkha",
    "Ford Aspire", "Ford EcoSport", "Ford Endeavour",
    "Ford Figo", "Ford Freestyle",
    "Honda Amaze", "Honda CR-V", "Honda City",
    "Honda Civic", "Honda Jazz", "Honda WR-V",
    "Hyundai Aura", "Hyundai Creta", "Hyundai Elantra",
    "Hyundai Grand i10", "Hyundai Santro", "Hyundai Tucson",
    "Hyundai Venue", "Hyundai Verna", "Hyundai i10", "Hyundai i20",
    "ISUZU MUX", "Isuzu D-Max", "Isuzu MUX",
    "Jaguar F-PACE", "Jaguar XE", "Jaguar XF",
    "Jeep Compass", "Jeep Wrangler",
    "Kia Carnival", "Kia Seltos",
    "Land Rover Discovery",
    "Lexus ES", "Lexus NX", "Lexus RX",
    "MG Hector",
    "Mahindra Alturas", "Mahindra Bolero", "Mahindra KUV100",
    "Mahindra Marazzo", "Mahindra Scorpio", "Mahindra Thar",
    "Mahindra XUV300", "Mahindra XUV500",
    "Maruti Alto", "Maruti Baleno", "Maruti Celerio",
    "Maruti Ciaz", "Maruti Dzire LXI", "Maruti Dzire VXI",
    "Maruti Dzire ZXI", "Maruti Eeco", "Maruti Ertiga",
    "Maruti Ignis", "Maruti S-Presso", "Maruti Swift",
    "Maruti Swift Dzire", "Maruti Vitara Brezza",
    "Maruti Wagon R", "Maruti XL6",
    "Maserati Ghibli", "Maserati Quattroporte",
    "Mercedes-AMG C63", "Mercedes-Benz C-Class", "Mercedes-Benz CLS",
    "Mercedes-Benz E-Class", "Mercedes-Benz GL-Class",
    "Mercedes-Benz GLS", "Mercedes-Benz S-Class",
    "Mini Cooper",
    "Nissan Kicks", "Nissan X-Trail",
    "Porsche Cayenne", "Porsche Macan", "Porsche Panamera",
    "Renault Duster", "Renault KWID", "Renault Triber",
    "Rolls-Royce Ghost",
    "Skoda Octavia", "Skoda Rapid", "Skoda Superb",
    "Tata Altroz", "Tata Harrier", "Tata Hexa",
    "Tata Nexon", "Tata Safari", "Tata Tiago", "Tata Tigor",
    "Toyota Camry", "Toyota Fortuner", "Toyota Glanza",
    "Toyota Innova", "Toyota Yaris",
    "Volkswagen Polo", "Volkswagen Vento",
    "Volvo S90", "Volvo XC40", "Volvo XC60", "Volvo XC90",
]

SAVE_DIR    = "static/cars"
MAX_WORKERS = 4
MIN_SIZE    = 15_000
os.makedirs(SAVE_DIR, exist_ok=True)

HEADERS = {"User-Agent": "Mozilla/5.0"}
print_lock  = threading.Lock()
api_lock    = threading.Lock()
api_call_count = 0

def filename_from_name(name):
    return (
        name.lower()
        .replace(" ", "_").replace("/", "_")
        .replace("-", "_").replace("(", "").replace(")", "")
        + ".jpg"
    )

def google_image_urls(query, count=3):
    try:
        r = requests.get(
            "https://www.googleapis.com/customsearch/v1",
            params={
                "key":        GOOGLE_API_KEY,
                "cx":         SEARCH_ENGINE_ID,
                "q":          query,
                "searchType": "image",
                "num":        count,
                "imgType":    "photo",
                "safe":       "active",
            },
            timeout=10,
        )
        data = r.json()
        
        if "error" in data:
            with print_lock:
                print(f"  API ERROR: {data['error']['message']}")
            return []
        return [item["link"] for item in data.get("items", [])]
    except Exception as e:
        print("EXCEPTION:", e)
        return []

def download_image(url, filepath):
    try:
        r = requests.get(url, headers=HEADERS, timeout=12, stream=True)
        ct = r.headers.get("Content-Type", "")
        if r.status_code == 200 and "image" in ct:
            with open(filepath, "wb") as f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)
            if os.path.getsize(filepath) >= MIN_SIZE:
                return True
            os.remove(filepath)
    except Exception:
        pass
    if os.path.exists(filepath):
        os.remove(filepath)
    return False

def process_car(args):
    global api_call_count
    i, car = args
    fname    = filename_from_name(car)
    filepath = os.path.join(SAVE_DIR, fname)

    if os.path.exists(filepath):
        with print_lock:
            print(f"[{i:>3}/{len(CAR_NAMES)}] SKIP  {car}")
        return car, True

    with api_lock:
        if api_call_count >= 95:
            with print_lock:
                print(f"[{i:>3}/{len(CAR_NAMES)}] QUOTA REACHED — stopping")
            return car, False
        api_call_count += 1

    for url in google_image_urls(f"{car} car India"):
        if download_image(url, filepath):
            with print_lock:
                print(f"[{i:>3}/{len(CAR_NAMES)}] OK    {car}")
            return car, True

    with print_lock:
        print(f"[{i:>3}/{len(CAR_NAMES)}] FAIL  {car}")
    return car, False

if __name__ == "__main__":
    print(f"NOTE: Google free tier = 100 queries/day.")
    print(f"      {len(CAR_NAMES)} cars may need 2 days if quota runs out.\n")

    start = time.time()
    success, failed = [], []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = {ex.submit(process_car, (i, car)): car
                   for i, car in enumerate(CAR_NAMES, 1)}
        for fut in as_completed(futures):
            car, ok = fut.result()
            (success if ok else failed).append(car)

    elapsed = time.time() - start
    print(f"\n{'='*55}")
    print(f"Done in {elapsed:.1f}s | OK: {len(success)} | Failed: {len(failed)}")
    print(f"API calls used today: {api_call_count}/100")

    print("\n── Paste into views.py ──\n")
    print("CAR_IMAGES = {")
    for car in CAR_NAMES:
        fname = filename_from_name(car)
        path  = f"cars/{fname}" if car not in failed else "cars/default.jpg"
        print(f"    '{car}': '{path}',")
    print("}")

    if failed:
        print(f"\n── Run again tomorrow for these {len(failed)} cars ──")
        for f in failed:
            print(f"  {filename_from_name(f)}  ←  {f}")
