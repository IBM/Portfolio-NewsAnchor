from flask import Flask, render_template, jsonify, json, url_for, request, redirect, Response, flash, abort, make_response, send_file, send_from_directory
from flask_socketio import SocketIO
import requests
import io
import os
import csv
import datetime
import investmentportfolio
from pprint import pprint
from werkzeug.utils import secure_filename
import pickle
import subprocess
import threading

print ('Running portfolio.compute.py')
app = Flask(__name__)
socketio = SocketIO(app, async_mode='gevent')

bloomUsProcess = None
bloomGlobProcess = None
skyProcess = None
cnbcAfricaProcess = None

bloomUsNews = 'https://www.bloomberg.com/live/us'
bloomGlobNews = 'https://www.bloomberg.com/live'
skyNews = 'https://www.youtube.com/watch?v=XOacA3RYrXk'
cnbcAfricaNews = 'https://www.youtube.com/watch?v=IpmKglKxQpA'

# On Bluemix, get the port number from the environment variable VCAP_APP_PORT
# When running this app on the local machine, default the port to 8080
port = int(os.getenv('VCAP_APP_PORT', 8080))
host='0.0.0.0'

# I couldn't add the services to this instance of the app so VCAP is empty
# do this to workaround for now
if 'VCAP_SERVICES' in os.environ:
    if str(os.environ['VCAP_SERVICES']) == '{}':
        print ('Using a file to populate VCAP_SERVICES')
        with open('VCAP.json') as data_file:
            data = json.load(data_file)
        os.environ['VCAP_SERVICES'] = json.dumps(data)

#======================================RUN LOCAL======================================
# stuff for running locally
if 'RUN_LOCAL' in os.environ:
    print ('Running locally')
    port = int(os.getenv('SERVER_PORT', '5555'))
    host = os.getenv('SERVER_HOST', 'localhost')
    with open('VCAP.json') as data_file:
        data = json.load(data_file)
    os.environ['VCAP_SERVICES'] = json.dumps(data)

#======================================MAIN PAGES======================================
@socketio.on('user_connect')
def handle_msg(msg):
    print(msg)

@app.route('/')
def run():
    """
    Load the site page
    """
    return render_template('index.html')

@app.route('/api/uploadvid', methods=['POST'])
def upload_video():
    #clean
    for root, dirs, files in os.walk('clips/'):  
        for filename in files:
            os.remove('clips/' + filename)
    
    #storing video
    data = request.files['file']
    data.save("processor/" + secure_filename(data.filename))
    print("Ash - video uploaded")
    return json.dumps({'success':'true'}), 200, {'ContentType':'application/json'}

@app.route('/clips/<path:path>')
def get_file(path):
    return send_from_directory('clips/', path, as_attachment=True)

@app.route('/api/getvid', methods=['GET'])
def get_video():
    f = open("cnbc.mp4", "r")
    data = f.read()
    return render_template('videorender.html', videosrc=data)

