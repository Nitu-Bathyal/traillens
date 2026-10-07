# Real-World Outdoor Test Checklist

Use this protocol to verify TrailLens on a real outdoor trail, city park, botanical garden, or backyard nature walk.

> **Honesty Notice:** In accordance with Hacktoberfest integrity guidelines, this checklist is provided for explorers and evaluators to execute in a live natural setting. Do not mark items complete until physically performed in the field.

---

## Pre-Trail Preparation
- [ ] Charge mobile device to at least 50%.
- [ ] Open TrailLens in a mobile browser (Chrome / Safari / Firefox) at the live Render URL or local tunnel.
- [ ] Confirm the PWA manifest and service worker load (look for the "Online" status pill).
- [ ] Enable location permissions only if you wish to record coarse coordinates with observations.
- [ ] Set device volume to an audible level for the "Listen" voice narration and 432Hz ambient chime.

---

## 10-Step Field Protocol

| Step | Action | Expected Result | Verified? |
|---|---|---|---|
| **1** | Step outdoors into natural ambient light. | Screen remains legible due to high-contrast outdoor UI styling. | [ ] |
| **2** | Locate an interesting wild specimen (flower, leaf, tree bark, fungus, or insect). | Specimen is clearly visible within 0.5 to 1.5 meters. | [ ] |
| **3** | Tap **[ Choose or Take Photo ]** and capture the specimen using your phone camera. | Image preview renders immediately in the card. | [ ] |
| **4** | Tap **[ Analyze & Step Away ]**. | Open-weight vision AI processes the image and returns common name, Latin binomial, and confidence score. | [ ] |
| **5** | Tap **[ Listen ]** to hear the audio cue. | Spoken narration reads the primary identification and immediately instructs you to put the phone away. | [ ] |
| **6** | Read the **3 Micro-Observations** and the **Outdoor Challenge**. | Challenge provides a clear 2–5 minute physical task requiring zero digital interaction. | [ ] |
| **7** | Tap **[ Step Away / Put Phone Away ]**. | Fullscreen Step Away Mode activates, starts a 3-minute countdown ring, and begins optional ambient chimes. | [ ] |
| **8** | Slide the phone into your pocket or place it face-down on a bench or dry ground. | **Phone is completely out of sight. No screens are looked at.** | [ ] |
| **9** | Perform the challenge with your eyes, ears, hands, and attention. | Notice tactile bark furrows, count petal veins, or track an insect's path across leaf litter. | [ ] |
| **10** | When the countdown finishes, take your phone out, tap **[ I Observed This ]**, and tap **[ Save Observation ]**. | Specimen appears in your **Field Journal** with timestamp and sync badge. | [ ] |

---

## Offline Resilience Verification
- [ ] Toggle device into **Airplane Mode** while outdoors.
- [ ] Confirm the status badge updates to **"Offline Trail"**.
- [ ] Capture a new observation and save it.
- [ ] Verify that the item shows as **"Saved Offline"** and the sync queue increments.
- [ ] Turn Airplane Mode off.
- [ ] Tap **[ Sync Now ]** on the banner and confirm the observation transitions to **"Synced"**.

---

## Field Notes & Observations
*Date & Time of Test:* ________________________  
*Location (Park / Trail / Garden):* ________________________  
*Weather Conditions:* Temperature: ______°C, Sky: ____________  
*Species Encountered:* ________________________  
*Sensory Details Discovered:* ________________________  
