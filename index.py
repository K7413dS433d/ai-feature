from fastapi import FastAPI
from src.search_by_image.search import app as search_app, lifespan

main_app = FastAPI()

# Mount the inner app under a prefix
main_app.mount("/search", search_app)

# Root-level route for testing
@main_app.get("/")
def root():
    return {"message": "Main App is running"}
# Handle the startup of the mounted app manually
@main_app.on_event("startup")
async def start_inner_app():
    # Run the lifespan startup manually
    await lifespan(search_app).__aenter__()


#  uvicorn index:main_app --reload
#  uvicorn index:main_app --host 0.0.0.0 --port 8000
