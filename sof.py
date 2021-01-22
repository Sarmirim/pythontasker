from __future__ import print_function
from logging import error
import pickle
import os.path
from socket import timeout
from aiohttp.client_exceptions import ClientConnectionError, ContentTypeError
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from aiohttp import ClientSession
import time
import requests
import aiohttp
import asyncio
import pypeln as pl
import threading
from threading import Thread
from multiprocessing import Process

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1jT1YVDCQm5j_BlLROUZrParnTiC3jUzpI8AVN7pEi10'
SAMPLE_RANGE_NAME = 'Proxylist!A2:D10000'

async def googlesheet():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME).execute()
    values = result.get('values', [])

    newlist = {}
    num = 0
    if not values:
        print('No data found.')
    else:
        for row in values:
            # check('http://%s:%s@%s:%s' % (row[2], row[3], row[0], row[1]))
            newlist[num] = {'user':row[2], 'pass':row[3], 'ip':row[0], 'port':row[1]}
            num+=1
            # newlist.append('http://%s:%s@%s:%s' % (row[2], row[3], row[0], row[1]))

            # print('http://%s:%s@%s:%s' % (row[2], row[3], row[0], row[1]))
    print(num)
    await controller(list(newlist.values()))

async def check(item):
    prox = ('http://%s:%s@%s:%s' % (item['user'], item['pass'], item['ip'], item['port']))
    proxy = f"{item['ip']}:{item['port']}:{item['user']}:{item['pass']}"
    status = 0
    problem = None
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('http://142.93.171.79:3000/test', proxy=prox, timeout=10) as response:
                if(response.status!=200):
                    raise Exception(response.reason)
                resp = await response.json(content_type='application/json')
                status = 1
    # except aiohttp.ServerDisconnectedError as SDE:
    #     print(SDE)
    #     return 0
    except ClientConnectionError as CCE:
        problem = CCE.message
    except asyncio.exceptions.TimeoutError as TE:
        problem = "Timeout"
    # except ContentTypeError as CTE:
    #     print("ContentTypeError")
    except Exception as error:
        problem = error
    finally:
        if(problem == None and status == 0):
            print('asdasd')
        return {"proxy": proxy, "status": status, "problem": problem, "ip":item['ip'], "port": item['port'],
         "user": item['user'], "pass": item['pass']}

async def make_requests(list):
# async with ClientSession() as session:
    firsthalf = list[:len(list)//2]
    secondhalf = list[len(list)//2:]
    tasks1 = []
    tasks2 = []
    for prox in firsthalf:
        tasks1.append(check(prox))
    # for prox in secondhalf:
    #     tasks2.append(check(prox))
    results = await asyncio.gather(*tasks1, *tasks2)
    return results

async def controller(list):
    currentlist = list
    numberOfChecks = 1
    seconds = 1
    while seconds<=32:
        results = await make_requests(currentlist)
        # print(results)
        currentlist = []
        ones = 0
        zeros = 0
        for item in results:
            if item["status"]==0:
                currentlist.append(item)
                zeros+=1
            else:
                ones+=1
        if(len(currentlist)==0):
            seconds*=100
        print('len = ', len(results))
        print('0 = ', zeros)
        print('1 = ', ones)
        numberOfChecks-=1
        seconds*=2
        await asyncio.sleep(seconds)
        if(seconds>32):
            seconds = 1



async def main():
    await asyncio.gather(googlesheet())

if __name__ == '__main__':
    asyncio.run(main())
    # asyncio.run(main())