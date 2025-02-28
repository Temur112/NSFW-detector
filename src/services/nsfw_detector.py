import os
import cv2
import uuid
from nudenet import NudeDetector
from typing import Dict


detector = NudeDetector()
FRAME_INTERVAL = 15


def detect_nsfw_image(path: str):
    '''
        Runs NSFW on given image file

        :param path: path to image file
        :return :Dictionary with NSFW classification and confindence score
    '''

    results = detector.detect(image_path=path)

    print(results)
    nsfw_score = max([r["score"] for r in results], default=0)

    return {
        "nsfw": nsfw_score>0.5, # the threshold need to be specified based on task
        "confidence": nsfw_score
    }


def extract_frames(video_path:str, output_dir: str):
    """
        extract frames from a video at given intervals
        :return: list of extract frame path
    """
    

    #ensuer output dir exists
    os.makedirs(output_dir, exist_ok=True)


    frame_paths = []
    video = cv2.VideoCapture(video_path)


    frame_count = 0
    while video.isOpened():
        success, frame = video.read()
        if not success:
            print("failes to open")
            break

        if frame_count % FRAME_INTERVAL == 0:
            frame_path = os.path.join(output_dir, f"{uuid.uuid4()}.jpg")
            cv2.imwrite(frame_path, frame)
            frame_paths.append(frame_path)

        frame_count += 1

    video.release()

    return frame_paths


def detect_nsfw_video(video_path: str)-> Dict[str, float]:
    """
        Runs NSFW detection on video frames,
        :return: Final classification and confidance score
    """
    
    output_dir = f"uploads/frames/{uuid.uuid4}"

    frame_paths = extract_frames(video_path, output_dir)

    nsfw_frames = 0
    # total_frames = len(frame_paths)
    max_confidence = 0.0


    for frame in frame_paths:
        result = detect_nsfw_image(frame)
        if result["nsfw"]:
            nsfw_frames += 1
        max_confidence = max(max_confidence, result["confidence"])
        os.remove(frame) # cleanup

    os.rmdir(output_dir)

    return {
        "nsfw": nsfw_frames > 0,
        "confidence": max_confidence
    }