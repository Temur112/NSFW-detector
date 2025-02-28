from pydantic import BaseModel, HttpUrl


class DetectionResult(BaseModel):
    nsfw: bool
    confidence: float



class URLDetectionRequest(BaseModel):
    url: HttpUrl


    