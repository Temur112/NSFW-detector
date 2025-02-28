from fastapi import APIRouter, UploadFile, File, HTTPException, status
import shutil
import uuid
import os
import requests
import mimetypes
from src.services.nsfw_detector import detect_nsfw_image, detect_nsfw_video
# import response models
from src.utils.utils import validate_and_convert_image
from src.schemas.detection import URLDetectionRequest, DetectionResult


ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "bmp"}
ALLOWED_VIDEO_EXTENSIONS = {"mp4", "avi", "mov", "mkv"}

UPLOAD_IMAGE_DIR = "uploads/images/"
UPLOAD_VIDEO_DIR = "uploads/Videos/"


# ensure directories are exists
os.makedirs(UPLOAD_IMAGE_DIR, exist_ok=True)
os.makedirs(UPLOAD_VIDEO_DIR, exist_ok=True)

detector_router = APIRouter()


@detector_router.post("/detect/file")
async def detect_nsfw_file(file: UploadFile = File(...)):
    '''
        accepts image, save temporarily, runs on nsfw detection and deletes the image
    '''

    ext = file.filename.split(".")[-1].lower()
    if ext in ALLOWED_IMAGE_EXTENSIONS:
        file_type = "image"
        file_path = f"{UPLOAD_IMAGE_DIR}/{uuid.uuid4()}.{ext}"
    elif ext in ALLOWED_VIDEO_EXTENSIONS:
        file_type = "video"
        file_path = f"{UPLOAD_VIDEO_DIR}/{uuid.uuid4()}.{ext}"
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="unspported file")


    

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # file_path = validate_and_convert_image(file, file_path)  use if u want consistent file types which is jpeg in this case

    if file_type == "image":
        result = detect_nsfw_image(file_path)
    else:
        result = detect_nsfw_video(file_path)

    os.remove(file_path) # cleanup

    return result


@detector_router.post("/detect/url")
async def detect_nsfw_from_url(request:URLDetectionRequest):
    try:
        response = requests.get(request.url, stream=True)
        response.raise_for_status()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bad or unreachable url")
    
    


    try:
        file_extension = mimetypes.guess_extension(response.headers.get("content-type", "")).replace('.', '').lower()
        if file_extension in ALLOWED_IMAGE_EXTENSIONS:
            file_path = f"{UPLOAD_IMAGE_DIR}/{uuid.uuid4()}.{file_extension}"
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(response.raw, buffer)
            result = detect_nsfw_image(file_path)
            os.remove(file_path)

            return {
                "type": "image",
                "nsfw": result["nsfw"],
                "confidence": result["confidence"]
            }
        elif file_extension in ALLOWED_VIDEO_EXTENSIONS:
            file_path = f"{UPLOAD_VIDEO_DIR}/{uuid.uuid4()}"
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(response.raw, buffer)

            result = detect_nsfw_video(file_path)

            os.remove(file_path)

            return {"type": "video", "nsfw": result["nsfw"], "confidence": result["confidence"]}
        
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="unsupported file")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"internal server error due to {e}" )
    


@detector_router.post("/detect/local", response_model=DetectionResult)
async def detect_nsfw_from_local(file_path:str):
    """
        Detects NSFW content from local existing file absoulte path need to be provided
    
    """

    abs_path = os.path.abspath(file_path)


    if not os.path.exists(abs_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File Not found")
    
    # print(file_extension)

    _, file_extension = os.path.splitext(file_path)
    
    file_extension = file_extension.replace(".", "")


    if file_extension in ALLOWED_IMAGE_EXTENSIONS:
        result = detect_nsfw_image(path=file_path)
        return {"nsfw": result["nsfw"], "confidence": result["confidence"]}
    elif file_extension in ALLOWED_VIDEO_EXTENSIONS:
        result = detect_nsfw_video(file_path)
        return {"nsfw": result["nsfw"], "confidence": result["confidence"]}
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file type")
    

