import hashlib
from typing import Optional, List, Dict, Any
from PIL import Image
from app.ai.base import AIProvider
from app.models.observation import IdentificationResult


DEMO_SPECIES_CATALOG: List[Dict[str, Any]] = [
    {
        "identification": "Common Dandelion",
        "scientific_name": "Taraxacum officinale",
        "category": "flora",
        "confidence": 0.88,
        "confidence_level": "high",
        "summary": "A ubiquitous composite flower in the Asteraceae family. Its bright yellow head consists of hundreds of tiny ligulate florets that track the sun across the morning sky.",
        "observations": [
            "Count or estimate the jagged tooth-like lobes on a lower leaf (the French 'dent-de-lion').",
            "Notice whether the stem exudes a bitter white milky latex if gently bent.",
            "Look for any small hoverflies or solitary bees visiting the yellow florets."
        ],
        "outdoor_challenge": "Spend 3 minutes finding two dandelions in different stages of bloom (yellow flower vs spherical seed clock) and notice how the stems differ in length.",
        "safety_note": "While dandelions are historically edible, never consume plants gathered near roadsides or lawns that may be treated with chemical pesticides.",
        "screen_break_message": "Put your phone in your pocket. Kneel down close to the flower for 3 minutes without digital distractions."
    },
    {
        "identification": "White Clover",
        "scientific_name": "Trifolium repens",
        "category": "flora",
        "confidence": 0.82,
        "confidence_level": "high",
        "summary": "A nitrogen-fixing herbaceous perennial native to Europe and widely naturalized. Its trifoliate leaves often have a faint pale 'V' watermark.",
        "observations": [
            "Check for the distinctive white chevron or crescent watermark on each of the three leaflets.",
            "Examine the flower head to see individual tubular florets blooming from bottom to top.",
            "Touch the soil around the creeping stolon runners anchoring the plant."
        ],
        "outdoor_challenge": "Search a 1-meter square patch of grass for 4 minutes to see if any leaf has an unusual four leaflets. Breathe in the cool outdoor air.",
        "safety_note": "Harmless wild clover, but watch for foraging honeybees whose stingers can be hidden among the white heads.",
        "screen_break_message": "Lock your screen. Feel the cool turf beneath your fingers for 3 minutes."
    },
    {
        "identification": "Turkey Tail Fungus",
        "scientific_name": "Trametes versicolor",
        "category": "fungi",
        "confidence": 0.74,
        "confidence_level": "moderate",
        "summary": "A common polypore shelf fungus found on decaying hardwood logs worldwide, featuring concentric multicolored bands resembling a wild turkey's plumage.",
        "observations": [
            "Inspect the underside of the bracket — true turkey tail has tiny pores (3-8 per mm), not gills.",
            "Trace the concentric velvet and satin bands of varying browns, creams, and steely blues.",
            "Check how flexible the thin fruiting body feels without ripping it from the wood."
        ],
        "outdoor_challenge": "Look around the surrounding fallen log for 5 minutes to see what mosses, beetles, or woodlice share this decomposer ecosystem.",
        "safety_note": "Wild mushrooms must NEVER be ingested without certified mycological expert verification. Many shelf fungi look similar.",
        "screen_break_message": "Step back from your screen. Let your eyes adjust to the forest floor shadows for 5 quiet minutes."
    },
    {
        "identification": "English Oak Leaf",
        "scientific_name": "Quercus robur",
        "category": "flora",
        "confidence": 0.85,
        "confidence_level": "high",
        "summary": "The signature deciduous tree of temperate broadleaf forests. Characterized by deeply lobed leaves with very short stalks (petioles) and small ear-like auricles at the base.",
        "observations": [
            "Count the rounded lobe pairs on the leaf margin (typically 4 to 7 pairs).",
            "Look for small oak marble galls or silk button galls formed by tiny cynipid wasps.",
            "Inspect the underside of the leaf for subtle paler green coloration and fine branching veins."
        ],
        "outdoor_challenge": "Step 5 paces back from the tree trunk. Look up into the canopy silhouette against the sky and track the path of three major boughs.",
        "safety_note": "Oak acorns contain tannins that are astringent and raw acorns are toxic to pets and humans in quantity.",
        "screen_break_message": "Pocket your phone now. Stand under the canopy and listen to the wind rustling through the boughs."
    },
    {
        "identification": "European Honeybee on Blossom",
        "scientific_name": "Apis mellifera",
        "category": "fauna",
        "confidence": 0.89,
        "confidence_level": "high",
        "summary": "A eusocial pollinator visiting flowers to collect nectar and protein-rich pollen, playing an indispensable role in wild floral biodiversity.",
        "observations": [
            "Watch the hind legs (corbiculae or pollen baskets) to see if bright yellow or orange pollen pellets are packed there.",
            "Observe the rapid flight cadence between adjacent blooms without disturbing the bee.",
            "Listen closely to the low-frequency hum produced by the bee's flight muscles."
        ],
        "outdoor_challenge": "Keep a respectful 1-meter distance. Follow one bee as it visits 5 consecutive flowers without checking your phone or moving abruptly.",
        "safety_note": "Keep a calm, steady posture. Honeybees are gentle when foraging and will not sting unless threatened or pinched.",
        "screen_break_message": "Phone away! Stand completely motionless for 3 minutes and let the garden sounds fill your focus."
    },
    {
        "identification": "Crustose Lichen on Granite",
        "scientific_name": "Lecanora muralis complex",
        "category": "geology",
        "confidence": 0.70,
        "confidence_level": "moderate",
        "summary": "A symbiotic composite organism formed by fungi and photosynthetic algae or cyanobacteria, clinging tightly to mineral surfaces and indicating clean air.",
        "observations": [
            "Feel the rough contrast between the bare stone surface and the crusty lichen thallus.",
            "Notice the miniature bullseye or rosette growth rings spreading outward from the center.",
            "Check which side of the rock faces the prevailing weather or sunlight."
        ],
        "outdoor_challenge": "Find three different colored patches of lichen on nearby stones or trees (yellow, pale green, grey-white) without touching your device.",
        "safety_note": "Be careful when walking over damp lichen-covered rocks as they can become extremely slippery.",
        "screen_break_message": "Put your phone away. Run your fingers over the cool stone and contemplate the decades this lichen took to grow."
    }
]


