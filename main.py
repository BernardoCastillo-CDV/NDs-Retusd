import re
from google.cloud import storage
from flask import Flask, request, make_response
from google.cloud import bigquery
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import requests
from cdv_tools.gcp_clients.gsheet import GSheet_Client
import os
import pandas as pd
import datetime as dt
import requests
import json
from datetime import date, datetime
from nd import gerar_nota

app = Flask(__name__, template_folder='templates', static_folder='static')

#função para acessar dados do sheets
def get_records_from_sheet():
        sheet_id = '1iqQz0pfVxRMnBOxp7iS05-5ciOeoZx-2ni8h4G6hZkY'
        
        saccount_email = 'default-cf@portfolio-comercializadora.iam.gserviceaccount.com'

        gsheet_client = GSheet_Client(saccount_email=saccount_email, default_spreadsheet_id=sheet_id)

        data = gsheet_client.sheets.get_by_sheet_name(sheet_name='A RECEBER')
        
        df = pd.DataFrame(data)
    
        return df

def get_records_from_sheet_SAP():
    sheet_id = '1lp3s2-hIvEh_rU1fJUrdge_HNTYaPYUeyJdRRo43SWU'
    #saccount_email = 'get-var-info@portfolio-comercializadora.iam.gserviceaccount.com'
    saccount_email = 'default-cf@portfolio-comercializadora.iam.gserviceaccount.com'

    gsheet_client = GSheet_Client(saccount_email=saccount_email, default_spreadsheet_id=sheet_id)

    data = gsheet_client.sheets.get_by_sheet_name(sheet_name='SAP')
    
    # for column in data.columns:
    #     if column  in ['Parte - Código do Perfil', 'ContraParte - Código do Perfil', 'RETUSD', 'TUSD CONTRATO', 'TUSD APURADA CCEE', 'COBRAR']:
    #         data[column] = pd.to_numeric(data[column]).isnull()


    df = pd.DataFrame(data)
    
    return df

#função para acessar dados do thunders
def get_thunders_data(gcs_client, file_prefix) -> pd.DataFrame:

    price_bucket = gcs_client.bucket('thunders-operations')

    blob_name = f"current.csv"
    blob = price_bucket.blob(blob_name)
    blob.reload()

    filename = file_prefix+"thuders_data.csv"
    blob.download_to_filename(filename)
    col_read = ['partyProfileCode', 'counterpartyProfileCode','partyCNPJ','counterpartyCNPJ']
    df = pd.read_csv(filename, sep=";",usecols=col_read)
   
    
    return df


    
def formatar_coluna(input_float):
        pre_string = f"{input_float:,.2f}"
        out_string = pre_string.replace(",",";").replace(".",",").replace(";",".")

        return out_string
    

@app.route("/")


def flask_receive_request():
    return receive_request(request=request)

def receive_request(request=request):
    
    # Gerando as bases que precisamos pra gerar a nota

    # 1) Base do SAP

    sap_ext = get_records_from_sheet_SAP()

    sap_ext['Nome 2'] = sap_ext['Nome 2'].fillna("")

    sap_ext['Nome'] = sap_ext['Nome 1'].apply(str).str.cat(sap_ext['Nome 2'],sep = " ")

    sap = sap_ext[['Nome','Local', 'Bairro', 'Rua', 'Código postal', 'Região', 'Telefone 1', 'Nº ID fiscal 1']]

    rename_col = {'Nome': 'Nome',
                'Local': 'Cidade',
                'Bairro': 'Bairro',
                'Rua': 'Endereço',
                'Código postal':'CEP',
                'Região': 'UF',
                'Telefone 1': 'Telefone',
                'Nº ID fiscal 1':'CNPJ'}

    sap = sap.rename(columns=rename_col)

    sap['CNPJ'] = sap['CNPJ'].astype("str")

    CNPJ = pd.DataFrame()

    CNPJ['pt1'] = sap['CNPJ'].str.slice(0,2)
    CNPJ['pt2'] = sap['CNPJ'].str.slice(2,5)
    CNPJ['pt3'] = sap['CNPJ'].str.slice(5,8)
    CNPJ['pt4'] = sap['CNPJ'].str.slice(8,12)
    CNPJ['pt5'] = sap['CNPJ'].str.slice(12,14)

    sap['CNPJ'] = (CNPJ['pt1'].str.cat([CNPJ['pt2'],CNPJ['pt3']],sep='.')).str.cat(CNPJ['pt4'],sep="/").str.cat(CNPJ['pt5'],sep='-')

    sap = sap.rename(columns=rename_col)

    sap['Telefone'] = sap['Telefone'].fillna(0)

    sap['Telefone'] = sap['Telefone'].round(0)

    sap['Telefone'] = sap['Telefone'].astype("str")

    sap['Telefone'] = sap['Telefone'].str.slice(0,-2)

    
    # Pegando a base do Thunders para conseguirmos os cnpjs das empresas 

    thunders = get_thunders_data()

    cnpj_base = thunders[['partyProfileCode' , 'counterpartyProfileCode','partyCNPJ','counterpartyCNPJ']].drop_duplicates().copy().reset_index(drop = True)
    cnpj_base = cnpj_base.dropna(subset=['partyProfileCode', 'counterpartyProfileCode'])
    cnpj_base['partyProfileCode'] = cnpj_base['partyProfileCode'].astype('int64')
    cnpj_base['counterpartyProfileCode'] = cnpj_base['counterpartyProfileCode'].astype('int64')

    # Base de dados de sheets

    sheets = get_records_from_sheet()

    print(sheets["COBRAR\nR$"])

    sheets["COBRAR\nR$"] = sheets["COBRAR\nR$"].apply(str).str.replace(",",".")

    sheets["COBRAR\nR$"] = pd.to_numeric(sheets["COBRAR\nR$"])

    sheets["Parte - Código do Perfil"] = pd.to_numeric(sheets["Parte - Código do Perfil"])

    sheets["ContraParte - Código do Perfil"] = pd.to_numeric(sheets["ContraParte - Código do Perfil"])

    sheets["COBRAR\nR$"]= sheets["COBRAR\nR$"].round(2)

    sheets = sheets[sheets["RECEBIDO"].isnull()]

    base = sheets.copy().reset_index(drop= True)

    base = base[base["COBRAR\nR$"]>0]

    bf = base.copy().reset_index(drop = True)

