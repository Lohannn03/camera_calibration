import cv2 as cv
import numpy as np


def load_calibration(npz_file='calibration_result.npz'):
    data = np.load(npz_file)
    K = data['K']
    dist_coeff = data['dist_coeff']
    return K, dist_coeff


def rectify_video(video_file, K, dist_coeff, output_file='rectified_demo.mp4'):
    video = cv.VideoCapture(video_file)
    assert video.isOpened(), f'Cannot open video: {video_file}'

    fps = video.get(cv.CAP_PROP_FPS)
    if fps <= 0:
        fps = 30

    writer = None
    map1, map2 = None, None

    while True:
        valid, img = video.read()
        if not valid:
            break

        h, w = img.shape[:2]

        if writer is None:
            fourcc = cv.VideoWriter_fourcc(*'mp4v')
            writer = cv.VideoWriter(output_file, fourcc, fps, (w * 2, h))

        if map1 is None or map2 is None:
            map1, map2 = cv.initUndistortRectifyMap(
                K, dist_coeff, None, K, (w, h), cv.CV_32FC1
            )

        rectified = cv.remap(img, map1, map2, interpolation=cv.INTER_LINEAR)

        left = img.copy()
        right = rectified.copy()
        
        font = cv.FONT_HERSHEY_DUPLEX
        scale = 0.7
        thickness = 2

        text1 = 'Original'
        (text_w1, _), _ = cv.getTextSize(text1, font, scale, thickness)
        cv.putText(left, text1, (w - text_w1 - 10, 25), font, scale, (0,255,0), thickness)

        text2 = 'Rectified'
        (text_w2, _), _ = cv.getTextSize(text2, font, scale, thickness)
        cv.putText(right, text2, (w - text_w2 - 10, 25), font, scale, (0,255,0), thickness)
       
        merge = np.hstack((left, right))

        cv.imshow('Distortion Correction: Original | Rectified', merge)
        writer.write(merge)

        key = cv.waitKey(1) & 0xFF
        if key == 27:
            break

    video.release()
    if writer is not None:
        writer.release()
    cv.destroyAllWindows()


def rectify_image(image_file, K, dist_coeff, output_file='rectified_image.png'):
    img = cv.imread(image_file)
    assert img is not None, f'Cannot open image: {image_file}'

    rectified = cv.undistort(img, K, dist_coeff)

    merge = np.hstack((img, rectified))
    cv.putText(merge, 'Original', (10, 25), cv.FONT_HERSHEY_DUPLEX, 0.7, (0, 255, 0), 2)
    cv.putText(merge, 'Rectified', (img.shape[1] + 10, 25), cv.FONT_HERSHEY_DUPLEX, 0.7, (0, 255, 0), 2)

    cv.imwrite(output_file, merge)
    cv.imshow('Distortion Correction: Original | Rectified', merge)
    cv.waitKey(0)
    cv.destroyAllWindows()


if __name__ == '__main__':
    K, dist_coeff = load_calibration('calibration_result.npz')

    # Video demonstration
    rectify_video('chessboard.avi', K, dist_coeff, output_file='rectified_demo.mp4')

    # If you have a separate wide-angle image, uncomment the line below
    # rectify_image('sample_wide.jpg', K, dist_coeff, output_file='rectified_image.png')