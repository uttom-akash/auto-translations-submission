import requests
from lxml.html import fromstring
from time import sleep
# from lxml import etree
import argparse
import json

def get_arguments():
    # argument template
    parser=argparse.ArgumentParser()
    parser.add_argument('-nt','--n_translate',type=int,default=1,help='Number of translations')
    parser.add_argument('-c','--cookie',default="",help='Your cookie')
    
    args=parser.parse_args()
    n_translate=args.n_translate
    cookie=args.cookie
    if cookie=="":
        parser.print_help()
        exit()

    return {"n_translate":n_translate,"cookie":cookie}

def parse_response(response_ojbect):
    dom=fromstring(response_ojbect.content)
    bntext=dom.xpath('.//input[@name="bntext"]/@value')[0]
    engAns=dom.xpath('.//textarea/text()')[0]
    bangla_to_english = dom.xpath('.//h3/text()')

    return {"bntext":bntext,'engAns':engAns,"bangla":bangla_to_english[0],"english":bangla_to_english[1]}

def get_cookiejar(cookie):
    jar=requests.cookies.RequestsCookieJar()
    jar.set("connect.sid",cookie)
    
    return jar

def print_current_translations(data):
    print("_"*5," Bangla  ","_"*5)
    print(data['bangla'])
    print("_"*5," English ","_"*5)
    print(data['english'])
    print('Submitting...    ')

def write_to_file(data):
    with open("submission_history.json",'w',encoding='utf-8') as writer:
        json.dump(data,writer, ensure_ascii=False,indent=4)

def main():
    args=get_arguments() 

    # request params
    content_url="https://banglasketch.org/SuPara"
    submit_url='https://banglasketch.org/submitTranslation'
    headers={
      "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
      "accept-language": "en-US,en;q=0.9",
      "cache-control": "max-age=0",
      "content-type": "application/x-www-form-urlencoded",
      "sec-fetch-dest": "document",
      "sec-fetch-mode": "navigate",
      "sec-fetch-site": "same-origin",
      "sec-fetch-user": "?1",
      "upgrade-insecure-requests": "1"
    }
    user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36'
    cookie=get_cookiejar(args['cookie'])

    # initial request
    response_object=requests.get(content_url,headers={'User-Agent':user_agent},cookies=cookie)
    data=parse_response(response_object)

    n_translate=args["n_translate"]
    total=n_translate
    bangla_to_english_list=[]
    
    try:
        while n_translate>0:
            print("\nTrying to translate: ",total-n_translate+1)
            print_current_translations(data)
            bangla_to_english_list.append({"bangla":data['bangla'],'english':data['english']})

            # sleeping for 2 sec so that the websites doesn't ban me
            sleep(1)
            response_object=requests.post('https://banglasketch.org/submitTranslation',headers=headers,data=data,cookies=cookie)
            data=parse_response(response_object)
            n_translate=n_translate-1
            print("Submitted")
    except:
        raise
    finally:
        if len(bangla_to_english_list)>0:
            write_to_file(bangla_to_english_list)

if __name__=='__main__':
    try:
        main()
    except IndexError:
        print("Your cookie is not valid")
    