#Filtro das cobranças

    bf = bf[['Parte - Perfil','Parte - Código do Perfil','Contraparte - Perfil','ContraParte - Código do Perfil','Mês','COBRAR\nR$']]
    bf = bf.sort_values(by=['Parte - Código do Perfil','ContraParte - Código do Perfil'])
    code_list= [27977, 28024, 50609, 51810, 49254]
    bf = bf[bf['Parte - Código do Perfil'].isin(code_list)]
    bf = bf[-bf['ContraParte - Código do Perfil'].isin(code_list)]

    print(sheets["COBRAR\nR$"])

    df = bf[['Parte - Perfil','Parte - Código do Perfil','Contraparte - Perfil','ContraParte - Código do Perfil','Mês']].drop_duplicates().copy().reset_index(drop = True)
    code_list= [27977, 28024, 50609, 51810, 49254]
    df = df[df['Parte - Código do Perfil'].isin(code_list)]
    df = df[-df['ContraParte - Código do Perfil'].isin(code_list)]

    
#filtro mínimo para cobrança(soma dos valores das notas das empresas > 10)
    bf2 = pd.DataFrame(bf.groupby(['Parte - Perfil','Parte - Código do Perfil','Contraparte - Perfil','ContraParte - Código do Perfil'])["COBRAR\nR$"].agg(['sum']))

    bf2 = bf2[bf2["sum"]>=10]

    merged = pd.merge(bf2,df,how='inner',on=['Parte - Código do Perfil','ContraParte - Código do Perfil'])

    merged2 = pd.merge(bf,merged,how = 'inner', on=['Parte - Perfil','Parte - Código do Perfil','Contraparte - Perfil','ContraParte - Código do Perfil','Mês'])

    
#total a cobrar por empresa( soma das nd)
    total_cobranca = bf2
    total_cobranca= pd.DataFrame(total_cobranca.groupby(['Contraparte - Perfil','ContraParte - Código do Perfil','sum']))

        
#obtendo informações das empresas
    merged2 = merged2.drop(columns=['sum'],axis=1)
    merged2 = merged2.rename(columns={'COBRAR\nR$':'Cobrar'})
    
    bf3 = pd.DataFrame(merged2.groupby(['Parte - Perfil','Parte - Código do Perfil','Contraparte - Perfil','ContraParte - Código do Perfil','Mês'])["Cobrar"].agg(['sum']))

    merged3 = pd.merge(bf3,df,how='inner',on=['Parte - Perfil','Parte - Código do Perfil','Contraparte - Perfil','ContraParte - Código do Perfil','Mês'])

    merged3['sum'] = merged3['sum'].round(2)

    merged3.to_csv('help2.csv',index = False)
    
    bf4 = pd.merge(merged3,cnpj_base,how='inner',left_on=['Parte - Código do Perfil','ContraParte - Código do Perfil'],right_on=['partyProfileCode','counterpartyProfileCode'])

    bf4 = bf4.drop(columns=['partyProfileCode','counterpartyProfileCode'])

    base_final = bf4.merge(sap,how='inner',left_on=['counterpartyCNPJ'],right_on=['CNPJ'])


    base_final.drop(columns='CNPJ')

    base_final = base_final[['Nome','counterpartyCNPJ','Endereço','Bairro','Cidade','UF','CEP','Telefone','Mês','sum']]

    base_final['vencimento'] = (dt.datetime.today()+dt.timedelta(days=30)).strftime("%d/%m/%Y")

    base_final['base'] = 'Fortaleza - CE, ' + dt.datetime.today().strftime("%d/%m/%Y")

    base_final['file_name'] = base_final['Mês'] + base_final['Nome'].str.slice(0,4) 

    base_final.to_csv('bf.csv',index = False)

    base_final.head()
    
    base_final['sum']=base_final.apply(lambda x: formatar_coluna(float(x["sum"])),axis=1) 
    print(base_final['sum'])

    date_today = date.today()
    year_date = date_today.strftime( "%Y")
    day_date = date_today.strftime("%d")
    mounth_date = int(date_today.strftime("%m"))
    mounth = ['Janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']
    print(mounth_date)
    
    for i in range(len(base_final)):
    
        name= "ND" + "-" + str(base_final['file_name'].iloc[i]) + ".pdf"
        
        file_prefix = os.environ.get("FILE_PREFIX","/tmp/")
        name_p = file_prefix + name
        
        nd = gerar_nota(name_p,base_final,i,day_date, mounth, mounth_date, year_date)
        
        #gcs_client = storage.Client(project='portfolio-comercializadora')
        #bucket_name = "notas-de-debito"
        #bucket = gcs_client.bucket(bucket_name)
        #blob = bucket.blob( str(date_today) + "/"+ 'Notas_Compra/' + str(base_final.iloc[i]['Nome']) + '/' + name) 
        #blob.upload_from_filename(name_p)

    return 'ok', 200



