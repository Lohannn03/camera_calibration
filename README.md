# Wide Angle Camera Calibration and Distortion Correction

## Description

This project performs camera calibration and lens distortion correction using OpenCV.
A printed chessboard pattern is used to estimate intrinsic camera parameters and remove lens distortion.

---

## Chessboard Pattern

* Paper size: A4
* Square size: **25 mm (0.025 m)**
* Pattern: **10 x 7 inner corners (vertices)**
* Total squares: 11 x 8

---

## Environment

* Python 3.x
* OpenCV
* NumPy

---

## Files

* `camera_calibration.py` → performs camera calibration
* `distortion_correction.py` → removes lens distortion
* `calibration_result.npz` → saved calibration data
* `rectified_demo.mp4` → distortion correction video
* `rectified_image.png` → distortion correction image

---

## How to Run

### 1. Camera Calibration

```bash
python camera_calibration.py
```

Steps:

* Press **SPACE** to pause
* Press **ENTER** to save a good frame
* Press **A** to auto-save detected frames
* Press **ESC** to finish

---

### 2. Distortion Correction

```bash
python distortion_correction.py
```

---

## Camera Calibration Results
<img width="889" height="419" alt="camera_calibration_output" src="https://github.com/user-attachments/assets/7b19aa0e-f789-4868-ab1f-93bcef51f4cf" />

* Number of applied images: **21**
* RMS error (OpenCV): **1.201046**
* Reprojection RMSE: **1.201046**

---

### Camera Matrix (K)

```text
[[787.66175757   0.         284.82732367]
 [  0.         790.67986199 169.21612259]
 [  0.           0.           1.        ]]
```

---

### Distortion Coefficients

```text
[ 0.0920086   0.17366872 -0.02972521 -0.02060461 -0.19510412]
```

---

## Demo

### 1. Chessboard Detection

<img width="824" height="654" alt="detected_chessboard" src="https://github.com/user-attachments/assets/5b171a1b-2d89-478a-b8a0-2118b81009b2" />

---

### 2. Distortion Correction

#### Before vs After

<img width="1647" height="765" alt="rectified_demo" src="https://github.com/user-attachments/assets/6d302088-6501-4e9d-b96a-98185a58bddd" />


#### Video Demo

<video src="D:\3학년 2학기\컴퓨터비전\hw3_camera_calibration\rectified_demo.mp4" controls="controls" muted="muted" style="max-width: 100%;"></video>


---

## Key Concepts

* Camera matrix (K): intrinsic parameters (fx, fy, cx, cy)
* Distortion coefficients: lens distortion model (radial and tangential)
* Calibration: mapping 3D world coordinates to 2D image plane
* Undistortion: removing lens distortion

---

## Limitations

* Calibration accuracy depends on chessboard flatness
* Motion blur can increase error
* Limited viewpoints reduce calibration quality
* More images with diverse angles can further improve accuracy

---

## Conclusion

Camera calibration successfully estimated intrinsic parameters and corrected lens distortion.
The results demonstrate clear improvement between original and rectified images.
