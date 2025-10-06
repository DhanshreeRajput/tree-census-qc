from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import math
import os

app = Flask(__name__)
# Enable CORS for all routes to allow frontend connection
CORS(app)

# Species-to-coefficients mapping: height = a*(DBH^b), canopy = c*(DBH^d)
species_coeffs = {
    "Silver maple": {"height": (1.50, 1.778), "canopy": (0.82, 1.995)},
    "Ginkgo": {"height": (1.71, 1.465), "canopy": (0.63, 1.989)},
    "Oak": {"height": (1.30, 1.50), "canopy": (0.70, 1.20)},
    "Maple": {"height": (1.50, 1.70), "canopy": (0.80, 2.00)},
    "Pine": {"height": (0.80, 1.25), "canopy": (0.50, 1.40)},
    "Default": {"height": (1.00, 1.200), "canopy": (0.50, 1.500)}
}

@app.route('/qc', methods=['POST'])
def qc():
    """
    QC endpoint to estimate tree metrics from trunk image.
    
    Expected JSON payload:
    {
        "image_path": "/path/to/trunk.jpg",
        "species": "Species Name"
    }
    
    Returns:
    {
        "dbh": float,      # Diameter at breast height (cm)
        "girth": float,    # Circumference (cm)
        "height": float,   # Estimated height (m)
        "canopy": float    # Estimated canopy width (m)
    }
    """
    data = request.get_json() or {}
    image_path = data.get('image_path')
    species = data.get('species', "Default")
    
    if not image_path:
        return jsonify(error="No image_path provided"), 400
    
    # Check if file exists
    if not os.path.exists(image_path):
        return jsonify(error=f"Image not found: {image_path}"), 400

    # Load the image
    image = cv2.imread(image_path)
    if image is None:
        return jsonify(error="Failed to load image"), 400

    # Preprocess: convert to grayscale and detect edges
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Detect edges using Canny
    edges = cv2.Canny(blurred, 100, 200)

    # Find contours and select the largest (assumed tree trunk)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        return jsonify(error="No trunk contour found in image"), 400
    
    # Get the largest contour
    trunk_contour = max(contours, key=cv2.contourArea)

    # Compute minimum enclosing circle to estimate trunk diameter in pixels
    (x, y), radius = cv2.minEnclosingCircle(trunk_contour)
    pixel_diameter = 2 * radius

    # Convert pixel diameter to centimeters
    # NOTE: This is a calibration factor that should be adjusted based on:
    # - Camera distance from tree
    # - Known reference object in image
    # - Camera specifications
    scale_cm_per_pixel = 0.1  # [cm/px] - CALIBRATE THIS VALUE
    dbh_cm = pixel_diameter * scale_cm_per_pixel

    # Compute girth (circumference)
    girth_cm = math.pi * dbh_cm

    # Get species coefficients (or default if missing)
    coeffs = species_coeffs.get(species, species_coeffs["Default"])
    a_h, b_h = coeffs["height"]
    a_c, b_c = coeffs["canopy"]

    # Calculate height and canopy using allometric equations
    # Height and canopy formulas: metric = coefficient_a * (DBH ^ coefficient_b)
    height_m = a_h * (dbh_cm ** b_h)
    canopy_m = a_c * (dbh_cm ** b_c)

    # Return rounded results
    return jsonify({
        "dbh": round(dbh_cm, 1),      # cm
        "girth": round(girth_cm, 1),  # cm
        "height": round(height_m, 1), # m
        "canopy": round(canopy_m, 1)  # m
    })

@app.route('/species', methods=['GET'])
def get_species():
    """Return list of available species with coefficients."""
    return jsonify({
        "species": list(species_coeffs.keys()),
        "coefficients": species_coeffs
    })

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "service": "Tree Census QC Tool"})

if __name__ == '__main__':
    print("Starting Tree Census QC Service...")
    print("Available species:", list(species_coeffs.keys()))
    print("\nEndpoints:")
    print("  POST /qc       - Process tree image")
    print("  GET  /species  - List available species")
    print("  GET  /health   - Health check")
    print("\nCORS enabled - Frontend can connect from any origin")
    app.run(debug=True, host='0.0.0.0', port=5000)