import cv2


IMAGE_PATH = "output/sample_frames/frame_000060.jpg"

points = []


def handle_click(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        points.append((x, y))
        print(f"Point {len(points)}: ({x}, {y})")

        cv2.circle(
            image,
            (x, y),
            6,
            (0, 0, 255),
            -1,
        )

        cv2.imshow("Court Calibration", image)


image = cv2.imread(IMAGE_PATH)

if image is None:
    raise ValueError(f"Could not open image: {IMAGE_PATH}")

cv2.imshow("Court Calibration", image)

cv2.setMouseCallback(
    "Court Calibration",
    handle_click,
)

print("Click 4 court points in order.")
print("Press Q when finished.")

while True:
    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break

cv2.destroyAllWindows()

print("Selected points:")
print(points)