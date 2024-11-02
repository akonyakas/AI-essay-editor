from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],  # Allow all origins for demo purposes. Restrict this in production.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the "static" folder to serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")


# Serve the HTML file from the "static" folder
@app.get("/", response_class=HTMLResponse)
async def get():
    with open("static/index.html") as f:
        return HTMLResponse(content=f.read(), status_code=200)


# Example API endpoint for essay editing
@app.post("/ai-essay-editor")
async def edit_essay(text: str):
    # Mock response - replace this with your actual logic
    return [
        {
            "original_sentence": "The cat sat on the mat.",
            "revised_sentence": "The feline rested on the rug.",
            "explanation": "Used more formal language.",
        },
        {
            "original_sentence": "It was a beautiful day.",
            "revised_sentence": None,
            "explanation": "This sentence is fine.",
        },
    ]
