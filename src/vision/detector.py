from dataclasses import dataclass
from typing import Any
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from .coco_labels import IMPORTANT_OBJECTS, to_ptbr

@dataclass
class Detection:
    label: str
    label_pt: str
    confidence: float
    box: list[int]

class ObjectDetector:
    def __init__(self, model_name: str = "yolov8n.pt", confidence_threshold: float = 0.70, only_important: bool = True):
        self.model_name = model_name
        self.confidence_threshold = confidence_threshold
        self.only_important = only_important
        self.model = None
        self._load_model()

    def _load_model(self) -> None:
        try:
            from ultralytics import YOLO
            self.model = YOLO(self.model_name)
        except Exception as exc:
            raise RuntimeError(
                "Não foi possível carregar o YOLO. Verifique se 'ultralytics' está instalado."
            ) from exc

    def detect(self, image: Image.Image | np.ndarray) -> list[dict[str, Any]]:
        if isinstance(image, Image.Image):
            frame = np.array(image.convert("RGB"))
        else:
            frame = image

        results = self.model.predict(frame, conf=self.confidence_threshold, verbose=False)
        detections: list[dict[str, Any]] = []

        for result in results:
            names = result.names
            for box in result.boxes:
                cls_id = int(box.cls[0].item())
                conf = float(box.conf[0].item())
                label = names.get(cls_id, str(cls_id))
                if self.only_important and label not in IMPORTANT_OBJECTS:
                    continue
                x1, y1, x2, y2 = [int(v) for v in box.xyxy[0].tolist()]
                detections.append({
                    "label": label,
                    "label_pt": to_ptbr(label),
                    "confidence": conf,
                    "box": [x1, y1, x2, y2],
                })
        return detections

    def draw_detections(self, image: Image.Image, detections: list[dict[str, Any]]) -> Image.Image:
        img = image.convert("RGB").copy()
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("DejaVuSans.ttf", 18)
        except Exception:
            font = ImageFont.load_default()

        for det in detections:
            x1, y1, x2, y2 = det["box"]
            label = f'{det["label_pt"]} {det["confidence"]*100:.0f}%'
            draw.rectangle([x1, y1, x2, y2], outline=(0, 120, 255), width=4)
            text_bbox = draw.textbbox((x1, y1), label, font=font)
            draw.rectangle(text_bbox, fill=(0, 120, 255))
            draw.text((x1, y1), label, fill=(255, 255, 255), font=font)
        return img
