import cv2 as cv
import numpy as np


def select_img_from_video(video_file, board_pattern, select_all=False, wait_msec=30):
    """
    Select frames from a video for calibration.

    Key:
    - SPACE : pause / resume
    - ENTER : save current frame (if a chessboard is detected)
    - A     : toggle auto-save for all detected frames
    - ESC   : finish
    """
    video = cv.VideoCapture(video_file)
    assert video.isOpened(), f'Cannot open video: {video_file}'

    img_select = []
    paused = False
    auto_save = select_all
    frame_idx = 0
    img = None

    while True:
        if not paused:
            valid, current = video.read()
            if not valid:
                break
            img = current
            frame_idx += 1

        if img is None:
            break

        view = img.copy()
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

        complete, pts = cv.findChessboardCorners(gray, board_pattern)

        if complete:
            # refine corners for better accuracy
            criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
            pts = cv.cornerSubPix(gray, pts, (11, 11), (-1, -1), criteria)
            cv.drawChessboardCorners(view, board_pattern, pts, complete)

        info1 = f'Frame: {frame_idx} | Saved: {len(img_select)}'
        info2 = f'Chessboard: {"DETECTED" if complete else "NOT DETECTED"} | AutoSave(A): {"ON" if auto_save else "OFF"}'
        info3 = 'SPACE: pause/resume | ENTER: save current frame | ESC: finish'

        cv.putText(view, info1, (10, 25), cv.FONT_HERSHEY_DUPLEX, 0.6, (0, 255, 0), 2)
        cv.putText(view, info2, (10, 50), cv.FONT_HERSHEY_DUPLEX, 0.55,
                   (0, 255, 0) if complete else (0, 0, 255), 1)
        cv.putText(view, info3, (10, 75), cv.FONT_HERSHEY_DUPLEX, 0.5, (0, 255, 255), 1)

        cv.imshow('Select Calibration Images', view)

        if auto_save and complete and not paused:
            img_select.append(img.copy())

        key = cv.waitKey(wait_msec) & 0xFF

        if key == 27:  # ESC
            break
        elif key == ord(' '):
            paused = not paused
        elif key == 13:  # ENTER
            if complete:
                img_select.append(img.copy())
        elif key in (ord('a'), ord('A')):
            auto_save = not auto_save

    video.release()
    cv.destroyAllWindows()
    return img_select


def calib_camera_from_chessboard(images, board_pattern, board_cellsize,
                                 K=None, dist_coeff=None, calib_flags=None):
    """
    board_pattern = (number of inner corners horizontally, number of inner corners vertically)
    board_cellsize = size of a single square (in meters)
    """
    img_points = []
    gray = None

    criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    for img in images:
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        complete, pts = cv.findChessboardCorners(gray, board_pattern)

        if complete:
            pts = cv.cornerSubPix(gray, pts, (11, 11), (-1, -1), criteria)
            img_points.append(pts)

    assert len(img_points) > 0, 'There is no set of complete chessboard points!'

    # Create 3D points of the chessboard on the z = 0 plane
    obj_pts = [[c, r, 0] for r in range(board_pattern[1]) for c in range(board_pattern[0])]
    obj_template = np.array(obj_pts, dtype=np.float32) * board_cellsize
    obj_points = [obj_template.copy() for _ in range(len(img_points))]

    return cv.calibrateCamera(
        obj_points,
        img_points,
        gray.shape[::-1],
        K,
        dist_coeff,
        flags=0 if calib_flags is None else calib_flags
    )


def compute_reprojection_rmse(obj_points, img_points, rvecs, tvecs, K, dist_coeff):
    total_error_sq = 0.0
    total_points = 0

    for objp, imgp, rvec, tvec in zip(obj_points, img_points, rvecs, tvecs):
        proj_pts, _ = cv.projectPoints(objp, rvec, tvec, K, dist_coeff)
        err = cv.norm(imgp, proj_pts, cv.NORM_L2)
        total_error_sq += err ** 2
        total_points += len(objp)

    if total_points == 0:
        return 0.0
    return np.sqrt(total_error_sq / total_points)


if __name__ == '__main__':
    video_file = 'chessboard.avi'
    board_pattern = (10, 7)   # 10x7 vertices = inner corners
    board_cellsize = 0.025    # 25 mm = 0.025 m

    # Select frames from the video
    images = select_img_from_video(video_file, board_pattern, select_all=False, wait_msec=30)

    assert len(images) > 0, 'No images were selected from the video.'

    # Rebuild obj_points & img_points to calculate reprojection RMSE
    img_points = []
    gray = None
    criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    for img in images:
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        complete, pts = cv.findChessboardCorners(gray, board_pattern)
        if complete:
            pts = cv.cornerSubPix(gray, pts, (11, 11), (-1, -1), criteria)
            img_points.append(pts)

    obj_pts = [[c, r, 0] for r in range(board_pattern[1]) for c in range(board_pattern[0])]
    obj_template = np.array(obj_pts, dtype=np.float32) * board_cellsize
    obj_points = [obj_template.copy() for _ in range(len(img_points))]

    # Camera calibration
    rmse, K, dist_coeff, rvecs, tvecs = cv.calibrateCamera(
        obj_points,
        img_points,
        gray.shape[::-1],
        None,
        None
    )

    reproj_rmse = compute_reprojection_rmse(obj_points, img_points, rvecs, tvecs, K, dist_coeff)

    # Save the result for subsequent use in distortion_correction.py
    np.savez(
        'calibration_result.npz',
        K=K,
        dist_coeff=dist_coeff,
        rmse=rmse,
        reproj_rmse=reproj_rmse,
        image_width=gray.shape[1],
        image_height=gray.shape[0],
        board_pattern=np.array(board_pattern),
        board_cellsize=board_cellsize,
        used_images=len(img_points)
    )

    print('\n## Camera Calibration Results')
    print(f'* The number of applied images = {len(img_points)}')
    print(f'* RMS error (OpenCV return) = {rmse:.6f}')
    print(f'* Reprojection RMSE = {reproj_rmse:.6f}')
    print('* Camera matrix (K) =')
    print(K)
    print('* Distortion coefficient (k1, k2, p1, p2, k3, ...) =')
    print(dist_coeff.ravel())
    print('* Saved file = calibration_result.npz')