import cv2
import numpy as np

img = cv2.imread("../example/pushkin_aksakov/image/crossroads.jpg", cv2.IMREAD_GRAYSCALE)

lsd = cv2.createLineSegmentDetector()

lines, _, _, _ = lsd.detect(img)

drawn_img = lsd.drawSegments(img.copy(), lines)

scale = 0.5  # уменьшить в 2 раза
drawn_img = cv2.resize(drawn_img, (0, 0), fx=scale, fy=scale)

cv2.imshow("Detected Lines", drawn_img)
cv2.waitKey(0)
cv2.destroyAllWindows()