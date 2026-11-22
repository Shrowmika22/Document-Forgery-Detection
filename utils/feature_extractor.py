import cv2
import numpy as np


def extract_features(image_path):

    image = cv2.imread(image_path)

    if image is None:
        raise ValueError("Unable to read image.")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Image dimensions
    height, width = gray.shape

    # Blur measurement
    blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()

    # Edge measurement
    edges = cv2.Canny(gray, 100, 200)
    edge_ratio = np.mean(edges > 0)

    # Noise estimation
    noise = cv2.GaussianBlur(gray, (3, 3), 0)
    noise_difference = cv2.absdiff(gray, noise)
    noise_score = np.mean(noise_difference)

    # Brightness
    brightness = np.mean(gray)

    # Contrast
    contrast = np.std(gray)

    features = {
        "width": width,
        "height": height,
        "blur_score": float(blur_score),
        "edge_ratio": float(edge_ratio),
        "noise_score": float(noise_score),
        "brightness": float(brightness),
        "contrast": float(contrast)
    }

    return features