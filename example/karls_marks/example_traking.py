from ultralytics import YOLO

model = YOLO("yolov8n.pt")
model.track(source="D:\Final qualifying work\Main\other\load_video_ufanet\output.mp4", show=True, save=True)