"""Production entrypoint for Hugging Face Spaces deployment."""
import os
import uvicorn
from src.main import app

if __name__ == "__main__":
    port = int(os.getenv("PORT", 7860))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    )
