import subprocess
import numpy as np
from threading import Thread
import os

class AudioClipWriter:
    def __init__(self, stream, fps):
        self.stream = stream
        self.fps = fps
        self.threads = []
        #self.audioFromStream = AudioSegment.from_file(stream, "mp4")

    def start(self, clip, sFrame, eFrame):
        self.threads.append(Thread(target=self.write, args=(clip,sFrame,eFrame,)))
        self.threads[len(self.threads)-1].daemon = True
        self.threads[len(self.threads)-1].start()

    def write(self, clip, sFrame, eFrame):
        sTime = int(sFrame/self.fps)
        eTime = int(eFrame/self.fps)
        duration = eTime - sTime
        
        audioFile = "clips/" + str(sFrame) + ".wav"
        videoFile = "clips/" + str(clip)
        finalClipFile = "clips/" + str(sFrame) + "clip.avi"

        #Extract Audio of interest
        #audio = self.audioFromStream[sTime*1000: eTime*1000]
        #audio.export(audioFile, format="wav")

        #Mux video and Audio
        #command = "ffmpeg -i " + videoFile + " -i " + audioFile + " -c:v copy -c:a copy " + finalClipFile
        #subprocess.call(command, shell=True)
        
        #self.clean(audioFile, videoFile)

    def clean(self, audioFile, videoFile):
        os.remove(audioFile)
        os.remove(videoFile)

    def finish(self):
        for thread in self.threads:
            thread.join()

