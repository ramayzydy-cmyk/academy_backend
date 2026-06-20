import os
import shutil

import fitz
from PIL import Image
from django.conf import settings


class PDFConverterService:

    @staticmethod
    def convert(reader_book):

        if not reader_book.pdf_file:
            return False

        pdf_path = reader_book.pdf_file.path

        folder_name = reader_book.folder_name.strip()

        output_dir = os.path.join(
            settings.MEDIA_ROOT,
            "reader",
            "books",
            folder_name,
        )

        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)

        os.makedirs(output_dir, exist_ok=True)

        document = fitz.open(pdf_path)

        total_pages = len(document)

        for index in range(total_pages):

            page = document.load_page(index)

            pix = page.get_pixmap(
                matrix=fitz.Matrix(2, 2),
                alpha=False,
            )

            temp_png = os.path.join(
                output_dir,
                f"page{index + 1:03}.png",
            )

            pix.save(temp_png)

            image = Image.open(temp_png)

            image.save(
                os.path.join(
                    output_dir,
                    f"page{index + 1:03}.webp",
                ),
                "WEBP",
                quality=80,
                method=6,
            )

            image.close()

            os.remove(temp_png)

        document.close()

        reader_book.total_pages = total_pages
        reader_book.save(update_fields=["total_pages"])

        return True