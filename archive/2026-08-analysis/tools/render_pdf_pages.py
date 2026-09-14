from pathlib import Path
import sys

import pypdfium2 as pdfium
from PIL import Image, ImageDraw


def render(pdf_path: Path, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    pdf = pdfium.PdfDocument(str(pdf_path))
    page_paths = []
    for index in range(len(pdf)):
        page = pdf[index]
        bitmap = page.render(scale=1.7)
        image = bitmap.to_pil().convert("RGB")
        target = output_dir / f"page-{index + 1:03d}.png"
        image.save(target, quality=95)
        page_paths.append(target)

    for start in range(0, len(page_paths), 6):
        selected = page_paths[start : start + 6]
        thumb_w, thumb_h = 360, 466
        sheet = Image.new("RGB", (thumb_w * 3 + 80, thumb_h * 2 + 100), "#D9E0E8")
        draw = ImageDraw.Draw(sheet)
        for offset, page_path in enumerate(selected):
            page_image = Image.open(page_path).convert("RGB")
            page_image.thumbnail((thumb_w - 20, thumb_h - 35), Image.Resampling.LANCZOS)
            x = 20 + (offset % 3) * thumb_w
            y = 35 + (offset // 3) * thumb_h
            sheet.paste(page_image, (x + (thumb_w - page_image.width) // 2, y + 20))
            draw.text((x + 8, y), f"Page {start + offset + 1}", fill="#12304F")
        end = start + len(selected)
        sheet.save(output_dir / f"contact-{start + 1:03d}-{end:03d}.png")
    print(f"Rendered {len(page_paths)} pages to {output_dir}")


if __name__ == "__main__":
    render(Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve())
