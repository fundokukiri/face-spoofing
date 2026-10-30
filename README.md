# Face Spoofing Detection - FacePay

Student project (2020) researching and building a Face Anti-Spoofing system combined with Face Recognition to create a demo payment application called FacePay.

The system distinguishes between real faces and spoofing attempts (printed photos, video replay, 3D masks) to protect face recognition systems.

---

## Project Goals

1. Face Anti-Spoofing: Detect fake faces (spoofing) using an ONNX model
2. Face Recognition: Identity verification using FaceNet + ArcFace
3. FacePay Demo: Web application simulating face-based payment (liveness check + face recognition)

---

## System Architecture

```
FacePay/
├── app.py                 # Flask app entry point
├── train.py               # Train FaceNet classifier (SVM)
├── test.py                # Simple camera test
├── FacePay/
│   ├── __init__.py        # Initialize Flask app, load models
│   ├── func.py            # Core logic: face detection, recognition, anti-spoofing
│   ├── views.py           # Flask routes: video feed, checkout, register
│   ├── users.py           # Auth: sign up, sign in, logout
│   ├── model.py           # SQLAlchemy models (Users, PurchaseHistory, etc.)
│   ├── facepay.db         # SQLite database
│   ├── facetools/         # Computer vision modules
│   │   ├── face_detection.py    # MediaPipe FaceMesh + Head Pose Estimation
│   │   ├── face_antispoofing.py # ONNX Runtime inference (liveness)
│   │   └── utils.py             # Visualization, face extraction
│   ├── Models/            # Model weights
│   │   ├── FaceNet_Model.pb        # FaceNet frozen graph (TensorFlow)
│   │   ├── FaceNet_Model.pkl       # SVM classifier + class names
│   │   └── AntiSpoofing_bin_1.5_128.onnx  # Anti-spoofing ONNX model
│   ├── static/
│   │   ├── Data/
│   │   │   ├── FaceNet/            # FaceNet training data (organized by user)
│   │   │   └── ArcFace/            # Reference images for ArcFace verification
│   │   ├── css/, js/, images/      # Frontend assets
│   │   └── user_img_temp/          # Temp frames
│   └── templates/         # Jinja2 HTML templates
```

---

## Architecture and Data Flow

### High-Level Architecture

The system follows a modular pipeline architecture with three main layers:

**Presentation Layer (Flask Web Application)**
- Jinja2 templates render HTML pages
- MJPEG video streaming via Flask Response objects
- Blueprint-based routing (views, users)
- Session management with Flask-Login

**Business Logic Layer (func.py)**
- Orchestrates the computer vision pipeline
- Loads and manages ML models at startup (FaceNet, SVM, ArcFace, Anti-Spoofing)
- Provides stateless functions for detection, recognition, and liveness checking
- Handles thresholds and decision logic

**Computer Vision Layer (facetools/)**
- Face Detection: MediaPipe FaceMesh for 468 landmarks + Head Pose Estimation via solvePnP
- Anti-Spoofing: ONNX Runtime inference on 128x128 padded crops
- Face Recognition: FaceNet (TF1 frozen graph) for 512-d embeddings + SVM classification; optional ArcFace verification
- Utilities: Face extraction with margin, visualization helpers

**Data Layer (SQLite + File System)**
- SQLite database for users, transactions, sign-in history
- File-based storage for training images (FaceNet) and reference images (ArcFace)
- Model weights stored as .pb, .onnx, .pkl files

### Data Flow: Checkout (Payment) Pipeline

```
User adds items to cart (POST / with total-price, data-purchase)
         │
         ▼
    Redirect to /checkout
         │
         ▼
Client loads checkout.html → requests /video_feed (MJPEG stream)
         │
         ▼
gen_frames_checkout() runs continuous loop:
  1. Camera capture (cv2.VideoCapture)
  2. Face Detection (MediaPipe FaceMesh) → face crops + bounding boxes
  3. Anti-Spoofing per face (ONNX model) → REAL/FAKE score
  4. If REAL: Face Recognition
       a. FaceNet embedding (TF1 graph) → 512-d vector
       b. SVM classifier → predicted user + probability
       c. If prob > 0.6: optional ArcFace verification
  5. Visualization overlay on frame
  6. Encode JPEG → yield MJPEG chunk
         │
         ▼
Browser displays live video with overlays
         │
         ▼
When recognition succeeds (recognize_id set globally):
  Home route (/) detects recognize_id + money > 0
  → Validates user exists + sufficient balance
  → Deducts currency, creates PurchaseHistory record
  → Flash success message
  → Resets global state (recognize_id, money, data_cart)
```

### Data Flow: Face Registration Pipeline

```
User clicks "Add Face" in /account → redirect to /face_register
         │
         ▼
Client loads face_register.html → requests /video_feed_register
         │
         ▼
gen_frames_register() runs continuous loop:
  1. Camera capture
  2. Face Detection + Head Pose Estimation (5 poses: Up, Down, Left, Right, Forward)
  3. Anti-Spoofing check (must be REAL)
  4. SuggestPoseCounter guides user through 5 poses × 50 frames each = 250 images
  5. Images saved to FacePay/static/Data/FaceNet/{user_id}/
  6. On completion: saves 1 reference frame to FacePay/static/Data/ArcFace/{user_id}/temp.jpg
         │
         ▼
Admin runs: python train.py
         │
         ▼
train.py:
  1. Loads all images from FaceNet directory
  2. FaceNet forward pass → embeddings for all images
  3. Trains SVM (linear kernel, probability=True)
  4. Saves (model, class_names) to FaceNet_Model.pkl
  5. Copies to production Models/ directory
```

### Model Loading and Initialization

