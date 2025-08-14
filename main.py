import asyncio
import contextlib
import json
import os
import shutil
from contextlib import asynccontextmanager
from pathlib import Path
from typing import List

import httpx
from PIL import Image
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

CONFIG_PATH = Path("config.json")
FILES_DIR = Path("files/s0/tiles")
BLUEPRINT_DIR = Path("blueprints")
TILE_BASE_URL = "https://backend.wplace.live/files/s0/tiles"
UPDATE_INTERVAL = 60  # seconds


async def update_images():
    """Background task that downloads and updates tiles periodically."""
    async with httpx.AsyncClient(headers={"User-Agent": "Mozilla/5.0"}) as client:
        while True:
            if not CONFIG_PATH.exists():
                print("No config.json found, skipping update.")
                await asyncio.sleep(UPDATE_INTERVAL)
                continue

            with CONFIG_PATH.open() as f:
                tiles: List[List[int]] = json.load(f)

            missing_pix = 0

            for tile in tiles:
                x, y = tile
                basepath = FILES_DIR / str(x) / f"{y}.png"
                blueprintpath = BLUEPRINT_DIR / str(x) / f"{y}blueprint.png"

                # Download current tile
                url = f"{TILE_BASE_URL}/{x}/{y}.png"
                resp = await client.get(url)
                resp.raise_for_status()
                os.makedirs(basepath.parent, exist_ok=True)
                basepath.write_bytes(resp.content)

                # Create blueprint if missing
                if not blueprintpath.exists():
                    os.makedirs(blueprintpath.parent, exist_ok=True)
                    shutil.copyfile(basepath, blueprintpath)

                # Compare with blueprint
                basepic = Image.open(basepath).convert("RGBA")
                basepix = basepic.load()
                blueprint = Image.open(blueprintpath).convert("RGBA")
                blueprintpix = blueprint.load()

                width, height = basepic.size
                identical = True
                xmin, ymin = 999, 999
                xmax, ymax = 0, 0
                diff = []

                for px in range(width):
                    for py in range(height):
                        if blueprintpix[px, py] != (0, 0, 0, 0) and blueprintpix[px, py] != basepix[px, py]:
                            missing_pix += 1
                            bppix = blueprintpix[px, py]
                            identical = False
                            xmin = min(px, xmin)
                            xmax = max(px, xmax)
                            ymin = min(py, ymin)
                            ymax = max(py, ymax)
                            diff.append(((px, py), (bppix[0], bppix[1], bppix[2], 255)))

                if not identical:
                    for px in range(xmin - 4, xmax + 5):
                        for py in range(ymin - 4, ymax + 5):
                            if px < 0 or py < 0 or px > 999 or py > 999:
                                continue
                            basepix[px, py] = (255, 0, 255, 80)
                    for el in diff:
                        basepix[el[0]] = el[1]
                    basepic.save(basepath, "PNG")

            print(
                f"Updated diff. Missing pixels: {missing_pix} ~ {round(missing_pix / 2 / 60, 1)} hours to regenerate"
            )

            await asyncio.sleep(UPDATE_INTERVAL)


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Start background updater
    task = asyncio.create_task(update_images())
    try:
        yield
    finally:
        # Optionally cancel background task on shutdown
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # same as Access-Control-Allow-Origin: *
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static directories
Path("files").mkdir(parents=True, exist_ok=True)
Path("blueprints").mkdir(parents=True, exist_ok=True)
app.mount("/files", StaticFiles(directory="files"), name="files")
app.mount("/blueprints", StaticFiles(directory="blueprints"), name="blueprints")


@app.get("/config.json")
async def get_config():
    """Serve config.json."""
    return FileResponse(CONFIG_PATH)
