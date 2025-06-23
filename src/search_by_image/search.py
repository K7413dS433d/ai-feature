import os
import shutil
import logging
import asyncio
from pathlib import Path
from fastapi import FastAPI, File, UploadFile
from DeepImageSearch import Load_Data, Search_Setup
from fastapi import HTTPException
from contextlib import asynccontextmanager
import builtins

builtins.input = lambda *args, **kwargs: "yes"

from src.search_by_image.image_utils import fetch_image_urls, download_images

# Set working directory to current file's directory
os.chdir(Path(__file__).resolve().parent)

# Fix for some parallel processing issues with certain libraries
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

BASE_DIR = Path(__file__).resolve().parent
IMAGE_DIR = BASE_DIR / "data"
UPLOAD_FOLDER = BASE_DIR / "uploads"

# Create necessary folders
Path(IMAGE_DIR).mkdir(parents=True, exist_ok=True)
Path(UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

search_engine = None

async def update_index_with_new_images():
    image_data = await fetch_image_urls()  
    await download_images(image_data)  
    image_list = Load_Data().from_folder([IMAGE_DIR])  
    search_engine.run_index()  

async def schedule_index_update(interval_seconds: int = 3600):
    while True:
        try:
            logger.info("Starting scheduled image update...")
            await update_index_with_new_images()
            logger.info("Scheduled update completed.")
        except Exception as e:
            logger.error(f"Error during scheduled update: {e}")
        await asyncio.sleep(interval_seconds)

@asynccontextmanager
async def lifespan(app: FastAPI):
    global search_engine

    if any(Path(IMAGE_DIR).iterdir()):
        logger.info("Found local images. Using them for indexing.")
    else:
        logger.info("No local images found. Downloading from DB...")
        image_data = await fetch_image_urls()
        await download_images(image_data)

    image_list = Load_Data().from_folder([IMAGE_DIR])
    logger.info(f"Total images indexed: {len(image_list)}")

    if not image_list:
        logger.warning("No images to index.")
        yield
        return

    search_engine = Search_Setup(image_list=image_list)
    search_engine.run_index()
    logger.info("Indexing completed.")

    asyncio.create_task(schedule_index_update())

    yield
    logger.info("Shutting down.")

# Create the FastAPI app with the lifespan context manager
app = FastAPI(lifespan=lifespan)

@app.get("/")
def home():
    return {"message": "FastAPI is running with image search!"}

@app.post("/search-by-image/")
async def search_by_image(file: UploadFile = File(...), top_n: int = 5):
    file_location = f"{UPLOAD_FOLDER}/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    if search_engine is None:
        logger.warning("Search engine not initialized. No data available for search.")
        raise HTTPException(
            status_code=503,
            detail="Search engine not initialized. No data available for search."
        )

    search_results = search_engine.get_similar_images(image_path=file_location, number_of_images=top_n)
    meal_ids = []
    for path in search_results.values():
        filename = os.path.basename(path)
        if filename.startswith("meal_") and filename.endswith(".jpg"):
            meal_id = filename.replace("meal_", "").replace(".jpg", "")
            meal_ids.append(meal_id)

    return {
        "query_image": file_location,
        "similar_meal_ids": meal_ids
    }

# uvicorn src.search_by_image.search:app --reload
