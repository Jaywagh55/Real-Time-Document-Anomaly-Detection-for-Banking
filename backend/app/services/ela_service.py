from typing import Optional
import io
import base64

from PIL import Image, ImageChops, ImageEnhance


def compute_ela_bytes(content_bytes: bytes, filename: Optional[str] = None, quality: int = 90) -> dict:
    """Compute a simple Error Level Analysis (ELA) heatmap for an image payload.

    Returns a dict with a small base64-encoded PNG under `heatmap` and a simple `score` heuristic.
    If processing fails, returns an explanatory message.
    """
    try:
        img = Image.open(io.BytesIO(content_bytes)).convert("RGB")
    except Exception as e:
        return {"error": f"Not an image or cannot open: {e}"}

    try:
        # Save compressed version to memory
        buffer = io.BytesIO()
        img.save(buffer, "JPEG", quality=quality)
        buffer.seek(0)
        compressed = Image.open(buffer).convert("RGB")

        # Compute absolute difference
        diff = ImageChops.difference(img, compressed)
        # Enhance differences for visibility
        enhancer = ImageEnhance.Brightness(diff)
        diff = enhancer.enhance(2.5)
        # Optionally convert to grayscale and boost contrast
        # Create a small thumbnail for faster transmission
        diff.thumbnail((800, 800))

        out_buf = io.BytesIO()
        diff.save(out_buf, format="PNG")
        out_buf.seek(0)
        b64 = base64.b64encode(out_buf.read()).decode("ascii")

        # A crude score: mean pixel value of diff (0-255) normalized
        stat = diff.convert("L").resize((100, 100))
        pixels = list(stat.getdata())
        avg = sum(pixels) / max(1, len(pixels))
        score = round((avg / 255.0) * 100, 1)

        return {"heatmap": b64, "score": score, "note": "ELA heatmap (base64 PNG)"}
    except Exception as e:
        return {"error": f"ELA processing failed: {e}"}
