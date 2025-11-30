import json
import requests
import pprint
import pandas as pd
#from requests.exceptions import HTTPError
import os

my_file="out.csv"
try:
    if os.path.exists(my_file):
        os.remove(my_file)
    else:
        print("The file does not exist")
except OSError as e:
    print("Error: %s : %s" % (file_path, e.strerror))

try:
    def webhook(position1):
        #position1 = "E30476"
        #position1 = "User111"
        #period1 = "October 2019"
        apidomain = "https://XXXX.callidusondemand.com/api/v2/"
        resulttbl = "paymentSummarys?"
        participanttbl = "participants?"
        participantfilter = "$filter=payeeId eq "+"'"+       position1  +"'" 
        partselect = "&select=payeeSeq,payeeId,firstName,middleName,lastName,terminationDate,hireDate,businessUnits"
        filter = "&$filter=participant/payeeId eq "+"'"+       position1  +"'"
        expand = "expand=participant,processingUnit,position,period"
        select = "&select=participant,period,businessUnits,processingUnit,position,payment"
        skip = "&skip=0&top=100"
        sort = "&orderBy=period asc "
        headers = {'authorization': "Basic XXXXXXXXXXXXXXXXXXXXXXXXXX==",'cache-control': "no-cache",'Accept':"application/json"}
            

        response = requests.request("GET", apidomain+resulttbl+expand+filter+select+skip+sort, headers=headers)
        response.raise_for_status()     
        response.encoding = 'utf-8' 
        paymentdata = response.json()
        paymentdata = json.dumps(paymentdata['paymentSummarys'])
        
        response1 = requests.request("GET", apidomain+participanttbl+participantfilter+partselect+skip, headers=headers)
        response1.encoding = 'utf-8' 
        payee = response1.json()
        payee = json.dumps(payee["participants"])
        dfpar = pd.read_json(payee)
        #print(dfpar)
        
                
        
        df = pd.read_json(paymentdata)
        #print(paymentdata)
        paymentdata = json.loads(paymentdata)
        if len(paymentdata[0]['businessUnits'])>0:
            BU = str(paymentdata[0]['businessUnits'][0]['name'])
        else:
            BU = ''
        if paymentdata[0]['processingUnit']['displayName'] == 'Unassigned':
            PU = ''
        else:
            PU = str(paymentdata[0]['processingUnit']['displayName'])
        #print(PU)
        Position = str(paymentdata[0]['position']['displayName'])
        Participant = str(paymentdata[0]['participant']['displayName'])
        #print(paymentdata)
        df = df[['period','payment']]
        df1 = df['payment']
        df1 = pd.json_normalize(df1)
        df1 = df1.rename(columns={"unitType.name": "Currency"})
        df1 = df1[['value','Currency']]
        df1["new_col"] = df1['Currency'].astype(str) +" "+ df1["value"].astype(str)
        df1.drop(['value', 'Currency'], axis=1, inplace=True)
        
        df4 = df['period']
        df4 = pd.json_normalize(df4)
        df4 = df4.rename(columns={"displayName": "par"})

        df5 = df4['par'].str.split(' ').str[0]
        df6 = df4['par'].str[-4:]
        df6.rename("fields",inplace=True)

    #########################################################################################################################
        dfpar = dfpar[['payeeId','firstName','lastName','hireDate','terminationDate']]
        #print(dfpar['hireDate'].dropna().empty)
        #print(len(dfpar['hireDate']))
        if dfpar['hireDate'].dropna().empty == True:
            dfpar['hireDate'] = 'Not Updated'
        else :
            dfpar['hireDate'] = dfpar['hireDate'].str[0:10]
        #print(dfpar['hireDate'])    
        dfpar2 = dfpar[['payeeId']]        
        #print(dfpar)    
        #dfpar.assign(dfpar=blank)
        for f in dfpar.values:
            d = pd.Series(f, name="par")

    ##########################################################################################################################
        left = pd.DataFrame({"Flag": ["Payouts"],"payeeId": ["Year"]})
        participantframe = pd.DataFrame({"Flag": ["Sales Personal Details"]})
        participantfields = pd.DataFrame({"fields": ["payeeId","First Name","Last Name","Hire Date","Terminate Date"]})
        new_col = pd.DataFrame({"new_col": []})
        

        paymentresults = pd.concat([df6, df5, df1], axis=1)
        #print(paymentresults)
        result1 = pd.merge(participantframe, dfpar2, how="cross")
        result2 = pd.merge(result1,participantfields , how="cross")
        result2.index.rename('foo', inplace=True)  
        result3 = pd.concat([result2, d, pd.get_dummies(new_col)], axis=1)
        result3.index.rename('foo', inplace=True)  
        #print(result3)
        #result3.to_csv('/home/vcap/app/out.csv', encoding='utf-8', mode='a', index=True)
        
    #################################################################################################################################### 
        result = left.merge(paymentresults, how='cross')
        result.index.rename('foo', inplace=True)       
        #result.to_csv('out.csv', encoding='utf-8', index=True, columns=['A','B','Year','month','Payment'])
        #print(final)
        #result.to_csv('/home/vcap/app/out.csv', encoding='utf-8', mode='a', header=False, index=True, columns=['A','B','Year','month','Payment'])
        
        final = pd.concat([result3, result], ignore_index = True)
        final.index.rename('foo', inplace=True)   
        final.to_csv('out.csv', encoding='utf-8', header=True, index=True)
    ####################################################################################################################################        
        return

except requests.exceptions.HTTPError as errh:
    print("Http Error:",errh)
except requests.exceptions.ConnectionError as errc:
    print("Error Connecting:",errc)
except requests.exceptions.Timeout as errt:
    print("Timeout Error:",errt)
except requests.exceptions.RequestException as err:
    print("OOps: Something Else",err)      





##### https://jsonpathfinder.com/
##### https://jsonpath.com/
