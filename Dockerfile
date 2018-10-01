FROM ubuntu:trusty
COPY . .
RUN apt-get update -y && \
  apt-get upgrade -y && \
  apt-get install -y software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa && \
  apt-get update -y && \
  apt-get install -y python3.6 && \
  apt-get install -y python3-pip
RUN pip3 install flask && \
  pip3 install python-dotenv
RUN apt-get install -y libav-tools libavcodec-extra
RUN pip3 install numpy
RUN pip3 install opencv-python && \
  pip3 install pydub && \
  pip3 install pytesseract && \
  pip3 install imutils && \
  pip3 install Pillow
  
EXPOSE 8080
CMD ["python3", "run.py"]