At Flask app creation (`FacePay/__init__.py`):
1. `create_app()` initializes Flask, SQLAlchemy, LoginManager
2. Registers blueprints (views, users)
3. At module import in `func.py` (triggered by views import):
   - Loads SVM classifier from `FaceNet_Model.pkl`
   - Creates TF1 session, loads FaceNet frozen graph (`FaceNet_Model.pb`)
   - Gets input/embedding/phase tensors by name
   - Initializes ArcFace detector
   - Initializes AntiSpoof ONNX session (CUDA if available)
   - Initializes MediaPipe FaceMesh detector
4. First request to `/` runs warm-up inference on a test image

### Key Configuration Parameters

Located in `func.py`:
- `threshold = 0.5` — Anti-spoofing decision boundary
- `probabilitiesFaceNet = 0.6` — SVM confidence threshold for recognition
- `probabilitiesArcFace = 0.8` — ArcFace distance threshold (lower = stricter)
- `ArcFaceActivate = False` — Toggle ArcFace second-factor verification

---

## Technology Stack

| Component | Technology/Library |
|-----------|-------------------|
| Web Framework | Flask, Flask-SQLAlchemy, Flask-Login |
| Face Detection | MediaPipe FaceMesh |
| Face Recognition | FaceNet (TensorFlow 1.x frozen graph) + ArcFace |
| Anti-Spoofing (Liveness) | ONNX Runtime (model: AntiSpoofing_bin_1.5_128.onnx) |
| Classifier | scikit-learn SVM (Linear kernel, probability=True) |
| Database | SQLite |
| Video Stream | OpenCV (cv2.VideoCapture) + MJPEG streaming |
| Head Pose Estimation | OpenCV solvePnP + RQDecomp3x3 |

---

## Core Modules

### 1. Face Detection (`facetools/face_detection.py`)
- Uses MediaPipe FaceMesh (max 1 face)
- Extracts 468 landmarks
- Head Pose Estimation: Calculates head rotation angles (LookUp, LookDown, LookLeft, LookRight, Forward) using cv2.solvePnP
- Crops and aligns face with margin for recognition

### 2. Anti-Spoofing (`facetools/face_antispoofing.py`)
- ONNX model: AntiSpoofing_bin_1.5_128.onnx
- Input: 128x128 RGB (padding + resize keeping aspect ratio)
- Output: 2 classes [Real, Fake] with softmax
- Default threshold: 0.5

### 3. Face Recognition (`func.py`)
**Two-step pipeline:**
1. FaceNet (Embedding + SVM):
   - FaceNet frozen graph (FaceNet_Model.pb) → 512-d embedding
   - SVM classifier (FaceNet_Model.pkl) → predicted class + probability
   - FaceNet threshold: 0.6

2. ArcFace Verification (Optional):
   - Compares real-time embedding with reference image (ArcFace/{user}/temp.jpg)
   - Distance threshold: 0.8
   - Only enabled when ArcFaceActivate=True

### 4. Face Registration (`views.py:gen_frames_register`)
- Requires user to perform 5 poses: LookUp, LookDown, LookLeft, LookRight, Forward
- Each pose: 50 images → total 250 images/user for FaceNet training
- Saves 1 reference image for ArcFace at ArcFace/{id}/temp.jpg

### 5. Checkout Flow (`views.py`)
1. User adds to cart → POST / with total-price, data-purchase
2. Redirect /checkout → stream video from webcam
3. Real-time: Anti-Spoofing + Face Recognition per frame
4. If recognition succeeds & balance sufficient → deduct money, save PurchaseHistory
5. Flash message with result

---

## How to Run

### Requirements
- Python 3.7+ (TensorFlow 1.x compatibility)
- Webcam
- GPU (recommended) for TensorFlow/ONNX Runtime CUDA

### Installation
```bash
cd /path/to/face-spoofing
pip install -r requirements.txt  # Create if not exists
```

**Key Dependencies:**
```
flask flask-sqlalchemy flask-login
tensorflow==1.15.x  # Or tf.compat.v1 in TF2
opencv-python
mediapipe
onnxruntime-gpu  # or onnxruntime
scikit-learn
arcface  # pip install arcface
pyshine
python-dotenv
```

### Retrain FaceNet Classifier (when adding new users)
```bash
python train.py
```
- Reads images from FacePay/static/Data/FaceNet/{user_id}/
- Outputs FacePay/Models/temp/FaceNet_Model.pkl → copies to FacePay/Models/FaceNet_Model.pkl

### Run Application
```bash
python app.py
```
- Open browser: http://localhost:5000
- Sign up/Sign in → Account → "Add Face" → Checkout

---

## Database Schema (SQLite)

| Table | Description |
|-------|-------------|
| Users | id, name, birthday, gender, id_card, address, phone, email, password_hash, currency (default 1B) |
| PurchaseHistory | id, data (JSON cart), price, date, user_id |
| SignInHistory | id, ip_address, date, user_id |
| FaceData | id, data, date_update, user_id |
| Avatar | id, img, name, mimetype, date_update, user_id |

---

## Key Configuration (`FacePay/func.py`)

```python
# Thresholds
threshold = 0.5           # Anti-spoofing threshold
probabilitiesFaceNet = 0.6  # FaceNet SVM confidence
probabilitiesArcFace = 0.8  # ArcFace distance threshold
ArcFaceActivate = False     # Enable/disable ArcFace verification
```

---

## Important Notes

- This is a 2020 student project — code uses older patterns (TensorFlow 1.x style, legacy Flask patterns)
- Model weights (.pb, .onnx, .pkl) are committed in the repo
- Originally developed on Windows (uses cv2.CAP_DSHOW), may need adjustments for Linux/macOS
- Demo/research purpose only — not production-ready

---

## License

Student project — Educational purpose only.