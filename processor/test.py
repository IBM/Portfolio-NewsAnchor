import cv2
import streamlink

#streams = streamlink.streams('www.youtube.com/watch?v=XOacA3RYrXk')
streams = streamlink.streams('www.bloomberg.com/live/us')
url = streams['best']
print(url)
#cap = cv2.VideoCapture(url)
fd = url.open()
bytes_ = fd.read(1024)

index = 1
while index < 5000:
    #succ, frame = cap.read()
    bytes_ += fd.read(1024)
    print("hello")
    index += 1

#verify optimization of this part by writing to file as soon as bytes are received.
with open('hello.mp4','wb') as w:
    w.write(bytes_)
fd.close()