class DemoAIProvider(AIProvider):
    """
    Deterministic offline AI provider.
    Runs 100% locally with zero external network connectivity.
    Ideal for local demos, offline trails, and judge evaluation without API tokens.
    """

    @property
    def name(self) -> str:
        return "demo"

    @property
    def model_name(self) -> str:
        return "TrailLens-Demo-Engine (Offline Heuristics & Curated Taxonomy)"

    @property
    def license(self) -> str:
        return "Apache 2.0 / Open Source"

    @property
    def is_offline(self) -> bool:
        return True

    async def identify(
        self,
        image: Image.Image,
        user_hint: Optional[str] = None
    ) -> IdentificationResult:
        # Generate deterministic selection based on image thumb perceptual hash
        thumb = image.resize((8, 8)).convert("L")
        pixel_bytes = thumb.tobytes()
        hash_digest = hashlib.sha256(pixel_bytes).hexdigest()
        index = int(hash_digest[:4], 16) % len(DEMO_SPECIES_CATALOG)

        data = DEMO_SPECIES_CATALOG[index]

        return IdentificationResult(
            identification=data["identification"],
            scientific_name=data["scientific_name"],
            category=data["category"],
            confidence=data["confidence"],
            confidence_level=data["confidence_level"],
            summary=data["summary"],
            observations=data["observations"],
            outdoor_challenge=data["outdoor_challenge"],
            safety_note=data["safety_note"],
            screen_break_message=data["screen_break_message"],
            model_used=self.model_name,
            is_demo=True
        )
