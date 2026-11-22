import os
import cv2
import numpy as np

from utils.feature_extractor import extract_features


def analyze_image(image_path):

    features = extract_features(image_path)

    score = 0
    reasons = []

    # --------------------------------
    # Blur analysis
    # --------------------------------

    if features["blur_score"] < 30:

        score += 10
        reasons.append(
            "The document image appears unusually blurred."
        )

    # --------------------------------
    # Noise analysis
    # --------------------------------

    if features["noise_score"] > 15:

        score += 20
        reasons.append(
            "Unusual image noise or local pixel variation detected."
        )

    # --------------------------------
    # Edge analysis
    # --------------------------------

    if features["edge_ratio"] < 0.01:

        score += 10
        reasons.append(
            "Low edge consistency detected in the document image."
        )

    # --------------------------------
    # Contrast analysis
    # --------------------------------

    if features["contrast"] < 20:

        score += 5
        reasons.append(
            "Low document contrast detected."
        )

    # --------------------------------
    # Final assessment
    # --------------------------------

    if score >= 25:

        label = "POSSIBLY FORGED"

    else:

        label = "LIKELY AUTHENTIC"

    confidence = min(95, max(55, 55 + score))

    if not reasons:

        reasons.append(
            "No major visual inconsistencies were detected by the current analysis."
        )

    return {
        "label": label,
        "confidence": confidence,
        "score": score,
        "reasons": reasons,
        "features": features
    }


def analyze_document(file_path, processed_folder):

    extension = os.path.splitext(file_path)[1].lower()

    # --------------------------------
    # Image document
    # --------------------------------

    if extension in [".jpg", ".jpeg", ".png"]:

        return analyze_image(file_path)

    # --------------------------------
    # PDF document
    # --------------------------------

    if extension == ".pdf":

        import fitz

        os.makedirs(processed_folder, exist_ok=True)

        pdf = fitz.open(file_path)

        page_results = []

        for i, page in enumerate(pdf):

            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))

            image_path = os.path.join(
                processed_folder,
                f"analysis_page_{i + 1}.png"
            )

            pix.save(image_path)

            result = analyze_image(image_path)

            page_results.append(result)

        pdf.close()

        if not page_results:
            raise ValueError("PDF does not contain any pages.")

        # Combine page results

        total_score = sum(
            result["score"] for result in page_results
        )

        average_score = total_score / len(page_results)

        all_reasons = []

        for result in page_results:

            for reason in result["reasons"]:

                if reason not in all_reasons:
                    all_reasons.append(reason)

        if average_score >= 25:

            label = "POSSIBLY FORGED"

        else:

            label = "LIKELY AUTHENTIC"

        confidence = min(
            95,
            max(55, int(55 + average_score))
        )

        return {
            "label": label,
            "confidence": confidence,
            "score": round(average_score, 2),
            "reasons": all_reasons,
            "pages": len(page_results)
        }

    raise ValueError("Unsupported file format.")