#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import io
import mimetypes
import re
from pathlib import Path

try:
    from PIL import Image
except Exception:
    Image = None


IMAGE_PATTERN = re.compile(r"!\[([^\]]*)\]\((<[^>]+>|[^)]+)\)")
DATA_URI_PATTERN = re.compile(r"^data:([^;,]+);base64,(.*)$", re.IGNORECASE | re.DOTALL)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_md", type=Path)
    parser.add_argument("output_md", type=Path)
    parser.add_argument("--compress", action="store_true")
    parser.add_argument("--process-data-uri", action="store_true")
    parser.add_argument("--max-width", type=int, default=0)
    parser.add_argument("--jpeg-quality", type=int, default=82)
    return parser.parse_args()


def extract_path(raw: str) -> str:
    value = raw.strip()
    if value.startswith("<") and value.endswith(">"):
        value = value[1:-1].strip()
    if value.startswith("http://") or value.startswith("https://"):
        return value
    if " \"" in value and value.endswith("\""):
        value = value.split(" \"", 1)[0].strip()
    return value


def guess_mime(path: Path) -> str:
    mime, _ = mimetypes.guess_type(str(path))
    if mime is not None:
        return mime
    suffix = path.suffix.lower()
    return {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".webp": "image/webp",
        ".svg": "image/svg+xml",
    }.get(suffix, "application/octet-stream")


def decode_data_uri(uri: str) -> tuple[str, bytes] | None:
    m = DATA_URI_PATTERN.match(uri)
    if m is None:
        return None
    mime = m.group(1).strip().lower()
    payload = m.group(2).strip()
    try:
        raw = base64.b64decode(payload, validate=False)
    except Exception:
        return None
    return mime, raw


def encode_data_uri(mime: str, data: bytes) -> str:
    return f"data:{mime};base64,{base64.b64encode(data).decode('ascii')}"


def maybe_reencode_image(
    mime: str,
    data: bytes,
    compress: bool,
    max_width: int,
    jpeg_quality: int,
) -> tuple[str, bytes]:
    if Image is None:
        return mime, data
    if not mime.startswith("image/"):
        return mime, data
    if not compress and max_width <= 0:
        return mime, data

    try:
        img = Image.open(io.BytesIO(data))
    except Exception:
        return mime, data

    if max_width > 0 and img.width > max_width:
        resampling = getattr(getattr(Image, "Resampling", Image), "LANCZOS")
        new_height = max(1, int(round(img.height * (max_width / float(img.width)))))
        img = img.resize((max_width, new_height), resampling)

    has_alpha = img.mode in ("RGBA", "LA") or "transparency" in getattr(img, "info", {})

    if compress:
        if has_alpha:
            out = io.BytesIO()
            if img.mode not in ("RGBA", "LA"):
                img = img.convert("RGBA")
            img.save(out, format="PNG", optimize=True, compress_level=9)
            return "image/png", out.getvalue()

        rgb = img.convert("RGB")
        out = io.BytesIO()
        rgb.save(out, format="JPEG", optimize=True, progressive=True, quality=max(30, min(95, jpeg_quality)))
        return "image/jpeg", out.getvalue()

    out = io.BytesIO()
    if has_alpha or mime == "image/png":
        if img.mode not in ("RGBA", "LA", "P"):
            img = img.convert("RGBA")
        img.save(out, format="PNG", optimize=True)
        return "image/png", out.getvalue()

    rgb = img.convert("RGB")
    rgb.save(out, format="JPEG", optimize=True, progressive=True, quality=95)
    return "image/jpeg", out.getvalue()


def embed_images(
    markdown: str,
    base_dir: Path,
    compress: bool,
    process_data_uri: bool,
    max_width: int,
    jpeg_quality: int,
) -> tuple[str, int, int]:
    replaced = 0
    skipped = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal replaced, skipped
        alt = match.group(1)
        raw_target = match.group(2)
        target = extract_path(raw_target)

        if target.startswith("http://") or target.startswith("https://"):
            skipped += 1
            return match.group(0)

        if target.startswith("data:"):
            if not process_data_uri:
                skipped += 1
                return match.group(0)
            parsed = decode_data_uri(target)
            if parsed is None:
                skipped += 1
                return match.group(0)
            mime, raw = parsed
            out_mime, out_data = maybe_reencode_image(mime, raw, compress, max_width, jpeg_quality)
            replaced += 1
            return f"![{alt}]({encode_data_uri(out_mime, out_data)})"

        image_file = (base_dir / target).resolve()
        if not image_file.exists() or not image_file.is_file():
            skipped += 1
            return match.group(0)

        mime = guess_mime(image_file)
        raw = image_file.read_bytes()
        out_mime, out_data = maybe_reencode_image(mime, raw, compress, max_width, jpeg_quality)
        replaced += 1
        return f"![{alt}]({encode_data_uri(out_mime, out_data)})"

    result = IMAGE_PATTERN.sub(replace, markdown)
    return result, replaced, skipped


def main() -> None:
    args = parse_args()
    source = args.input_md.resolve()
    target = args.output_md.resolve()

    content = source.read_text(encoding="utf-8")
    out, replaced, skipped = embed_images(
        content,
        source.parent,
        args.compress,
        args.process_data_uri,
        args.max_width,
        args.jpeg_quality,
    )
    target.write_text(out, encoding="utf-8")
    print(f"output={target}")
    print(f"replaced={replaced}")
    print(f"skipped={skipped}")


if __name__ == "__main__":
    main()
