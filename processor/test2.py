import cv2
import streamlink

streams = streamlink.streams('https://www.youtube.com/watch?v=RD83Cs9entE')
url = streams['best'].url
print(url)
cap = cv2.VideoCapture(url)

print(int(round(cap.get(5))))
index = 1
while index < 11:
    succ, frame = cap.read()
    if succ:
        cv2.imwrite(str(index) + ".png", frame)
        print("hello")
    else:
        break
    index += 1

cap.release()