@app.route('/api/upload', methods=['POST'])
def portfolio_from_csv():
    """
    Loads a portfolio in Algo Risk Service (ARS) format into the Investment Portfolio service.
    """
    holdings = {
        'timestamp':'{:%Y-%m-%dT%H:%M:%S.%fZ}'.format(datetime.datetime.now()),
        'holdings':[]
    }
    data = json.loads(request.data)
    print(data)
    data = [row.split(',') for row in data]
    headers = data[0]
    #Loop through and segregate each portfolio by its identifier (there may be multiple in the file)
    #Column 1 (not 0) is the ID column. Column 5 is the PORTFOLIO column...
    portfolios = {}
    unique_id_col =  headers.index("UNIQUE ID")
    id_type_col =  headers.index("ID TYPE")
    name_col =  headers.index("NAME")
    pos_units_col =  headers.index("POSITION UNITS")
    portfolio_col =  headers.index("PORTFOLIO")
    price_col =  headers.index("PRICE")
    currency_col =  headers.index("CURRENCY")

    #for d in data...
    for d in data[1:]:
        hldg = {
            "name":d[name_col],
            "instrumentId":d[unique_id_col],
            "quantity":d[pos_units_col]
        }
        if len(headers)>5:
            for meta in headers[6:]:
                hldg[meta.replace('\r','')] = d[headers.index(meta)].replace('\r','')
        
        if d[portfolio_col] not in portfolios:       
            portfolios[d[portfolio_col]] = [hldg]
        else:
            portfolios[d[5]].append(hldg)
    
    #Send each portfolio and its holdings to the investment portfolio service
    for key, value in portfolios.items():
        my_portfolio = {
            "timestamp": '{:%Y-%m-%dT%H:%M:%S.%fZ}'.format(datetime.datetime.now()) ,
            'closed':False,
            'data':{'type':'news anchor portfolio'},
            'name':key
        }
    try:
        req  = investmentportfolio.Create_Portfolio(my_portfolio)
    except:
        print("Unable to create portfolio for " + str(key) + ".")

    try:
        for h in range(0,len(value),100):
            hldgs = value[h:h+100]
            req  = investmentportfolio.Create_Portfolio_Holdings(str(key),hldgs)
    except:
        print("Unable to create portfolio holdings for " + str(key) + ".")
       
    return req


#Returns list of 'unit test' portfolios
@app.route('/api/news_anchor_portfolios',methods=['GET'])
def get_unit_test_portfolios():
    '''
    Returns the available user portfolio names in the Investment Portfolio service.
    Uses type='news anchor portfolio' to filter.
    '''
    portfolio_names = []
    res = investmentportfolio.Get_Portfolios_by_Selector('type','news anchor portfolio')
    try:
        for portfolios in res['portfolios']:
            portfolio_names.append(portfolios['name'])
        #returns the portfolio names as list
        print("Portfolio_names:" + str(portfolio_names))
        return json.dumps(portfolio_names)
    except:
        return "No portfolios found."

#Deletes all unit test holdings and portfolios for cleanup
@app.route('/api/news_anchor_delete',methods=['GET'])
def get_unit_test_delete():
    '''
    Deletes all portfolios and respective holdings that are of type 'news anchor'
    '''
    portfolios = investmentportfolio.Get_Portfolios_by_Selector('type','news anchor portfolio')['portfolios']
    print(portfolios)
    for p in portfolios:
        holdings = investmentportfolio.Get_Portfolio_Holdings(p['name'],False)
        # delete all holdings
        for h in holdings['holdings']:
            timestamp = h['timestamp']
            rev = h['_rev']
            investmentportfolio.Delete_Portfolio_Holdings(p['name'],timestamp,rev)
        investmentportfolio.Delete_Portfolio(p['name'],p['timestamp'],p['_rev']) 
    return "Portfolios deleted successfully."

