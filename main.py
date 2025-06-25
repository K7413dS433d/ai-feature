from fastapi import FastAPI
from src.search_by_image.search import app as search_app

main_app = FastAPI()

# Root-level route for testing
@main_app.get("/")
def root():
    return {"message": "Main App is running"}

# Mount the inner app under a prefix
main_app.mount("/search", search_app)

#  uvicorn main:main_app --reload
#  uvicorn main:main_app --host 0.0.0.0 --port 8000
##  python -m uvicorn main:main_app --host 0.0.0.0 --port 8000