# Copyright 2015 IBM Corp. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import requests
import json
import argparse
from dotenv import load_dotenv
import os
import datetime

#Initalize Investment Portfolio Service credentials to find on Bluemix otherwise from .env file
if 'VCAP_SERVICES' in os.environ:
    vcap_servicesData = json.loads(os.environ['VCAP_SERVICES'])
    # Log the fact that we successfully found some service information.
    print("Got vcap_servicesData\n")
    #print(vcap_servicesData)
    # Look for the IP service instance.
    IP_W_username=vcap_servicesData['fss-portfolio-service'][0]['credentials']['writer']['userid']
    IP_W_password=vcap_servicesData['fss-portfolio-service'][0]['credentials']['writer']['password']
    IP_R_username=vcap_servicesData['fss-portfolio-service'][0]['credentials']['reader']['userid']
    IP_R_password=vcap_servicesData['fss-portfolio-service'][0]['credentials']['reader']['password']
    # Log the fact that we successfully found credentials
    print("Got IP credentials\n")
else:
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
    IP_W_username=os.environ.get("CRED_PORTFOLIO_USERID_W")
    IP_W_password=os.environ.get("CRED_PORTFOLIO_PWD_W")
    IP_R_username=os.environ.get("CRED_PORTFOLIO_USERID_R")
    IP_R_password=os.environ.get("CRED_PORTFOLIO_PWD_R")

def Get_Portfolios():
    """
    Retreives portfolio data by calling the Investment Portfolio service
    """
    print ("Get Portfolios")
    #call the url
    BASEURL = "https://investment-portfolio.mybluemix.net/api/v1/portfolios/"
    headers = {
        'accept': "application/json",
        'content-type': "application/json"
        }
    get_data = requests.get(BASEURL, auth=(IP_R_username, IP_R_password), headers=headers)
    print("Investment Portfolio status: " + str(get_data.status_code))
    # return json data
    data = get_data.json()
    return data

def Get_Portfolio_Holdings(Portfolio,latest=True):
    """
    Retreives holdinga data from the Investment Portfolio service for the Portfolio
    """
    print ("Get Portfolio Holdings for " + Portfolio)
    #construct the url
    BASEURL = "https://investment-portfolio.mybluemix.net/api/v1/portfolios/" + Portfolio + "/holdings"
    if latest:
        BASEURL += "?latest=true"
    #call the url
    headers = {
        'accept': "application/json",
        'content-type': "application/json"
        }
    get_data = requests.get(BASEURL, auth=(IP_R_username, IP_R_password), headers=headers)
    print("Investment Portfolio - Get Portfolio Holdings status: " + str(get_data.status_code))
    #return json data
    data = get_data.json()
    return data

def Get_Portfolios_by_Selector(selector,value):
    """
    Retreives portfolio data by calling the Investment Portfolio service
    """
    print ("Get Portfolios by Selector")
    #call the url
    BASEURL = "https://investment-portfolio.mybluemix.net/api/v1/portfolios/_find"
    headers = {
        'accept': "application/json",
        'content-type': "application/json"
        }
    s = {
        'dataSelector':{
            selector:value
        }
    }

    get_data = requests.post(BASEURL, auth=(IP_R_username, IP_R_password), headers=headers, data=json.dumps(s))
    print("Investment Portfolio status: " + str(get_data.status_code))
    # return json data
    data = get_data.json()
    return data

def Get_Holdings_by_Selector(portfolio,selector,value):
    """
    Retreives portfolio data by calling the Investment Portfolio service
    """
    print ("Get Portfolios by Selector")
    #call the url
    BASEURL = "https://investment-portfolio.mybluemix.net/api/v1/portfolios/" + portfolio + "/holdings/_find"
    headers = {
        'accept': "application/json",
        'content-type': "application/json"
        }
    s = {
        'dataSelector':{
            str(selector):str(value)
        }
    }
    get_data = requests.post(BASEURL, auth=(IP_R_username, IP_R_password), headers=headers, data=json.dumps(s))
    print("Investment Portfolio status: " + str(get_data.status_code))
    # return json data
    data = get_data.json()
    return data

def Create_Portfolio(Portfolio):
    """
    Creates portfolio in the database.
    """
    #construct the url
    BASEURL = "https://investment-portfolio.mybluemix.net/api/v1/portfolios"
    headers = {
        'Content-Type': "application/json",
        'Accept': "application/json"
        }
    get_data = requests.post(BASEURL, auth=(IP_W_username, IP_W_password), headers=headers, data=json.dumps(Portfolio))

    #print the status and returned json
    status = get_data.status_code
    print("Investment Portfolio status: " + str(status))

    if status != 200:
        return get_data
    else:
        data = get_data.json()
        return json.dumps(data, indent=4, sort_keys=True)

def Create_Portfolio_Holdings(portfolio_name,holdings):
    """
    Creates portfolio holdings.
    """
    timestamp = '{:%Y-%m-%dT%H:%M:%S.%fZ}'.format(datetime.datetime.now())
    BASEURL = "https://investment-portfolio.mybluemix.net/api/v1/portfolios/" + portfolio_name + "/holdings"
    headers = {
        'Content-Type': "application/json",
        'Accept': "application/json"
        }
    data = {
        'timestamp': timestamp,
        'holdings': holdings
        }
    get_data = requests.post(BASEURL, auth=(IP_W_username, IP_W_password), headers=headers, data=json.dumps(data))

    #print the status and returned json
    status = get_data.status_code
    print("Investment Portfolio Holding status: " + str(status))

    if status != 200:
        return get_data.json()
    else:
        data = get_data.json()
        return json.dumps(data, indent=4, sort_keys=True)

def Delete_Portfolio(portfolio_name,timestamp,rev):
    """
    Deletes a portfolio.
    """
    BASEURL = "https://investment-portfolio.mybluemix.net/api/v1/portfolios/" + str(portfolio_name) + "/" + str(timestamp) + "?rev=" + str(rev)
    headers = {
        'Content-Type': "application/json",
        'Accept': "application/json",
        'Authorization':"Basic aGV5cmVsc2VuZG9udHJhdGlyc2VudWVuOjM4NDUzNTZjNzY2NTY4NTA0YjkyYzM3ZDJiOGVkZTkzZWYzMTg0NTA="
        }
    res = requests.delete(BASEURL, auth=(IP_W_username, IP_W_password), headers=headers)

    #print the status and returned json
    status = res.status_code
    print("Investment Portfolio delete status: " + str(status))

    if status != 200:
        return res
    else:
        return "Portfolio " + portfolio_name + " deleted successfully."

def Delete_Portfolio_Holdings(portfolio_name,timestamp,rev):
    """
    Deletes a portfolio.
    """
    BASEURL = "https://investment-portfolio.mybluemix.net/api/v1/portfolios/" + str(portfolio_name) + "/holdings/" + str(timestamp) + "?rev=" + str(rev)
    print(BASEURL)
    headers = {
        'Content-Type': "application/x-www-form-urlencoded",
        'Accept': "application/json",
        'authorization':'Basic REPLACE_BASIC_AUTH'
        }
    res = requests.delete(BASEURL, auth=(IP_W_username, IP_W_password), headers=headers)

    #print the status and returned json
    status = res.status_code
    print("Investment Portfolio holdings delete status: " + str(status))

    if status != 200:
        return res
    else:
        return "Portfolio " + portfolio_name + " deleted successfully."