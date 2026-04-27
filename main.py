import cv2
import numpy as np
from motor_control import move_forward, turn_left, turn_right, stop_car


def thresholding(img):
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    lower_white = np.array([0, 0, 180])
    upper_white = np.array([180, 80, 255])

    mask = cv2.inRange(img_hsv, lower_white, upper_white)
    return mask


def warp_image(img):
    height, width = img.shape[:2]

    pts1 = np.float32([
        [100, height],
        [width - 100, height],
        [width - 220, int(height * 0.55)],
        [220, int(height * 0.55)]
    ])

    pts2 = np.float32([
        [0, height],
        [width, height],
        [width, 0],
        [0, 0]
    ])

    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    img_warp = cv2.warpPerspective(img, matrix, (width, height))

    return img_warp


def get_lane_center(img):
    histogram = np.sum(img[img.shape[0] // 2:, :], axis=0)

    midpoint = int(histogram.shape[0] / 2)

    left_base = np.argmax(histogram[:midpoint])
    right_base = np.argmax(histogram[midpoint:]) + midpoint

    lane_center = int((left_base + right_base) / 2)

    return lane_center


def steering_control(error):
    threshold = 40

    if error > threshold:
        print("Turn Right")
        turn_right()

    elif error < -threshold:
        print("Turn Left")
        turn_left()

    else:
        print("Move Forward")
        move_forward()


def main():
    cap = cv2.VideoCapture(0)

    while True:
        success, img = cap.read()

        if not success:
            print("Camera not detected")
            stop_car()
            break

        img = cv2.resize(img, (640, 480))

        img_threshold = thresholding(img)
        img_warp = warp_image(img_threshold)

        lane_center = get_lane_center(img_warp)
        frame_center = img.shape[1] // 2

        error = lane_center - frame_center

        steering_control(error)

        cv2.line(img, (frame_center, 0), (frame_center, 480), (255, 0, 0), 2)
        cv2.line(img, (lane_center, 0), (lane_center, 480), (0, 255, 0), 2)

        cv2.imshow("Original Image", img)
        cv2.imshow("Lane Detection", img_warp)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            stop_car()
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
