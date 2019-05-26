# WARNING: This repository is no longer maintained :warning:

> This repository will not be updated. The repository will be kept available in read-only mode.

# Watch live news for market changes that could affect your investments

If you've ever set foot on a trading floor, you know that there are almost always several TVs tuned to business news stations. The trading floor is anything but a quiet place, making it all but impossible for traders to hear any of the content coming from those channels other than catastrophic breaking news. Breaking news also tends to be about larger, more visible companies; news about smaller companies may have a greater impact on individual fund managers or equity researchers than these big news stories, but may go undetected as these news segments tend to be shorter and can get buried beneath the larger stories.

This code pattern shows you how to create a web application that takes the user's investment portfolio as input and monitors multiple live news streams in real time to identify what tickers in the portfolio are covered in the media. If the app comes across a relevant event in the news, it records the content of the stream until the news source moves on to another subject. It then sends these clips back to the user so they can watch these clips at their convenience, and prepare for potential market changes that could affect their portfolio.

This code pattern is for developers who want to integrate with the Investment Portfolio services and use them to monitor live video feeds. When you have completed it, you will understand how to:

* Create a Flask web app that is integrated with the Investment Portfolio service.
* Monitor live video feeds in real time using Python.
* Use OpenCV and Tesseract-OCR to perform character recognition on the frames in a video feed.
* Use Web Sockets for real-time streaming of data between the server and the client application.

# Architecture flow

![Architecture flow](docs/doc-images/arch-flow.png?raw=true)

1. User sends the investment portfolio to the Investment Portfolio service.
2. User selects multiple news feeds for the application to monitor.
3. Application sends the portfolio name and selected news feeds to the server.
4. Server pulls the user's portfolio from the investment portfolio service.
5. Server then spawns a process for each feed to monitor them in parallel.
6. Each process spawns two threads:
   * One that starts and stops recording the clip once the process identifies an appropriate clip for the user based on the portfolio
   * The other sends the clip extracted through an error detect sequence to fix any encoding issues with the clip
7. Processes continuously send the clips to be stored in a repository.
8. User gets the clips on the client side through a socket connection to the server.

# Included components

+ [Investment Portfolio](https://console.ng.bluemix.net/catalog/services/investment-portfolio) The Investment Portfolio service lets you store, update, and query your investment portfolios and associated holdings using flexible object definitions.
> The Investment Portfolio service is available for free on [IBM Cloud](https://console.bluemix.net).

## Featured technologies

* [Python](https://www.python.org/downloads/) is a programming language that lets you work more quickly and integrate your systems more effectively.
* [JQuery](https://jquery.com) is a cross-platform JavaScript library designed to simplify the client-side scripting of HTML.
* [Flask](http://flask.pocoo.org/) is a micro web framework written in Python.
* [Tesseract-OCR](https://github.com/tesseract-ocr/tesseract) is an OCR engine.
* [OpenCV](https://opencv.org/) is a library of programming functions mainly aimed at real-time computer vision.
* [Streamlink](https://streamlink.github.io/) is a command-line utility that extracts streams from various services and pipes them into a video player of choice.
* [Socket.IO](https://socket.io/) enables real-time, bidirectional, and event-based communication.
* [Docker](https://www.docker.com/) is a computer program that performs operating-system-level virtualization, also known as Containerization.
* [Curl](https://curl.haxx.se/) is a command-line tool and library for transferring data with URLs.

# Running the application

## Manually deploy to local machine
1. [Set up your machine](#1-set-up-your-machine)
2. [Clone the repository](#2-clone-the-repository)
3. [Create the Investment Portfolio service](#3-create-the-investment-portfolio-service)
4. [Configure the .env file](#4-configure-the-.env-file)
5. [Run the application in a Docker container](#5-run-with-docker)
6. [Upload the holdings](#6-upload-the-holdings)
7. [Watch the news](#7-watch-the-news)

### 1. Set up your machine
- [Python](https://www.python.org/downloads/): Download and install Python 3.6 or above.
- [Docker](https://www.docker.com/): Go to the Docker website and download the installer. After installation, run Docker.

### 2. Clone the repository

```
git clone https://github.com/IBM/Portfolio-NewsAnchor.git
```

## 3. Create the Investment Portfolio service

Create the following services in IBM Cloud. These services are part of the `Free` plan.

* [**Investment Portfolio**](https://console.ng.bluemix.net/catalog/services/investment-portfolio)


## 4. Configure the .env file

Create the `.env` file in the root directory of your clone of the project repository by copying the sample `.env.example` file using the following command in the terminal:

  ```none
  cp .env.example .env
  ```

> Most file systems regard files with a "." at the front as hidden files.  If you are on a Windows system, you should be able to use either [GitBash](https://git-for-windows.github.io/) or [Xcopy](https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/xcopy).

You will need to update the credentials with the IBM Cloud credentials for the services that you created in [Step 3](#3-create-the-investment-portfolio-service).

The `.env` file will look something like the following:

```none
# Investment Portfolio
CRED_PORTFOLIO_USERID_W=
CRED_PORTFOLIO_PWD_W=
CRED_PORTFOLIO_USERID_R=
CRED_PORTFOLIO_PWD_R=

```

### 5. Run with Docker

```
$ bash docker-run.sh
```

You can view the Docker logs of your store:
```
$ docker logs portfolio-newsanchor
```

Access the running app in a browser at <http://0.0.0.0:8080/>.

### 6. Upload the holdings

Once the application is running, the first step is to upload a file that will be used to create a portfolio or a series of portfolios in the Investment Portfolio service. We use the file format of the Algorithmics Risk Service (ARS) import file as many production clients are already used to that format.

You can use the `SamplePortfolio.csv` file in this repository.

- The column labeled "UNIQUE ID" must refer to the unique identifier of the asset in your system.
- The "NAME" column will hold the display name of the asset.
- The "POSITION UNITS" column holds the quantity.
- "PORTFOLIO" indicates which portfolio the asset belongs to.

The code will create a portfolio for each unique element found in the "PORTFOLIO" column. Future releases of this code will take into account a portfolio hierarchy, but currently all of the portfolios are entirely independent of each other.

Some notes:
- The portfolio will be loaded as 100-asset chunks as there are currently limitations on POST request sizing.
- The portfolio will be tagged as type = 'look through portfolio' to distinguish between any other portfolios that may exist in the system.

### 7. Watch the news

After successfully uploading the portfolio, select the news channels that you want the application to watch LIVE.

![](docs/doc-images/app.png)

# License

This code pattern is licensed under the Apache Software License, Version 2.  Separate third-party code objects invoked within this code pattern are licensed by their respective providers pursuant to their own separate licenses. Contributions are subject to the [Developer Certificate of Origin, Version 1.1 (DCO)](https://developercertificate.org/) and the [Apache Software License, Version 2](http://www.apache.org/licenses/LICENSE-2.0.txt).

[Apache Software License (ASL) FAQ](http://www.apache.org/foundation/license-faq.html#WhatDoesItMEAN)
