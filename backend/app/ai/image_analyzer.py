import numpy as np
from PIL import Image
from typing import Optional, Dict, Any, List
from app.models.observation import IdentificationResult

DEMO_WARNING_MESSAGE = (
    "DEMO / FALLBACK MODE: This is an illustrative heuristic, NOT a live model prediction. "
    "No vision-capable open-weight model (Gemma/PaliGemma/LLaVA) is currently connected. "
    "Start Ollama with a vision model or configure HUGGINGFACE_API_KEY for real AI inference."
)


def extract_visual_metrics(image: Image.Image) -> Dict[str, float]:
    """
    Extract genuine color and spatial distribution metrics using Pillow and NumPy.
    """
    img_rgb = image.convert("RGB").resize((64, 64))
    arr = np.array(img_rgb, dtype=np.float32) / 255.0

    r = arr[:, :, 0]
    g = arr[:, :, 1]
    b = arr[:, :, 2]

    # Brightness (Value)
    brightness = np.maximum(np.maximum(r, g), b)
    mean_brightness = float(np.mean(brightness))
    dynamic_range = float(np.max(brightness) - np.min(brightness))

    # Top half (sky / upper horizon) vs bottom half (ground / foliage)
    top_r, top_g, top_b = r[:32, :], g[:32, :], b[:32, :]
    bot_r, bot_g, bot_b = r[32:, :], g[32:, :], b[32:, :]

    # Warm sunset / sunrise sky: high red, lower blue in upper half
    warm_top_mask = (top_r > 0.45) & (top_r > top_b * 1.15) & (top_g > 0.20)
    top_warm_ratio = float(np.mean(warm_top_mask))

    # Clear daylight / blue sky: high blue in upper half
    blue_top_mask = (top_b > 0.45) & (top_b > top_r * 1.15)
    top_sky_ratio = float(np.mean(blue_top_mask))

    # Green foliage: Green exceeds both Red and Blue by at least 10%
    green_mask = (g > r * 1.10) & (g > b * 1.10) & (g > 0.15)
    green_ratio = float(np.mean(green_mask))

    # Center crop (32x32) vs perimeter to detect macro focus
    center_g = g[16:48, 16:48]
    center_r = r[16:48, 16:48]
    center_b = b[16:48, 16:48]

    # Bright yellow/white floral bloom in center (e.g. dandelion, daisy)
    center_yellow_mask = (center_r > 0.50) & (center_g > 0.45) & (center_b < 0.40)
    center_yellow_ratio = float(np.mean(center_yellow_mask))

    # Center white bloom
    center_white_mask = (center_r > 0.70) & (center_g > 0.70) & (center_b > 0.65)
    center_white_ratio = float(np.mean(center_white_mask))

    return {
        "mean_brightness": mean_brightness,
        "dynamic_range": dynamic_range,
        "top_warm_ratio": top_warm_ratio,
        "top_sky_ratio": top_sky_ratio,
        "green_ratio": green_ratio,
        "center_yellow_ratio": center_yellow_ratio,
        "center_white_ratio": center_white_ratio
    }


