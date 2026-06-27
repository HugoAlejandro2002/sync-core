from __future__ import annotations

import asyncio
from typing import Any

import cv2
import numpy as np

from app.core.exceptions import ImageProcessingError

_INVALID_IMAGE = "El archivo enviado no es una imagen válida."
_PROCESSING_FAILED = "No se pudo procesar la imagen."


class ImagePreprocessingService:
    """Enhances evidence photos with OpenCV for better AI extraction.

    OpenCV is used only inside this service. Decoding failures raise a controlled error;
    optional steps (document warp) degrade gracefully to the enhanced image.
    """

    MAX_DIMENSION = 1600

    async def preprocess(self, image_bytes: bytes) -> bytes:
        if not image_bytes:
            raise ImageProcessingError(message=_INVALID_IMAGE)
        return await asyncio.to_thread(self._process, image_bytes)

    def _process(self, image_bytes: bytes) -> bytes:
        buffer = np.frombuffer(image_bytes, dtype=np.uint8)
        image: Any = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
        if image is None:
            raise ImageProcessingError(message=_INVALID_IMAGE)

        image = self._resize(image)
        warped = self._try_document_warp(image)
        base = warped if warped is not None else image

        gray = cv2.cvtColor(base, cv2.COLOR_BGR2GRAY)
        gray = cv2.fastNlMeansDenoising(gray, None, h=10)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        contrast = clahe.apply(gray)
        threshold = cv2.adaptiveThreshold(
            contrast,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31,
            10,
        )

        ok, encoded = cv2.imencode(".png", threshold)
        if not ok:
            raise ImageProcessingError(message=_PROCESSING_FAILED)
        return bytes(encoded.tobytes())

    def _resize(self, image: Any) -> Any:
        height, width = image.shape[:2]
        longest = max(height, width)
        if longest <= self.MAX_DIMENSION:
            return image
        scale = self.MAX_DIMENSION / longest
        new_size = (int(width * scale), int(height * scale))
        return cv2.resize(image, new_size, interpolation=cv2.INTER_AREA)

    def _try_document_warp(self, image: Any) -> Any | None:
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            edged = cv2.Canny(blurred, 50, 150)
            contours, _ = cv2.findContours(edged, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            candidates = sorted(contours, key=cv2.contourArea, reverse=True)[:5]
            image_area = float(image.shape[0] * image.shape[1])
            for contour in candidates:
                perimeter = cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)
                if len(approx) == 4 and cv2.contourArea(approx) > 0.3 * image_area:
                    return self._four_point_warp(image, approx.reshape(4, 2))
        except cv2.error:
            return None
        return None

    def _four_point_warp(self, image: Any, points: Any) -> Any:
        rect = self._order_points(points).astype("float32")
        (tl, tr, br, bl) = rect
        width = int(max(np.linalg.norm(br - bl), np.linalg.norm(tr - tl)))
        height = int(max(np.linalg.norm(tr - br), np.linalg.norm(tl - bl)))
        if width < 10 or height < 10:
            return image
        destination = np.array(
            [[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]],
            dtype="float32",
        )
        matrix = cv2.getPerspectiveTransform(rect, destination)
        return cv2.warpPerspective(image, matrix, (width, height))

    def _order_points(self, points: Any) -> Any:
        rect = np.zeros((4, 2), dtype="float32")
        summed = points.sum(axis=1)
        rect[0] = points[np.argmin(summed)]
        rect[2] = points[np.argmax(summed)]
        diff = np.diff(points, axis=1)
        rect[1] = points[np.argmin(diff)]
        rect[3] = points[np.argmax(diff)]
        return rect
