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
import sys
import streamlink
from random import randint

feed_stream = None
stream = None
keywords = ['yelp', 'e.l.f.']
vcw = None
acw = None
consecFramesWithoutEvent = 0
frameRate = 30 #default

bloomUsNews = 'https://www.bloomberg.com/live/us'
bloomGlobNews = 'https://www.youtube.com/watch?v=Ga3maNZ0x0w'
skyNews = 'https://www.youtube.com/watch?v=XOacA3RYrXk'
cnbcAfricaNews = 'https://www.youtube.com/watch?v=IpmKglKxQpA'

def getImageWithText(img):
    global bloomUsNews, bloomGlobNews, skyNews, cnbcAfricaNews

    if feed_stream == skyNews:
        # sky-news textarea
        focus_x = 0 #0
        focus_y = 0.9213 #995
        focus_w = 1 #1920
        focus_h = 0.0787 #85
    
    elif feed_stream == bloomUsNews:
        # bloomberg-us-news textarea
        focus_x = 0 #0
        focus_y = 0.8889 #995
        focus_w = 1 #1920
        focus_h = 0.0653 #85
        
    elif feed_stream == bloomGlobNews:
        # bloomberg-global-news textarea
        focus_x = 0 #0
        focus_y = 0.8889 #640
        focus_w = 1 #1280
        focus_h = 0.0653 #47
        
    elif feed_stream == cnbcAfricaNews:
        # cnbc-africa-news textarea
        focus_x = 0 #0
        focus_y = 0.9213 #995
        focus_w = 1 #1920
        focus_h = 0.0787 #85

    else:
        return img
    
    img_h, img_w, img_ch = img.shape
    print(str(img_h) + " " + str(img_w) + " " + str(img_ch))

    focus_x = int(round(focus_x * img_w))
    focus_y = int(round(focus_y * img_h))
    focus_w = int(round(focus_w * img_w))
    focus_h = int(round(focus_h * img_h))

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
    global feed_stream, stream, vcw, acw, consecFramesWithoutEvent, frameRate
    feed_stream = sys.argv[1]
    print(feed_stream)
    streams = streamlink.streams(feed_stream)
    print(streams)
    stream = streams['best'].url

    vidcap = cv2.VideoCapture(stream)
    success, originalImg = vidcap.read()
    count = 0

#    ap = argparse.ArgumentParser()
#    ap.add_argument("-c", "--codec", type=str, default="MJPG", help="codec of output")
#    args = vars(ap.parse_args())

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
        
        tempFile = "frame" + str(count) + str(randint(10000,99999)) + "_1.jpg"
        cv2.imwrite(tempFile, originalImg)
        
        img = getImageWithText(originalImg)
        tempFile = "frame" + str(count) + str(randint(10000,99999)) + "_2.jpg"
        cv2.imwrite(tempFile, img)
        
        img = binariseImage(img)
        tempFile = "frame" + str(count) + str(randint(10000,99999)) + "_3.jpg"
        cv2.imwrite(tempFile, img)

        text = pytesseract.image_to_string(Image.open(tempFile))
        #os.remove(tempFile)

        print(count)
        print("parentPing:" + text)
        sys.stdout.flush()

        tokens = preprocessExtractedText(text)
        interesting, keywordsFound = isFrameInteresting(tokens)
        if interesting:
            consecFramesWithoutEvent = 0
            if not vcw.isRecording:
                timestamp = datetime.datetime.now()
                clipName = str(count) + ".avi"
                vcw.start(keywordsFound, clipName, count, "clips/" + clipName, cv2.VideoWriter_fourcc('M','J','P','G'), frameRate)
            elif not list(set(keywordsFound) & set(vcw.keywords)):
                vcw.finish()
                acw.start(vcw.clipName, vcw.startFrame, count)
                writeMetadata(count)
                
                clipName = str(count) + ".avi"
                vcw.start(keywordsFound, clipName, count, "clips/" + clipName, cv2.VideoWriter_fourcc('M','J','P','G'), frameRate)
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