def analyze_image_heuristics(
    image: Image.Image,
    user_hint: Optional[str] = None
) -> IdentificationResult:
    """
    Genuine heuristic evaluation of an image for offline / demo mode.
    Strictly prevents species fabrication or false high-confidence claims.
    """
    metrics = extract_visual_metrics(image)
    hint_clean = (user_hint or "").strip().lower()

    # Case 1: Dark / Ambiguous Image
    if metrics["mean_brightness"] < 0.12 or metrics["dynamic_range"] < 0.15:
        return IdentificationResult(
            identification="No confident identification — Low Light / Ambiguous Image",
            scientific_name=None,
            category="weather",
            confidence=0.05,
            confidence_level="uncertain",
            is_confident=False,
            summary=(
                "The uploaded image is too dark, blurry, or low in contrast to discern botanical or wildlife structures. "
                "TrailLens refuses to guess species without clear visual signal."
            ),
            observations=[
                "Move into an area with natural ambient outdoor daylight.",
                "Hold the camera steady within 30–60 cm of the specimen.",
                "Ensure the organism is in sharp focus before taking the shot."
            ],
            outdoor_challenge="Step into an open, sunlit clearing and observe how natural light filters through the trees for 3 minutes without screens.",
            safety_note="Never attempt identification using dark or ambiguous photos.",
            screen_break_message="Put your phone away. Let your eyes adjust to natural ambient light.",
            model_used="TrailLens Heuristics Engine (Offline Fallback)",
            is_demo=True,
            fallback_warning=DEMO_WARNING_MESSAGE,
            scene_description="Low-light or underexposed capture with insufficient contrast"
        )

    # Case 2: Sunset / Sunrise / Golden Hour Landscape
    # (Matches user's case: sunset landscape containing flowers and trees)
    if metrics["top_warm_ratio"] > 0.22 or (metrics["top_warm_ratio"] > 0.12 and metrics["green_ratio"] < 0.45):
        return IdentificationResult(
            identification="No confident identification — Sunset / Landscape View",
            scientific_name=None,
            category="geology",
            confidence=0.10,
            confidence_level="uncertain",
            is_confident=False,
            summary=(
                "The photo appears to capture a broad sunset, sunrise, or golden-hour landscape with distant foliage or trees. "
                "TrailLens does not fabricate a species identification for wide landscape views."
            ),
            observations=[
                "Look toward the horizon to observe the natural color gradient shifting from gold to amber and indigo.",
                "Notice the silhouette contours of foreground tree branches against the luminous sky.",
                "To identify a specific flower or leaf, move within 1 meter and take a focused macro photo."
            ],
            outdoor_challenge="Put your phone in your pocket. Watch the horizon light shift for 3 quiet minutes without digital distractions.",
            safety_note="Wide landscape photos cannot be used to verify individual flora or fungi species.",
            screen_break_message="Lock your screen and pocket your device. Enjoy the natural sunset with your own eyes.",
            model_used="TrailLens Heuristics Engine (Offline Fallback)",
            is_demo=True,
            fallback_warning=DEMO_WARNING_MESSAGE,
            scene_description="Sunset or golden-hour sky over horizon with distant trees and vegetation"
        )

    # Case 3: Wide Scenic Vista / Open Sky with Distant Foliage
    if metrics["top_sky_ratio"] > 0.28 and metrics["green_ratio"] < 0.40:
        return IdentificationResult(
            identification="No confident identification — Broad Scenic Vista",
            scientific_name=None,
            category="geology",
            confidence=0.12,
            confidence_level="uncertain",
            is_confident=False,
            summary=(
                "This photo shows an open landscape or panoramic vista. "
                "Because the frame contains a wide outdoor scene rather than a single close-up organism, no specific species can be responsibly identified."
            ),
            observations=[
                "Scan the wider terrain and pick one specific tree, shrub, or flowering plant to inspect.",
                "Notice the wind direction by observing the motion of treetops or grasses.",
                "Step closer to an individual organism for an accurate macro identification."
            ],
            outdoor_challenge="Walk up to one individual tree or plant in this landscape and examine its bark or leaves up close for 3 minutes.",
            safety_note="Always stay on marked trails when moving toward natural specimens.",
            screen_break_message="Put your phone away. Take three deep breaths and survey the open landscape.",
            model_used="TrailLens Heuristics Engine (Offline Fallback)",
            is_demo=True,
            fallback_warning=DEMO_WARNING_MESSAGE,
            scene_description="Panoramic outdoor vista with open sky and distant vegetation"
        )

    # Case 4: Centered Yellow Bloom on Foliage (e.g. Dandelion-like composite flower)
    if metrics["center_yellow_ratio"] > 0.08 and metrics["green_ratio"] > 0.20:
        return IdentificationResult(
            identification="Unverified Composite Flower (Asteraceae Candidate)",
            scientific_name="Asteraceae sp. (Candidate)",
            category="flora",
            confidence=0.45,
            confidence_level="uncertain",
            is_confident=False,
            summary=(
                "[ILLUSTRATIVE DEMO HEURISTIC] Visual heuristics detected a yellow floral center on green foliage. "
                "In offline demo mode without a live vision neural network, exact species identification is withheld to prevent false claims."
            ),
            observations=[
                "Check whether the flower head consists of many tiny ligulate florets (like a dandelion) or central disc florets.",
                "Examine the stem: is it hollow, and does it produce milky white latex if bent?",
                "Look for visiting pollinator insects around the yellow florets."
            ],
            outdoor_challenge="Spend 3 minutes observing the flower without your phone. Count how many petal-like florets make up the outer ring.",
            safety_note="Never ingest wild plants or flowers without verified expert botanical identification.",
            screen_break_message="Lock your screen. Spend 3 quiet minutes observing the flower structure.",
            model_used="TrailLens Heuristics Engine (Offline Fallback)",
            is_demo=True,
            fallback_warning=DEMO_WARNING_MESSAGE,
            scene_description="Close-up yellow flower head on foliage background"
        )

    # Case 5: Centered White Bloom on Foliage (e.g. Clover / Daisy candidate)
    if metrics["center_white_ratio"] > 0.08 and metrics["green_ratio"] > 0.20:
        return IdentificationResult(
            identification="Unverified Pale Blossom (Trifolium / Daisy Candidate)",
            scientific_name=None,
            category="flora",
            confidence=0.42,
            confidence_level="uncertain",
            is_confident=False,
            summary=(
                "[ILLUSTRATIVE DEMO HEURISTIC] Visual heuristics detected pale/white floral petals against foliage. "
                "Exact species identification requires a live vision model and is withheld here to prevent fabrication."
            ),
            observations=[
                "Check the surrounding leaves: are they divided into three leaflets with pale watermarks?",
                "Notice if individual florets bloom from the base upward.",
                "Feel the soil moisture around the roots."
            ],
            outdoor_challenge="Search a 1-meter square around this plant for 3 minutes without digital distractions.",
            safety_note="Watch for foraging honeybees whose stingers can be tucked inside clover blossoms.",
            screen_break_message="Screen off. Immerse yourself in the surrounding greenery.",
            model_used="TrailLens Heuristics Engine (Offline Fallback)",
            is_demo=True,
            fallback_warning=DEMO_WARNING_MESSAGE,
            scene_description="Close-up pale or white floral bloom on foliage"
        )

    # Case 6: Dominant Green Foliage / Leaves
    if metrics["green_ratio"] > 0.35:
        # Check if user provided a hint
        hint_label = f" (User Hint: '{user_hint.strip()}')" if user_hint else ""
        return IdentificationResult(
            identification=f"Unclassified Foliage Specimen{hint_label}",
            scientific_name=None,
            category="flora",
            confidence=0.38,
            confidence_level="uncertain",
            is_confident=False,
            summary=(
                "[ILLUSTRATIVE DEMO HEURISTIC] Dominant green foliage detected in the frame. "
                "In offline demo mode without a live vision neural network, exact species classification is withheld to prevent false identification."
            ),
            observations=[
                "Examine whether the leaf margins are smooth (entire), serrated, or deeply lobed.",
                "Check whether leaves are arranged alternately or opposite one another on the branch.",
                "Inspect the underside of a leaf for fine branching veins or subtle color changes."
            ],
            outdoor_challenge="Trace the primary vein of a single leaf and count its secondary branches for 3 quiet minutes.",
            safety_note="Never touch or ingest wild plants with unknown sap or oils.",
            screen_break_message="Put your phone in your pocket. Touch the leaf gently and feel its surface texture.",
            model_used="TrailLens Heuristics Engine (Offline Fallback)",
            is_demo=True,
            fallback_warning=DEMO_WARNING_MESSAGE,
            scene_description="Close-up view of green plant foliage or leaf canopy"
        )

    # Case 7: General / Unclassified Natural Specimen
    return IdentificationResult(
        identification="No confident identification — Unclassified Nature Specimen",
        scientific_name=None,
        category="flora",
        confidence=0.15,
        confidence_level="uncertain",
        is_confident=False,
        summary=(
            "The image contains natural textures, but TrailLens did not find sufficient distinctive visual markers to propose a reliable classification. "
            "To prevent false identifications, no species is asserted."
        ),
        observations=[
            "Move closer to the primary subject so it occupies at least 60% of the camera frame.",
            "Ensure the natural subject is well-lit and in crisp focus.",
            "Look for distinctive diagnostic features such as flower petals, leaf margins, or bark furrows."
        ],
        outdoor_challenge="Spend 3 minutes looking closely at this natural subject with your own eyes and notice three physical details you missed on the screen.",
        safety_note="Do not consume or handle wild specimens without certified botanical identification.",
        screen_break_message="Put your phone away. Step closer and observe the organism in real life.",
        model_used="TrailLens Heuristics Engine (Offline Fallback)",
        is_demo=True,
        fallback_warning=DEMO_WARNING_MESSAGE,
        scene_description="Natural textures without a single distinct diagnostic macro organism"
    )