#Calculates unit tests for a list of portfolios
@app.route('/api/news_anchor',methods=['POST'])
def compute_unit_tests():
    global bloomUsProcess, bloomGlobProcess, skyProcess, cnbcAfricaProcess, bloomUsNews, bloomGlobNews, skyNews, cnbcAfricaNews
    '''
    Calculates analytics for a portfolio.
    Breaks into 500 instrument chunks to comply with container constraints.
    '''
    print('Ash - Inside computing')
    if (bloomUsProcess != None):
        bloomUsProcess.terminate()
        bloomUsProcess = None
    if (bloomGlobProcess != None):
        bloomGlobProcess.terminate()
        bloomGlobProcess = None 
    if (skyProcess != None):
        skyProcess.terminate()
        skyProcess = None 
    if (cnbcAfricaProcess != None):
        cnbcAfricaProcess.terminate()
        cnbcAfricaProcess = None 
    
    portfolios = []
    feeds = None
    if request.method == 'POST':
        data = json.loads(request.data)
        portfolios.append(data["portfolio"])
        feeds = data["feeds"]
        print(portfolios)
        print(feeds)
    else:
        return "API not available through GET"
    
    #clean
    for root, dirs, files in os.walk('clips/'):  
        for filename in files:
            os.remove('clips/' + filename)

    if len(feeds) == 0:
        return json.dumps({'success':'false', 'metadata':'No feeds selected'}), 400, {'ContentType':'application/json'}

    #Stopwatch
    start_time = datetime.datetime.now()
   
    tickers = []
    for p in portfolios:
        portfolio_start = datetime.datetime.now()
        holdings = investmentportfolio.Get_Portfolio_Holdings(p,False)['holdings']
        #Since the payload is too large, odds are there are 500-instrument chunks added to the portfolio.
        for ph in range(0,len(holdings)):
            #names = [row['instrumentId'] for row in holdings[ph]['holdings']]
            print(ph)
            if len(holdings[ph]['holdings']) > 0:
                if 'Ticker' in holdings[ph]['holdings'][0]:
                    tickers = [row['Ticker'] for row in holdings[ph]['holdings']]

    print(tickers)
    print("Total time elapsed: " + str(datetime.datetime.now() - start_time))

    #initiate processor
    metadataFile = "clips/clip.metadata"

    if bloomUsNews in feeds:
        print("Bloomberg US feed...")
        bloomUsProcess = subprocess.Popen(['python', 'processor/main.py', bloomUsNews], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        t = threading.Thread(target=output_reader_bloom_us, args=(bloomUsProcess,))
        t.start()
    if bloomGlobNews in feeds:
        print("Bloomberg Global feed...")
        bloomGlobProcess = subprocess.Popen(['python', 'processor/main.py', 'https://www.youtube.com/watch?v=Ga3maNZ0x0w'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        t = threading.Thread(target=output_reader_bloom_glob, args=(bloomGlobProcess,))
        t.start()
    if skyNews in feeds:
        print("Sky News feed...")
        skyProcess = subprocess.Popen(['python', 'processor/main.py', skyNews], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        t = threading.Thread(target=output_reader_sky, args=(skyProcess,))
        t.start()
    if cnbcAfricaNews in feeds:
        print("CNBC Africa feed...")
        cnbcAfricaProcess = subprocess.Popen(['python', 'processor/main.py', cnbcAfricaNews], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        t = threading.Thread(target=output_reader_cnbc_africa, args=(cnbcAfricaProcess,))
        t.start()
    
    return json.dumps({'success':'true', 'metadata':'Processor started on feeds' + str(feeds)}), 200, {'ContentType':'application/json'}

def output_reader_bloom_us(proc):
    validCommPrefix = 'parentPing:'
    for line in iter(proc.stdout.readline, b''):
        ocr_str = line.decode('utf-8')
        print(ocr_str)
        if ocr_str.startswith(validCommPrefix):
            ocr_str = ocr_str.lstrip(validCommPrefix)
            socketio.emit('feed-bloom-us', {'data': ocr_str})

def output_reader_bloom_glob(proc):
    validCommPrefix = 'parentPing:'
    for line in iter(proc.stdout.readline, b''):
        ocr_str = line.decode('utf-8')
        print(ocr_str)
        if ocr_str.startswith(validCommPrefix):
            ocr_str = ocr_str.lstrip(validCommPrefix)
            socketio.emit('feed-bloom-glob', {'data': ocr_str})

def output_reader_sky(proc):
    validCommPrefix = 'parentPing:'
    for line in iter(proc.stdout.readline, b''):
        ocr_str = line.decode('utf-8')
        print(ocr_str)
        if ocr_str.startswith(validCommPrefix):
            ocr_str = ocr_str.lstrip(validCommPrefix)
            socketio.emit('feed-sky', {'data': ocr_str})

def output_reader_cnbc_africa(proc):
    validCommPrefix = 'parentPing:'
    for line in iter(proc.stdout.readline, b''):
        ocr_str = line.decode('utf-8')
        print(ocr_str)
        if ocr_str.startswith(validCommPrefix):
            ocr_str = ocr_str.lstrip(validCommPrefix)
            socketio.emit('feed-cnbc-africa', {'data': ocr_str})

if __name__ == '__main__':
    print(str(host) + ":" + str(port))
    socketio.run(app, host=host, port=port)
