from PIL import Image
from fastapi import HTTPException, UploadFile, status
import shutil

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "bmp"}


def validate_and_convert_image(file: UploadFile, file_path: str)->str:
    """Validate and conver image"""

    try:
        # open image
        image = Image.image(file.file)

        # validate format
        ext = image.format().lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file")
        

        # convert to JPED if it is needed
        if ext != "jpeg" and ext != "jpg":
            file_path = file_path.replace(".jpg", "jpeg")
            image = image.convert("RGB")
            image.save(file_path, format="JPEG")
        else:
            # save as it is
            with open(file_path, "wb") as buffer:
                file.file.seek(0)
                shutil.copyfileobj(file.file, buffer)

        return file_path

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="seems image is invalid")

