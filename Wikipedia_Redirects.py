#Wikipedia redirect compilation script
#Written by Rob Seidman on 4/27/18

import requests
import json

redirect_url = "https://dispenser.info.tm/~dispenser/cgi-bin/rdcheck.py?page="
entities = ['IBM','J._P._Morgan']

#def get_wiki_page_name():

def get_wiki_redirects():
    output = {}
    for e in entities:
        res = requests.get(redirect_url + e)
        res = res.text.split('<ul class="notarget">')[1].split('</ul>')[0].split('</a>')
        alt_names = []
        for r in res:
            n = r.split('redirect=no">')
            if len(n)>1:
                alt_names.append(str(n[1]))
        #alt_names = [row for row in alt_names if 'redirect' not in row]# and '<li>' not in row]
        output[e] = alt_names
    print(output)

get_wiki_redirects()