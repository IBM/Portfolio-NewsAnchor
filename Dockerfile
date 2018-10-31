FROM ubuntu:16.04
COPY . .
RUN apt-get update -y && \
  apt-get upgrade -y && \
  apt-get install -y software-properties-common
RUN add-apt-repository ppa:jonathonf/python-3.6 && \
  apt-get update -y && \
  apt-get install -y python3.6
RUN apt-get install -y libsm6 libxrender1 libfontconfig1
RUN apt-get install -y wget
RUN wget https://bootstrap.pypa.io/get-pip.py && \
  python3.6 get-pip.py
RUN ln -s /usr/bin/python3.6 /usr/local/bin/python
RUN pip install flask && \
  pip install python-dotenv
RUN apt-get install -y ffmpeg libavcodec-extra
RUN pip install gevent
RUN pip install flask-socketio
RUN pip install requests
RUN pip install numpy
RUN pip install opencv-python
RUN pip install opencv-contrib-python
RUN pip install pydub
RUN pip install pytesseract
RUN pip install imutils
RUN pip install Pillow
RUN pip install streamlink
RUN apt-get install -y tesseract-ocr
  
EXPOSE 8080
CMD ["python", "run.py"]
