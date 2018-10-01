from videoClipWriter import VideoClipWriter
from audioClipWriter import AudioClipWriter
from subprocess import Popen
import cv2
import numpy as np
import pytesseract
from PIL import Image
from imutils.video import VideoStream
import argparse
import os
import re
import datetime
import pickle

stream = 'cnbc.mp4'
keywords = ['yelp', 'e.l.f.']
vcw = None
acw = None
consecFramesWithoutEvent = 0
frameRate = 30 #default

def getImageWithText(img):
    focus_x = 245
    focus_y = 520
    focus_w = 670
    focus_h = 96

    img = img[focus_y:focus_y+focus_h, focus_x:focus_x+focus_w]
    return img

def binariseImage(original_img):
    try:
        grayscale = cv2.cvtColor(original_img, cv2.COLOR_BGR2GRAY)
        ret, modified_img = cv2.threshold(grayscale, 125, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    except cv2.error as e:
        return original_img
    return modified_img

def getFrameRate(vidcap):
    return int(round(vidcap.get(5)))

def preprocessExtractedText(text):
    lowerCase = text.lower()
    tokens = re.split('[ \n,\']', lowerCase)
    print(tokens)
    return tokens

def isFrameInteresting(tokens):
    global keywords
    keywordsInFrame = []
    for keyword in keywords:
        if keyword in tokens:
            keywordsInFrame.append(keyword)
    
    if not keywordsInFrame:
        return False, []
    return True, keywordsInFrame

def writeMetadata(count):
    global vcw, frameRate
    metadataFile = 'clips/clip.metadata'

    clip = dict()
    clip['keyword'] = vcw.keywords
    clip['filename'] = str(vcw.startFrame) + 'clip.avi'
    clip['start'] = int(vcw.startFrame/frameRate)
    clip['end'] = int(count/frameRate)

    try:
        with open(metadataFile, 'rb') as fp:
            metadata = pickle.load(fp)
    except:
        metadata = []
    
    metadata.append(clip)
    with open(metadataFile, 'wb') as fp:
        pickle.dump(metadata, fp)

def main():
    global stream, vcw, acw, consecFramesWithoutEvent, frameRate
    vidcap = cv2.VideoCapture(stream)
    success, originalImg = vidcap.read()
    count = 0

    ap = argparse.ArgumentParser()
    ap.add_argument("-c", "--codec", type=str, default="MJPG", help="codec of output")
    args = vars(ap.parse_args())

    frameRate = getFrameRate(vidcap)
    vcw = VideoClipWriter(bufSize=32)
    acw = AudioClipWriter(stream, frameRate)

    while success:
        if (count % frameRate != 0):
            success, originalImg = vidcap.read()
            if vcw.isRecording:
                vcw.update(originalImg)
            count += 1
            continue
        
        img = getImageWithText(originalImg)
        img = binariseImage(img)

        tempFile = "frame" + str(count) + ".jpg"
        cv2.imwrite(tempFile, img)
        text = pytesseract.image_to_string(Image.open(tempFile))
        os.remove(tempFile)

        print(count)
        print(text)

        tokens = preprocessExtractedText(text)
        interesting, keywordsFound = isFrameInteresting(tokens)
        if interesting:
            consecFramesWithoutEvent = 0
            if not vcw.isRecording:
                timestamp = datetime.datetime.now()
                clipName = str(count) + ".avi"
                vcw.start(keywordsFound, clipName, count, "clips/" + clipName, cv2.VideoWriter_fourcc(*args["codec"]), frameRate)
            elif not list(set(keywordsFound) & set(vcw.keywords)):
                vcw.finish()
                acw.start(vcw.clipName, vcw.startFrame, count)
                writeMetadata(count)
                
                clipName = str(count) + ".avi"
                vcw.start(keywordsFound, clipName, count, "clips/" + clipName, cv2.VideoWriter_fourcc(*args["codec"]), frameRate)
            else:
                vcw.keywords = list(set(keywordsFound) | set(vcw.keywords))
        else:
            consecFramesWithoutEvent += 1

        if vcw.isRecording and consecFramesWithoutEvent == 1:
            vcw.finish()
            acw.start(vcw.clipName, vcw.startFrame, count)
            writeMetadata(count)
            
        vcw.update(originalImg)

        success, originalImg = vidcap.read()
        print('Read a new frame: ', success)
        count += 1

    if vcw.isRecording:
        vcw.finish()
        acw.start(vcw.clipName, vcw.startFrame, count)
        writeMetadata(count)

    acw.finish()
    vidcap.release()

if __name__ == "__main__":
    main()
