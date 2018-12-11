# Watch live news for market changes which could affect your investments

If you've ever set foot on a trading floor, you'd know there's almost always several TVs tuned to CNBC, Fox Business, Bloomberg News - essentially business news. The trading floor is anything but a quiet place making it all but impossible for traders to hear any of the content coming from those channels barring catastrophic breaking news. Breaking news also tends to be about large, visible companies; smaller company news may have larger impacts on individual fund managers or equity researchers than these large news stories but may go undetected as they are shorter news segments or buried in broader stories.

In this code pattern, we will create a web application which takes an investment portfolio of a user as input, and monitors multiple live news streams in real time to identify if tickers in the portfolio are talked about in the media. If such an event is discovered in the news, the application will begin recording the content of the stream till the news anchors move on to another subject. These clips are then sent back to the user so they can watch these clips in their own time, and prepare for potential market changes that would affect their portfolio.

This code pattern is for developers looking to integrate with the investment portfolio services and use it to monitor live video feed. When the reader has completed this code pattern, they will understand how to:

* Create a Flask web application which is integrated with the investment portfolio service.
* Monitor live video feed in real time using python.
* Use OpenCV and Tesseract-OCR to perform character recognition of frames of a video feed.
* Use Web Sockets for real time streaming of data between the server and client application.

# Architecture Flow

![Architecture Flow](docs/doc-images/arch-flow.png?raw=true)

1. The user sends their investment portfolio to the investment portfolio service.
1. The user selects multiple News feeds for the application to monitor.
1. The name of the portfolio and news feeds are sent to the server.
1. The server pulls the portfolio of the user from the investment portfolio service.
1. The server then spawns a process for each feed to monitor them in parallel.
1. Each process spawns two threads:
	1. One to start and stop recording the clip once the process identifies an interesting clip for the user based on the portfolio.
	1. The other to send the clip extracted through an error detect sequence to fix any encoding issues with the clip.
1. The processes continuously send the clips to be stored in a repository.
1. The user gets the clips on the client side through a socket connection to the server.

# Included Components

+ [Investment Portfolio](https://console.ng.bluemix.net/catalog/services/investment-portfolio) The Investment Portfolio service lets you store, update, and query your investment portfolios and associated holdings using flexible object definitions
> The Investment Portfolio service is available for free on [IBM Cloud](https://console.bluemix.net)

## Featured Technologies

* [Python](https://www.python.org/downloads/): Python is a programming language that lets you work more quickly and integrate your systems more effectively
* [JQuery](https://jquery.com): jQuery is a cross-platform JavaScript library designed to simplify the client-side scripting of HTML
* [Flask](http://flask.pocoo.org/) Flask is a micro web framework written in Python
* [Tesseract-OCR](https://github.com/tesseract-ocr/tesseract) Tesseract is an OCR engine.
* [OpenCV](https://opencv.org/) OpenCV is a library of programming functions mainly aimed at real-time computer vision
* [Streamlink](https://streamlink.github.io/) Command-line utility that extracts streams from various services and pipes them into a video player of choice
* [Docker](https://www.docker.com/) Docker is a computer program that performs operating-system-level virtualization, also known as Containerization
* [Curl](https://curl.haxx.se/) Curl is a command line tool and library for transferring data with URLs

# Running the Application

## Manually deploy to local machine
1. [Setup your machine](#1-setup-your-machine)
2. [Clone the repository](#2-clone-the-repository)
3. [Create Investment Portfolio service](#3-create-investment-portfolio-service)
4. [Configure .env file](#4-configure-env-file)
5. [Run application in Docker container](#5-run-with-docker)
6. [Upload Holdings](#6-uploading-holdings)
7. [Watch News](#7-watch-news)

### 1. Setup your machine
- [Python](https://www.python.org/downloads/), Download and Install Python 3.6 or above.
- [Docker](https://www.docker.com/), Go to the docker website and download the installer. After installation, run Docker.

### 2. Clone the repository

```
git clone https://github.com/ash7594/Portfolio-NewsAnchor.git
```

## 3. Create Investment Portfolio service

Create the following services in IBM Cloud. This services is part of `Free` plan.

* [**Investment Portfolio**](https://console.ng.bluemix.net/catalog/services/investment-portfolio)


## 4. Configure .env file

Create a `.env` file in the root directory of your clone of the project repository by copying the sample `.env.example` file using the following command in terminal:

  ```none
  cp .env.example .env
  ```

> Most files systems regard files with a "." at the front as hidden files.  If you are on a Windows system, you should be able to use either [GitBash](https://git-for-windows.github.io/) or [Xcopy](https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/xcopy)

You will need to update the credentials with the IBM Cloud credentials for the services you created in [Step 2](#2-create-investment-portfolio-service).

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

You can view the docker logs of your store,
```
$ docker logs portfolio-newsanchor
```

Access the running app in a browser at <http://0.0.0.0:8080/>

### 6. Upload Holdings

Once the application is running, the first step is to upload a file that will be used to create a portfolio or a series of portfolios in the Investment Portfolio service. We use the file format of the Algorithmics Risk Service (ARS) import file as many production clients are already used to that format.

You can use the `SamplePortfolio.csv` file in this repository.

- The column labeled "UNIQUE ID" must refer to the unique identifier of the asset in our system.
- The "NAME" column will hold the display name of the asset.
- "POSITION UNITS" column holds the quantity.
- "PORTFOLIO" indicates which portfolio the asset belongs to.

The code will create a portfolio for each unique element found in the "PORTFOLIO" column. Future releases of this code will take into account a portfolio hierarchy, but currently each portfolio is entirely independent of each other.

Some notes:
- The portfolio will be loaded as 100-asset chunks as there are currently limitations on POST request sizing.
- The portfolio will be tagged as type = 'look through portfolio' to distinguish between any other portfolios that may exist in the system.

### 7. Watch News

After successfully uploading the portfolio, select the news channels that you want the application to watch LIVE.

![](docs/doc-images/app.png)

# License

This code pattern is licensed under the Apache Software License, Version 2.  Separate third party code objects invoked within this code pattern are licensed by their respective providers pursuant to their own separate licenses. Contributions are subject to the [Developer Certificate of Origin, Version 1.1 (DCO)](https://developercertificate.org/) and the [Apache Software License, Version 2](http://www.apache.org/licenses/LICENSE-2.0.txt).

[Apache Software License (ASL) FAQ](http://www.apache.org/foundation/license-faq.html#WhatDoesItMEAN)
