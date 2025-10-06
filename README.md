# Tree Census QC Tool

An automated tree measurement system using computer vision to estimate tree metrics from trunk images. This Flask-based API uses OpenCV to calculate DBH (Diameter at Breast Height), girth, and estimates tree height and canopy width using allometric equations.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [API Documentation](#api-documentation)
- [Usage Examples](#usage-examples)
- [Supported Species](#supported-species)
- [Calibration Guide](#calibration-guide)
- [Image Requirements](#image-requirements)
- [Troubleshooting](#troubleshooting)
- [Project Structure](#project-structure)

---

## Overview

The Tree Census QC Tool processes tree trunk images to automatically estimate tree dimensions. It uses edge detection to measure trunk diameter in pixels, converts to physical units, and applies allometric equations to estimate tree height and canopy width.

**How it works:**
1. Load image and detect trunk edges using OpenCV
2. Find largest contour (assumed to be trunk)
3. Calculate pixel diameter 
4. Convert to centimeters using calibration factor
5. Apply species-specific formulas to estimate height and canopy

---

## Features

- Automated DBH measurement from trunk images
- Species-specific height and canopy estimation
- RESTful API with JSON responses
- Web-based test interface
- CORS enabled for frontend connections
- Support for 6 tree species with extensible coefficients

---

## Requirements

**System:**
- Python 3.7 or higher
- Modern web browser for test interface

**Python Dependencies:**
```
flask>=2.0.0
flask-cors>=3.0.10
opencv-python>=4.5.0
numpy>=1.19.0
```

---

## Installation

### Step 1: Install Dependencies

```bash
pip install flask flask-cors opencv-python numpy
```

Or create `requirements.txt`:
```txt
flask>=2.0.0
flask-cors>=3.0.10
opencv-python>=4.5.0
numpy>=1.19.0
```

Then install:
```bash
pip install -r requirements.txt
```

### Step 2: Verify Installation

```bash
python Flaskapp_Tree_Cencus.py
```

Expected output:
```
Starting Tree Census QC Service...
Available species: ['Silver maple', 'Ginkgo', 'Oak', 'Maple', 'Pine', 'Default']

Endpoints:
  POST /qc       - Process tree image
  GET  /species  - List available species
  GET  /health   - Health check

CORS enabled - Frontend can connect from any origin
 * Running on http://0.0.0.0:5000
```

---

## Quick Start

### 1. Start the Server

```bash
python Flaskapp_Tree_Cencus.py
```

Server runs on `http://127.0.0.1:5000`

**Test the API is running:**
Open in browser: `http://127.0.0.1:5000/health`

### 2. Open Test Interface

**Option A: Double-click the file**
- Navigate to your project folder
- Double-click `test_page_tree.html`
- It will open in your default browser

**Option B: Command line**
```bash
# macOS/Linux
open test_page_tree.html

# Windows
start test_page_tree.html
```

**Option C: Direct browser**
- Open your browser
- Press `Ctrl+O` (or `Cmd+O` on Mac)
- Navigate to the project folder
- Select `test_page_tree.html`

The test interface will be available at `file:///your-path/test_page_tree.html`

### 3. Test with Sample Images

The interface includes quick-select buttons for the sample images in the `Images/` folder:
- Pine
- Oak  
- Maple
- Ginkgo
- Silver Maple

Click a button to auto-fill the image path and species, then click "Run QC Analysis".

### 4. Test via Command Line

```bash
curl -X POST http://127.0.0.1:5000/qc \
  -H "Content-Type: application/json" \
  -d '{"image_path": "Images/pine trunk.jpg", "species": "Pine"}'
```

---

## API Documentation

### Base URL
```
http://127.0.0.1:5000
```

### Endpoints

#### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "Tree Census QC Tool"
}
```

---

#### GET /species
Returns available species and their coefficients.

**Response:**
```json
{
  "species": ["Silver maple", "Ginkgo", "Oak", "Maple", "Pine", "Default"],
  "coefficients": {
    "Oak": {
      "height": [1.30, 1.50],
      "canopy": [0.70, 1.20]
    }
  }
}
```

---

#### POST /qc
Main endpoint to analyze tree trunk image.

**Request:**
```json
{
  "image_path": "Images/oak trunk.jpg",
  "species": "Oak"
}
```

**Success Response (200):**
```json
{
  "dbh": 45.3,      // Diameter at breast height (cm)
  "girth": 142.3,   // Circumference (cm)
  "height": 18.7,   // Estimated height (m)
  "canopy": 12.4    // Estimated canopy width (m)
}
```

**Error Responses:**
```json
// 400 - Missing image path
{"error": "No image_path provided"}

// 400 - File not found
{"error": "Image not found: /path/to/image.jpg"}

// 400 - Failed to load
{"error": "Failed to load image"}

// 400 - No contour detected
{"error": "No trunk contour found in image"}
```

---

## Usage Examples

### Python

```python
import requests

response = requests.post('http://127.0.0.1:5000/qc', json={
    'image_path': 'Images/oak trunk.jpg',
    'species': 'Oak'
})

if response.status_code == 200:
    data = response.json()
    print(f"DBH: {data['dbh']} cm")
    print(f"Height: {data['height']} m")
    print(f"Canopy: {data['canopy']} m")
```

### cURL

```bash
curl -X POST http://127.0.0.1:5000/qc \
  -H "Content-Type: application/json" \
  -d '{"image_path": "Images/maple tree trunk.jpg", "species": "Maple"}'
```

### JavaScript

```javascript
fetch('http://127.0.0.1:5000/qc', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    image_path: 'Images/pine trunk.jpg',
    species: 'Pine'
  })
})
.then(response => response.json())
.then(data => console.log(data));
```

---

## Supported Species

| Species | Height Formula | Canopy Formula |
|---------|---------------|----------------|
| Silver maple | Height = 1.50 × (DBH^1.778) | Canopy = 0.82 × (DBH^1.995) |
| Ginkgo | Height = 1.71 × (DBH^1.465) | Canopy = 0.63 × (DBH^1.989) |
| Oak | Height = 1.30 × (DBH^1.50) | Canopy = 0.70 × (DBH^1.20) |
| Maple | Height = 1.50 × (DBH^1.70) | Canopy = 0.80 × (DBH^2.00) |
| Pine | Height = 0.80 × (DBH^1.25) | Canopy = 0.50 × (DBH^1.40) |
| Default | Height = 1.00 × (DBH^1.200) | Canopy = 0.50 × (DBH^1.500) |

### Adding New Species

Edit `Flaskapp_Tree_Cencus.py` and add to `species_coeffs`:

```python
species_coeffs = {
    "Your Species": {
        "height": (a_height, b_height),
        "canopy": (a_canopy, b_canopy)
    },
    # ... existing species
}
```

---

## Calibration Guide

### CRITICAL: The Scale Factor

Line 62 in `Flaskapp_Tree_Cencus.py` contains:
```python
scale_cm_per_pixel = 0.1  # CALIBRATE THIS VALUE
```

This value **MUST be calibrated** for your specific setup. Without proper calibration, measurements will be inaccurate.

### Why Calibration Matters

**Symptoms of incorrect calibration:**
- Trees showing 60-150 meter heights (impossible)
- DBH values that don't match reality
- Unrealistic canopy widths

**Example from your test results:**
```
Pine: DBH 8.3 cm → Height 64.7 m (should be ~15-20m)
Maple: DBH 11.5 cm → Height 95 m (should be ~20-25m)
```

These indicate the scale factor is incorrect for your images.

### How to Calibrate

#### Method 1: Known Reference Object (Recommended)

1. Place a measuring tape on the trunk (e.g., 30 cm marker visible)
2. Take photo at same distance as measurement photos
3. Measure the 30 cm in pixels using image software
4. Calculate: `scale = 30 cm / pixel_width`

**Example:**
```python
# If 30 cm measures 300 pixels
scale_cm_per_pixel = 30 / 300 = 0.1

# If 30 cm measures 150 pixels  
scale_cm_per_pixel = 30 / 150 = 0.2

# If 30 cm measures 60 pixels
scale_cm_per_pixel = 30 / 60 = 0.5
```

#### Method 2: Known DBH

1. Manually measure tree DBH with tape measure at 1.3-1.5m height
2. Take photo and run through system
3. Note the pixel diameter detected
4. Calculate: `scale = actual_DBH_cm / pixel_diameter`

**Example:**
```python
# Actual DBH: 45 cm, System detected 450 pixels
scale_cm_per_pixel = 45 / 450 = 0.1

# Actual DBH: 30 cm, System detected 100 pixels
scale_cm_per_pixel = 30 / 100 = 0.3
```

#### Method 3: Camera Formula

If you know camera specs:
```python
scale = (distance_mm × sensor_width_mm) / (focal_length_mm × image_width_px)
```

### Update the Code

After calculating, update line 62:
```python
scale_cm_per_pixel = 0.3  # Your calculated value
```

---

## Image Requirements

### What Works Best

**Photo Guidelines:**
- Take photo at breast height (1.3-1.5m above ground)
- Distance: 1-3 meters from trunk
- Trunk fills 40-70% of frame
- Straight-on view (perpendicular)
- Clear background visible
- Even lighting (overcast is ideal)
- Sharp focus
- Minimum 800×600 pixels
- Straight trunk section (not branch junctions)

**Good Image Checklist:**
```
✓ Trunk centered in frame
✓ Clear edges against background
✓ No other objects touching trunk
✓ Even lighting
✓ Cylindrical section visible
✓ Sharp focus
```

### What Doesn't Work

**Avoid:**
- Branch junctions (Y-shaped areas)
- Extreme close-ups showing only bark texture
- Images too far away (trunk too small)
- Angled shots (looking up/down)
- Multiple trees overlapping
- Heavy shadows across trunk
- Blurry images
- Complex backgrounds with vegetation

**Your Sample Images:**

The images in your `Images/` folder should be:
- Full trunk sections at breast height
- NOT extreme bark close-ups
- NOT branch junction areas

If you're getting unrealistic measurements (trees 60-150m tall), your images may be extreme close-ups rather than full trunk sections.

---

## Troubleshooting

### Server Issues

**Problem: Port already in use**
```bash
# Kill process on port 5000
lsof -ti:5000 | xargs kill -9

# Or change port in code:
app.run(debug=True, host='0.0.0.0', port=5001)
```

**Problem: Connection refused**
- Ensure Flask server is running
- Check URL is `http://127.0.0.1:5000`
- Verify firewall settings

---

### Image Processing Issues

**Problem: "No trunk contour found"**

**Solutions:**
- Use sharper, focused image
- Ensure clear background
- Adjust edge detection thresholds (line 53):
```python
# For subtle edges (smooth bark):
edges = cv2.Canny(blurred, 50, 150)

# Current default:
edges = cv2.Canny(blurred, 100, 200)

# For rough bark:
edges = cv2.Canny(blurred, 150, 250)
```

**Problem: Unrealistic measurements**

**Cause:** Incorrect calibration or wrong image type

**Solutions:**
1. **Calibrate properly** (see Calibration Guide)
2. Use full trunk images, not bark close-ups
3. Use images taken at correct distance (1-3m)
4. Verify images show straight trunk sections

---

### Understanding Your Results

**Realistic ranges for common trees:**

| Species | DBH Range | Height Range | Canopy Range |
|---------|-----------|--------------|--------------|
| Young trees | 10-30 cm | 5-15 m | 3-8 m |
| Mature trees | 30-80 cm | 15-30 m | 8-20 m |
| Old trees | 80+ cm | 25-40 m | 15-30 m |

**If you see:**
- Heights > 50m for Oak/Maple/Ginkgo → Calibration error
- DBH < 5 cm → Using extreme close-up images
- Canopy > 50m → Wrong scale factor

---

## Project Structure

```
TREE-CENSUS-QC/
│
├── Images/                        # Sample tree trunk images
│   ├── Ginkgo trunk.jpg
│   ├── maple tree trunk.jpg
│   ├── Oak trunk.jpg
│   ├── pine trunk.jpg
│   └── silver maple.jpg
│
├── Flaskapp_Tree_Cencus.py       # Main Flask API server
├── test_page_tree.html            # Web test interface
├── README.md                      # This file
└── requirements.txt               # Python dependencies
```

---

## Technical Details

### Computer Vision Pipeline

1. **Preprocessing:**
   - Convert to grayscale
   - Apply Gaussian blur (5×5 kernel)
   
2. **Edge Detection:**
   - Canny edge detection (thresholds: 100, 200)
   
3. **Contour Analysis:**
   - Find external contours
   - Select largest by area
   - Compute minimum enclosing circle
   
4. **Measurement:**
   - Pixel diameter = 2 × radius
   - DBH (cm) = pixel_diameter × scale_cm_per_pixel
   - Girth (cm) = π × DBH

### Allometric Equations

```python
Height (m) = a_h × (DBH^b_h)
Canopy (m) = a_c × (DBH^b_c)
```

Where coefficients (a, b) are species-specific values derived from forestry research.

### Adjustable Parameters

**Edge Detection (line 53):**
```python
edges = cv2.Canny(blurred, threshold1, threshold2)
# Lower = more sensitive, Higher = more selective
```

**Blur (line 50):**
```python
blurred = cv2.GaussianBlur(gray, (kernel, kernel), 0)
# Larger kernel = more noise reduction
```

**Scale Factor (line 62):**
```python
scale_cm_per_pixel = 0.1  # MUST BE CALIBRATED
```

---

## Known Limitations

1. **Requires calibration** - Scale factor must be set for each camera/distance setup
2. **Works best on straight trunks** - Branch junctions produce poor results
3. **Needs clear backgrounds** - Complex vegetation interferes with edge detection
4. **Single trunk only** - Cannot handle multiple overlapping trees
5. **Lighting sensitive** - Harsh shadows create false edges
6. **Image quality dependent** - Blurry images fail to detect edges properly

---

## License

MIT License - Feel free to use and modify for your projects.

---

## Support

For issues or questions:
1. Check the Troubleshooting section
2. Verify your calibration is correct
3. Ensure images meet the requirements
4. Review the test results for realistic values

---

**Version:** 1.0  
**Last Updated:** 2024