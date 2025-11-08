from flask import Flask, request, jsonify,send_from_directory, send_file,make_response,abort
from flask_cors import CORS
import sys
import requests
from bs4 import BeautifulSoup
import re
from dateutil.parser import parse
import os
from datetime import datetime, date
import pandas as pd
from urllib.parse import urljoin, urlparse
import fitz
from docx import Document
import docx
# import win32com.client
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
# import pythoncom
import webbrowser
from jinja2 import Environment, FileSystemLoader
# from IPython.display import display, HTML
import PyPDF2


from website_extraction.EU.health_ec import health_ec as health_ec
from website_extraction.EU.eux import eux as eux
from website_extraction.EU.ec import ec as ec
from website_extraction.USA.ecfr import ecfr as ecfr
from website_extraction.Japan.japlawtrans import japlaw as japlaw
from website_extraction.Singapore.sso import sso as sso
from website_extraction.Singapore.hsa import hsa as hsa
from website_extraction.Korea.korea import korea as korea
from website_extraction.Japan.Jaish import jaish as jaish
from website_extraction.Japan.mhlw import mhlw as mhlw
from website_extraction.China.emsd import emsd as emsd
from website_extraction.China.Shangai import Shangai as Shangai
from website_extraction.China.elegislation import elegislation as elegislation
from website_extraction.Canada.bc_laws import bc_laws as bc_laws
from website_extraction.Australia.nsw_au import nsw_au as nsw_au
from website_extraction.Australia.health_au import health_au as health_au
from website_extraction.USA.fda_access import fda_access as fda_access
from website_extraction.USA.fda import fda as fda
from website_extraction.Japan.e_gov import e_gov as e_gov
from website_extraction.USA.gov_info import govinfo as govinfo


# from langchain.chat_models import AzureChatOpenAI
from langchain_openai import AzureChatOpenAI
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores import FAISS
# from langchain_community.vectorstores.faiss import FAISS
from langchain.prompts import PromptTemplate
from langchain.chains.summarize import load_summarize_chain
from langchain.chains.question_answering import load_qa_chain
from langchain.docstore.document import Document as doc

from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate

from langchain.text_splitter import RecursiveCharacterTextSplitter
from key import azure_api_key
from datetime import datetime
from fuzzywuzzy import fuzz, process
import simplejson 
from sentence_transformers import SentenceTransformer, util
from pathlib import Path
from mailmerge import MailMerge
from PyPDF2 import PdfReader

from flask_caching import Cache
import hashlib
import json

from rouge_score import rouge_scorer
from transformers import BertTokenizer, BertForMaskedLM, BertModel
from bert_score import BERTScorer

from website_extraction.keywords import keywords_list 
import tempfile

data_dict= {('APAC',
  'Association of South East Asian Nations (ASEAN)'): {'Region': 'APAC', 'country': 'Association of South East Asian Nations (ASEAN)', 'Key': 'APAC_ASEAN'},
 ('APAC', 'Australia (AUS)'): {'Region': 'APAC',  'country': 'Australia (AUS)',  'Key': 'APAC_AUS'}, ('APAC', 'Australia and New Zealand (AUS_NZL)'): {'Region': 'APAC',  'country': 'Australia and New Zealand (AUS_NZL)',
  'Key': 'APAC_AUS_NZL'}, ('APAC', 'Bangladesh (BGD)'): {'Region': 'APAC',  'country': 'Bangladesh (BGD)',  'Key': 'APAC_BGD'}, ('APAC', 'Hong Kong (HKG)'): {'Region': 'APAC',  'country': 'Hong Kong (HKG)',
  'Key': 'APAC_HKG'}, ('APAC', 'Indonesia (IDN)'): {'Region': 'APAC',  'country': 'Indonesia (IDN)',  'Key': 'APAC_IDN'}, ('APAC', 'India (IND)'): {'Region': 'APAC',  'country': 'India (IND)',  'Key': 'APAC_IND'}, ('APAC', 'Cambodia (KHM)'): {'Region': 'APAC',
  'country': 'Cambodia (KHM)',  'Key': 'APAC_KHM'}, ('APAC', 'Republic of Korea (KOR)'): {'Region': 'APAC',  'country': 'Republic of Korea (KOR)',
  'Key': 'APAC_KOR'}, ('APAC', 'Sri Lanka (LKA)'): {'Region': 'APAC',  'country': 'Sri Lanka (LKA)',  'Key': 'APAC_LKA'}, ('APAC', 'Myanmar (MMR)'): {'Region': 'APAC',
  'country': 'Myanmar (MMR)',  'Key': 'APAC_MMR'}, ('APAC', 'Malaysia (MYS)'): {'Region': 'APAC',  'country': 'Malaysia (MYS)',  'Key': 'APAC_MYS'}, ('APAC', 'New Zealand (NZL)'): {'Region': 'APAC',  'country': 'New Zealand (NZL)',  'Key': 'APAC_NZL'}, ('APAC', 'Pakistan (PAK)'): {'Region': 'APAC',  'country': 'Pakistan (PAK)',  'Key': 'APAC_PAK'},
 ('APAC', 'Philippine (PHL)'): {'Region': 'APAC',  'country': 'Philippine (PHL)',  'Key': 'APAC_PHL'}, ('APAC', 'Singapore (SGP)'): {'Region': 'APAC',  'country': 'Singapore (SGP)',
  'Key': 'APAC_SGP'}, ('APAC', 'Thailand (THA)'): {'Region': 'APAC',  'country': 'Thailand (THA)',  'Key': 'APAC_THA'}, ('APAC', 'Taiwan (TWN)'): {'Region': 'APAC',  'country': 'Taiwan (TWN)',  'Key': 'APAC_TWN'}, ('APAC', 'Vietnam (VNM)'): {'Region': 'APAC',  'country': 'Vietnam (VNM)',  'Key': 'APAC_VNM'}, ('ECN', 'China (CHN)'): {'Region': 'ECN',
  'country': 'China (CHN)',  'Key': 'ECN_CHN'}, ('EEU', 'Customs union (CU)'): {'Region': 'EEU',  'country': 'Customs union (CU)',  'Key': 'EEU_CU'}, ('EEU', 'Europe Union (EU)'): {'Region': 'EEU',  'country': 'Europe Union (EU)',  'Key': 'EEU_EU'}, ('EEU', 'France (FRA)'): {'Region': 'EEU',  'country': 'France (FRA)',  'Key': 'EEU_FRA'}, ('EEU',
  'United Kingdom of Great Britain and Northern Ireland (GBR)'): {'Region': 'EEU', 'country': 'United Kingdom of Great Britain and Northern Ireland (GBR)', 'Key': 'EEU_GBR'},
 ('EEU', 'Gulf Cooperation Council (GCC)'): {'Region': 'EEU',  'country': 'Gulf Cooperation Council (GCC)',  'Key': 'EEU_GCC'}, ('EEU', 'Morocco (MAR)'): {'Region': 'EEU',  'country': 'Morocco (MAR)',  'Key': 'EEU_MAR'}, ('EEU', 'Republic of South Africa (ZAF)'): {'Region': 'EEU',
  'country': 'Republic of South Africa (ZAF)',  'Key': 'EEU_ZAF'}, ('EJP', 'Japan (JPN)'): {'Region': 'EJP',  'country': 'Japan (JPN)',  'Key': 'EJP_JPN'}, ('EUSA', 'Brazil (BRA)'): {'Region': 'EUSA',  'country': 'Brazil (BRA)',
  'Key': 'EUSA_BRA'}, ('EUSA', 'Canada (CAN)'): {'Region': 'EUSA',  'country': 'Canada (CAN)',  'Key': 'EUSA_CAN'}, ('EUSA', 'United States of America (USA)'): {'Region': 'EUSA',
  'country': 'United States of America (USA)',  'Key': 'EUSA_USA'}, ('EJP', 'World Wide (WW)'): {'Region': 'EJP',  'country': 'World Wide (WW)',  'Key': 'EJP_WW'},}

def clean_string(input_string):
                     
    return re.sub(r'[\W_]+', '', input_string)


#RIR Report
def create_reports_folder():
    global reports_folder
    cwd = Path.cwd()
    reports_folder = cwd / 'Reports'

    if not reports_folder.exists():
        reports_folder.mkdir()
        print(f"'Reports' folder created at: {reports_folder}")
    else:
        print(f"'Reports' folder already exists at: {reports_folder}")

    return str(reports_folder)

# Reports Folder
global reports_folder
reports_folder = create_reports_folder()
print(f"The path to 'Reports' folder is: {reports_folder}")

#___________________________________________________________________________________________
#Adding data from flat file 

def clean_col2(value):
    return '_'.join(value.split('_')[:2])

def concatenate_columns(row):

   return row['Col3_Title 1'] + ' ' + row['Col4_Title 2'] + ' ' + row['Col5_Title 3']  + ' ' + row['Col9_RA_interpretation_English']


def split_multiline_entries(df, column_name):
    # Create an empty DataFrame to store the results
    result_df = pd.DataFrame(columns=df.columns)
    
    for index, row in df.iterrows():
        # Split the multiline entries in the specified column
        multiline_entries = str(row[column_name]).split('\n')
        
        for entry in multiline_entries:
            # Create a new row with the same values for other columns
            new_row = row.copy()
            new_row[column_name] = entry
            result_df = pd.concat([result_df, new_row.to_frame().T], ignore_index=True)
    
    return result_df





excel_file = os.path.join(reports_folder, "RMF_Database_Evident.xlsx")
data = pd.read_excel(excel_file, sheet_name = 'Sheet1')

data.dropna(subset=['Col9_RA_interpretation_English'],inplace= True)
data['Col9_RA_interpretation_English'] =data['Col9_RA_interpretation_English'].astype(str)
unwanted_values = ['0','1', 'yes', 'No', '-','　','none','Not mentioned']
data = data[~data['Col9_RA_interpretation_English'].isin(unwanted_values)]



selected_columns = ['Col2_Region_Country_Category', 'Col3_Title 1', 'Col4_Title 2', 'Col5_Title 3', 'Col9_RA_interpretation_English']
data = data[selected_columns]

data = split_multiline_entries(data, 'Col9_RA_interpretation_English')
print("data",data)

data['Col2_cleaned'] = data['Col2_Region_Country_Category'].apply(clean_col2)
data['cleaned_ra_interpretation'] = [clean_string(choice) for choice in data['Col9_RA_interpretation_English']]


filtered_data = data[data['Col4_Title 2'].isin(['Law/regulation name (in local language)','Law/regulation name (in English & Japanese)',	'Common name (in local language)',	'Common name (in English & Japanese)',	'Law/regulation no.',	'Standard name (in local language)',	'Standard name (in English & Japanese)','Standard name (in local language)',	'Standard name (in English & Japanese)', 'External link to regulation'
])]



filtered_data['Col9_RA_interpretation_English']= filtered_data['Col9_RA_interpretation_English'].str.replace('\n', ' ').str.replace('\u3000', ' ').str.replace('\t', ' ')
filtered_data = filtered_data[filtered_data['Col9_RA_interpretation_English'] != '0'].drop_duplicates()
# filtered_data['cleaned_ra_interpretation'] = [clean_string(choice) for choice in filtered_data['Col9_RA_interpretation_English']]
print("The regulation list is ready",filtered_data['cleaned_ra_interpretation'])    

def get_key(region, country):
    return data_dict.get((region, country), {}).get('Key')

def filter_dataframe_by_key(df, key):
    return df[df['Col2_cleaned'] == key]

def filter_main_sheet(sheet_name):
    global filtered_values
    filtered_data_rmf = filtered_values[filtered_values['Col2_Region_Country_Category'].isin([sheet_name])]
    filtered_data_rmf = filtered_data_rmf.astype(str)
    # filtered_data_rmf['concat_data'] = filtered_data_rmf['Col3_Title 1'].map(str) + ' ' + filtered_data_rmf['Col4_Title 2'].map(str)  + ' ' + filtered_data['Col5_Title 3'].map(str)  + ' ' + filtered_data['Col9_RA_interpretation_English'].map(str) 
    filtered_data_rmf['rmf_data']=filtered_data_rmf.apply(concatenate_columns, axis=1)
    rmf_data = ' '.join(filtered_data_rmf['rmf_data'].astype(str))
    return rmf_data





#__________________________________________________________________________________________________________
#Open Search
google_api_key = 'AIzaSyDyZHZ4YElGtwgwlIA40L9CpzrahhaMGpQ'
search_engine_id = 'a77f9aa08704543e8'

keywords = keywords_list

keywords_para = (" ").join(keywords_list)

result_dict={'http://yjj.sh.gov.cn/': 'No', 'http://www.nhc.gov.cn/': 'No', 'http://www.pudong.gov.cn/scjgj': 'No', 'http://www.smianet.com/': 'No', 'https://www.cmdi.org.cn/': 'No', 'http://www.camdi.org': 'No', 'http://www.mdta.org.cn/': 'No', 'http://www.nmpaied.org.cn/': 'No', 'https://www.mem.gov.cn/': 'No', 'http://www.miit.gov.cn/': 'No', 
             'http://gdfs.customs.gov.cn/customs/index/index.html': 'No', 'http://www.cnca.gov.cn/': 'No', 'https://sthj.sh.gov.cn/': 'No', 'http://scjgj.sh.gov.cn/': 'No', 'http://shanghai.customs.gov.cn/': 'No', 'https://www.ndrc.gov.cn/': 'No', 'http://www.sac.gov.cn/': 'No', 'http://www.npc.gov.cn/': 'No', 'http://www.moj.gov.cn/': 'No',
             'http://www.shanghai.gov.cn': 'Yes', 'https://flk.npc.gov.cn/': 'No', 'http://www.fmprc.gov.cn/chn': 'no', 'https://czj.sh.gov.cn/': 'no', 'https://www.elegislation.gov.hk/': 'Yes', 'https://www.emsd.gov.hk/tc/home/index.html': 'Yes', 'https://www.epd.gov.hk/epd/sc_chi/top.html': 'No', 'https://www.io.gov.mo/cn/legis': 'No', 
             'https://legalinfo.mn/mn': 'No', 'https://mohap.gov.ae/en/home': 'No', 'https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=celex%3A32008R0765': 'Yes', 'https://www.titck.gov.tr/': 'No', "'https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=38658&MevzuatTur=7&MevzuatTertip=5": 'No', 'https://www.health.gov.za/': 'No', 'https://www.sahpra.org.za/': 'No', 
             'https://gazettes.africa/gazettes/za/2024': 'No', 'https://moh.gov.om/en/web/dgpadc/-9': 'No', 'https://www.moh.gov.kw/': 'No', 'https://www.sch.org.bh/en/rules-and-regulations.html': 'No', 'https://www.hsa.gov.sg/medical-devices/guidance-documents': 'No', 'https://health.ec.europa.eu': 'Yes', 
             'https://www.fda.gov/medical-devices/guidance-documents-medical-devices-and-radiation-emitting-products/recent-final-medical-device-guidance-documents': 'Yes', 'https://www.pmda.go.jp/': 'Yes', 'https://www.crsbis.in/BIS/publicdashAction.do': 'No', 'https://elora.aerb.gov.in/ELORA/populateLoginAction.htm': 'No', 
             'https://dot.gov.in/wireless-planning-coordination-wpc': 'Yes','https://eprplastic.cpcb.gov.in/#/plastic/home': 'No', 'http://www.eprbatterycpcb.in/': 'No', 'https://eprewastecpcb.in/': 'No', 'https://cdsco.gov.in/opencms/opencms/en/Home': 'No', 'https://cdscomdonline.gov.in/NewMedDev/Homepage': 'No', 'https://www.hsa.gov.sg/medical-devices/regulatory-overview': 'No ', 
             'https://www.imda.gov.sg/regulations-and-licences/regulations': 'No', 'https://www.tga.gov.au/resources': 'No', 'https://www.arpansa.gov.au/understanding-radiation/what-radiation/what-non-ionising-radiation': 'No', 'https://www.acma.gov.au/': 'Yes', 'https://www.kcc.go.kr/user/ehpMain.do': 'No',
             'https://www.ecfr.gov/current/title-47/chapter-I/subchapter-A/part-2': 'Yes', 'https://www.fcc.gov/wireless-telecommunications?job=rules_and_regulations': 'No', 'https://www.govinfo.gov/content/pkg/FR-2017-11-02/pdf/2017-23217.pdf': 'Yes',
             'http://kouki-ws01.gss.local/pls/regdb/houki_details_disp.disp?i_houki_id=H-000025&i_houki_hansu=1&i_button_disp=on&i_search_flag=01': 'No', 'http://dms-ws01.gss.local/pls/dmdb/dmdb_std_open_document.site_dsp?i_std_control_code=STD000296': 'No', 'http://dms-ws01.gss.local/pls/dmdb/dmdb_std_open_document.site_dsp?i_std_control_code=STD000819': 'No', 
             'http://dms-ws01.gss.local/pls/dmdb/dmdb_std_open_document.site_dsp?i_std_control_code=STD001362': 'No', 'http://dms-ws01.gss.local/pls/dmdb/dmdb_std_open_document.site_dsp?i_std_control_code=STD001360': 'No', 'http://dms-ws01.gss.local/pls/dmdb/dmdb_std_open_document.site_dsp?i_std_control_code=STD000406': 'No', 
             'https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfcfr/CFRSearch.cfm?CFRPart=1000': 'Yes', 'https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfcfr/CFRSearch.cfm?CFRPart=1002': 'Yes', 'https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfcfr/CFRSearch.cfm?CFRPart=1003': 'Yes', 
             'https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfcfr/CFRSearch.cfm?CFRPart=1004': 'Yes', 'https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfcfr/CFRSearch.cfm?CFRPart=1005': 'Yes', 'https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfcfr/CFRSearch.cfm?CFRPart=1010&utm_campaign=Google2&utm_source=fdaSearch&utm_medium=website&utm_term=1010&utm_content=1': 'Yes',
             'https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfcfr/CFRSearch.cfm?CFRPart=1040&utm_campaign=Google2&utm_source=fdaSearch&utm_medium=website&utm_term=1040&utm_content=1': 'Yes', 'https://www.fda.gov/media/110120/download': 'Yes', 'https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfcfr/CFRSearch.cfm?CFRPart=1050': 'Yes', 
             'https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfcfr/CFRSearch.cfm?CFRPart=1020&utm_campaign=Google2&utm_source=fdaSearch&utm_medium=website&utm_term=1020&utm_content=3': 'Yes', 'https://www.govinfo.gov/app/details/CFR-2000-title47-vol1': 'Yes', 'https://apps.fcc.gov/oetcf/kdb/forms/FTSSearchResultPage.cfm?id=44637&switch=P': 'No', 'https://legislation.nsw.gov.au/view/html/inforce/current/act-2017-015': 'Yes', 'https://legislation.nsw.gov.au/view/html/inforce/current/sl-2018-0501#pt.1': 'Yes', 
             'http://www.health.qld.gov.au/radiationhealth/legislation/': 'Yes', 'https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/03039_01#part3': 'Yes', 
             'https://www.ontario.ca/laws/regulation/070438': 'No', 'https://www.ontario.ca/laws/statute/98e15': 'No', 'https://gkml.samr.gov.cn/nsjg/fgs/202210/t20221008_350551.html': 'No', 'http://www.sac.gov.cn/gjbzgg/201427/': 'No', "http://www.sac.gov.cn/SACSearch/search?channelid=97779&templet=gjcxjg_detail.jsp&searchword=STANDARD_CODE='GB%2031241-2014'&XZ=Q": 'No', 'http://www.sac.gov.cn/gzfw/ggcx/gjbzxgtz/201711/t20171114_319231.htm': 'No', 'https://www.samr.gov.cn/jls/zcfg/jlfg/201905/t20190515_293635.html': 'No', 
             'https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=uriserv:OJ.L_.2014.096.01.0357.01.ENG': 'Yes', 
             'https://single-market-economy.ec.europa.eu/single-market/european-standards/harmonised-standards/low-voltage-lvd_en': 'Yes', 'https://ec.europa.eu/docsroom/documents/31221/attachments/1/translations/en/renditions/pdf': 'Yes', 
             'https://ec.europa.eu/docsroom/documents/29121': 'Yes', 
             'https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=OJ:C:2022:247:TOC': 'Yes', 'https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:02011L0065-20200301&from=EN#tocId6': 'Yes', 'http://www.mcinet.gov.ma/sites/default/files/3_Arrete_LVD_BO_6404_Fr.pdf': 'No', 'http://www.douane.gov.ma/dms/loadDocument?documentId=80963&application=circulaire': 'No', 'http://www.douane.gov.ma/dms/loadDocument?documentId=77756&application=circulaire': 'No', 'https://www.google.co.jp/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&ved=2ahUKEwiItrbj-fP8AhULCd4KHbs6DMAQFnoECA4QAQ&url=https%3A%2F%2Fwww.onssa.gov.ma%2Fwp-content%2Fuploads%2F2022%2F06%2FReglementation%2FC.Reglementation-Connexe%2F4.%2520Divers%2FLOI.24-09.FR.pdf&usg=AOvVaw0U5lrBZ3IglxM0NpY6P5iF': 'No', 
             'https://www.mcinet.gov.ma/fr/content/surveillance-du-march%C3%A9': 'No', 'https://www.mcinet.gov.ma/fr/content/les-produits-soumis-%C3%A0-une-r%C3%A9glementation-technique-exigeant-le-marquage-%C2%ABc%D9%85%C2%BB-0': 'No', 'https://www.imanor.gov.ma/rev-nm-app-oblg/': 'No', 'https://www.meti.go.jp/policy/consumer/seian/denan/act.html': 'Yes', 'https://www.meti.go.jp/policy/consumer/seian/denan/hourei/act/tikuzyoukaisetsu.pdf': 'Yes', 'https://www.meti.go.jp/policy/consumer/seian/denan/pse_guide.html': 'Yes', 'https://www.meti.go.jp/policy/consumer/seian/denan/file/06_guide/seller_guide.pdf': 'Yes', 'https://www.meti.go.jp/policy/consumer/seian/denan/cab.html': 'Yes', 'https://www.env.go.jp/chemi/kagaku/hourei/seirei/sei202.pdf': 'No', 'https://www.japaneselawtranslation.go.jp/law/detail/?ft=1&re=01&dn=1&co=01&x=26&y=11&ky=%E5%8A%B4%E5%83%8D%E5%AE%89%E5%85%A8%E8%A1%9B%E7%94%9F%E6%B3%95&page=6': 'Yes', 
             'https://www.japaneselawtranslation.go.jp/law/detail/?ft=1&re=01&dn=1&co=01&x=26&y=11&ky=%E5%8A%B4%E5%83%8D%E5%AE%89%E5%85%A8%E8%A1%9B%E7%94%9F%E6%B3%95&page=7': 'Yes', 'https://laws.e-gov.go.jp/law/325AC0000000303': 'Yes', 'https://www.mhlw.go.jp/web/t_doc?dataId=81004000&dataType=0&pageNo=1': 'Yes', 'https://laws.e-gov.go.jp/law/322AC0000000049': 'Yes', 'https://www.jaish.gr.jp/anzen/hor/hombun/hor1-18/hor1-18-1-1-0.htm': 'Yes', 'https://www.jaish.gr.jp/anzen/hor/hombun/hor1-42/hor1-42-20-1-0.htm': 'Yes', 'https://laws.e-gov.go.jp/law/325AC0000000131': 'Yes', 'https://laws.e-gov.go.jp/law/413CO0000000245': 'Yes', 'https://laws.e-gov.go.jp/law/325M50080000014': 'Yes', 'https://www.japaneselawtranslation.go.jp/ja/laws/view/4164': 'Yes', 'https://www.law.go.kr/lsInfoP.do?lsiSeq=206082&ancYd=20181224&ancNo=16083&efYd=20191225&nwJoYnInfo=N&efGubun=Y&chrClsCd=010202&ancYnChk=0#0000': 'Yes', 'https://www.law.go.kr/%EB%B2%95%EB%A0%B9/%EC%9E%90%EC%9B%90%EC%9D%98%EC%A0%88%EC%95%BD%EA%B3%BC%EC%9E%AC%ED%99%9C%EC%9A%A9%EC%B4%89%EC%A7%84%EC%97%90%EA%B4%80%ED%95%9C%EB%B2%95%EB%A5%A0': 'Yes', 'https://portal.mda.gov.my/documents/regulation/687-medical-device-authority-act-2012-eng/file.html': 'No', 'https://mysafe.kpdnhep.gov.my/portal/post/6': 'No', 'http://www.mcinet.gov.ma/pdf/5-Arrete-CEM-BO_6404_Fr.pdf': 'No', 'https://www.law.go.kr/LSW//lsSc.do?section=&menuId=1&subMenuId=15&tabMenuId=81&eventGubun=060101&query=%EC%A0%84%EA%B8%B0%EC%9A%A9%ED%92%88+%EB%B0%8F+%EC%83%9D%ED%99%9C%EC%9A%A9%ED%92%88+%EC%95%88%EC%A0%84%EA%B4%80%EB%A6%AC%EB%B2%95#undefined': 'Yes', 'https://www.pta.gov.pk/media/telecom_act_170510.pdf': 'No', 'https://sso.agc.gov.sg/Act/HPA2007': 'Yes', 'https://www.hsa.gov.sg/docs/default-source/hprg-mdb/gn-14-r2-guidance-on-the-risk-classification-of-in-vitro-diagnostic-medical-devices-(updated-on-1-june-2018).pdf': 'No', 'https://www.hsa.gov.sg/medical-devices/registration/requirements': 'No', 'http://statutes.agc.gov.sg/aol/search/display/view.w3p;page=0;query=DocId%3A7cc1971c-6237-4f5a-a75c-dd378fc80179%20Depth%3A0%20ValidTime%3A01%2F07%2F2012%20TransactionTime%3A31%2F12%2F2002%20Status%3Ainforce;rec=0;whole=yes': 'No', 'http://statutes.agc.gov.sg/aol/search/display/view.w3p;page=0;query=DocId%3Ab66f6cff-ff65-4bd3-8d25-6f2d3ed97176%20%20Status%3Ainforce%20Depth%3A0;rec=0;whole=yes': 'No', 'http://ghs.cla.gov.tw/CHT/intro/AnnounceData3.aspx?cssid=4': 'No', 'http://www.iosh.gov.tw/English/Publish.aspx?cnid=121': 'No', 'http://law.epa.gov.tw/en/laws/642071703.html': 'No', 'http://www.ratchakitcha.soc.go.th/DATA/PDF/2563/A/055/T_0024.PDF': 'No', 'https://thuvienphapluat.vn/van-ban/EN/The-thao-Y-te/Decree-98-2021-ND-CP-classification-of-medical-devices/495965/tieng-anh.aspx': 'No', 'https://webdesk.jsa.or.jp/books/W11M0090/index/?bunsyo_id=IEC+62133-2+Amd.1+Ed.+1.0%3A2021': 'No', 'https://unece.org/transport/dangerous-goods/un-model-regulations-rev-23': 'No'}

url_db= pd.DataFrame.from_dict(result_dict, orient='index').reset_index()
url_db.columns = ['URL', 'Approved by Legal']
# print(url_db)

#__________________________________________________________________________________________________________
#for LLM
#__________________________________________________________________________________________________________

def calculate_rouge(reference_summary, generated_summary):
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
    scores = scorer.score(reference_summary, generated_summary)
    
    # Combine all ROUGE scores into one final score
    final_score = {
        'rouge1': scores['rouge1'].fmeasure,
        'rouge2': scores['rouge2'].fmeasure,
        'rougeL': scores['rougeL'].fmeasure,
        'average': (scores['rouge1'].fmeasure + scores['rouge2'].fmeasure + scores['rougeL'].fmeasure) / 3
    }
    
    print("ROUGE Scores:", final_score)

    scorer = BERTScorer(model_type='bert-base-uncased')
    P, R, F1 = scorer.score([generated_summary], [reference_summary])
    print(f"BERTScore Precision: {P.mean():.4f}, Recall: {R.mean():.4f}, F1: {F1.mean():.4f}")
    return final_score

# def calculate_rouge(reference_summary, generated_summary):
#     # Initialize the ROUGE scorer with the desired metrics
#     scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL', 'rougeS', 'rougeW'], use_stemmer=True)
    
#     # Calculate ROUGE scores
#     scores = scorer.score(reference_summary, generated_summary)
    
#     # Combine all ROUGE scores into one final score
#     final_score = {
#         'rouge1': scores['rouge1'].fmeasure,
#         'rouge2': scores['rouge2'].fmeasure,
#         'rougeL': scores['rougeL'].fmeasure,
#         'rougeS': scores['rougeS'].fmeasure,
#         'rougeW': scores['rougeW'].fmeasure,
#         'average': (scores['rouge1'].fmeasure + scores['rouge2'].fmeasure + scores['rougeL'].fmeasure + scores['rougeS'].fmeasure + scores['rougeW'].fmeasure) / 5
#     }
    
#     # Print the final ROUGE scores
#     print("ROUGE Scores:", final_score)
    
#     return final_score

def summarize_short(text):
    print("\n~~\n IN SHORT SUMMARIZE \n~~\n")
    final_combine_prompt = """
    Please summarize the following document in English within 1000 words and at least 400 words, focusing on several key aspects. First, identify all regulatory changes introduced in the latest amendment along with their key features. Be sure to mention the dates of addition, amendment, or deletion, including the specific article number or name if mentioned. Highlight why these changes are important and how they are likely to impact any industry if discussed.
    Next, identify the objective and scope of introducing these changes and explain what transitional differences exist from previous versions. Provide details on classification updates, categories, and edition changes. Include all other important details while ensuring that your summary remains within 1000 words but not less than 400 words without omitting any critical information.
    Ensure you include all relevant numbers, statistics, references, classes, frequency ranges, categories, dates, and abbreviations used in the article within your summary itself. Provide brief explanations for each abbreviation upon its first occurrence. Mention all dates wherever specified and reference all articles/standards/regulations that are relevant to this document. If classifications are given in bullet points with details in the original document, list them accordingly but do not provide a separate list of these numbers or other details.
 
        document:'{text}'.
    """
    prompt = PromptTemplate.from_template(final_combine_prompt)
    chunks_2 = llm_text_splitter.create_documents(text)
    llm_chain = LLMChain(llm=llm, prompt=prompt)
    stuff_chain = StuffDocumentsChain(llm_chain=llm_chain, document_variable_name="text")
    short_summary = stuff_chain.run(chunks_2)
    calculate_rouge(text, short_summary)
    return short_summary, chunks_2

def summarize_long(text):
    print("\n~~\n IN LONG SUMMARIZE \n~~\n")
    if len(text) > 130000:
        text = text[:130000]

    chunks_prompt = '''
    Summarize the below chunk. Mention all the regulation numbers/names given in chunk, specify what specific changes have occurred, and specify any numbers mentioned (in frequency, quantity, range, limit, class etc.). Keep all provided acronyms as shown rather than simplifying. 
    Use the below pointers for better summary:
    - What are the key features and what is their added/ammended or deleted date if mentioned?
    - Why is the standard important and how likely it is going to effect the industry?
    - What is the objective and scope of introducing the current applied standards or how it is different (transition) from previous one?
    chunk: '{text}'
    '''
    
    final_combine_prompt = """
    Please summarize the following document in English within 1000 words and at least 400 words, focusing on several key aspects. First, identify all regulatory changes introduced in the latest amendment along with their key features. Be sure to mention the dates of addition, amendment, or deletion, including the specific article number or name if mentioned. Highlight why these changes are important and how they are likely to impact any industry if discussed.
    Next, identify the objective and scope of introducing these changes and explain what transitional differences exist from previous versions. Provide details on classification updates, categories, and edition changes. Include all other important details while ensuring that your summary remains within 1000 words but not less than 400 words without omitting any critical information.
    Ensure you include all relevant numbers, statistics, references, classes, frequency ranges, categories, dates, and abbreviations used in the article within your summary itself. Provide brief explanations for each abbreviation upon its first occurrence. Mention all dates wherever specified and reference all articles/standards/regulations that are relevant to this document. If classifications are given in bullet points with details in the original document, list them accordingly but do not provide a separate list of these numbers or other details.
 
        document:'{text}'.
    """
    map_prompt_template = PromptTemplate(input_variables=['text'], template=chunks_prompt)
    final_combine_prompt_template = PromptTemplate(input_variables=['text'], template=final_combine_prompt)

    # Load the summarization chain and generate the summary
    chunks = llm_text_splitter.create_documents([text])
    summary_chain = load_summarize_chain(
        llm=llm,
        chain_type='map_reduce',
        return_intermediate_steps=True,
        map_prompt=map_prompt_template,
        combine_prompt=final_combine_prompt_template,
    )
    output = summary_chain(chunks)

    # Extract the summary and output text
    report_text = output['output_text']
    print('report_text',report_text)
    calculate_rouge(text, report_text)
    chunks_2 = llm_text_splitter.create_documents(output['intermediate_steps'])
    return report_text, chunks_2



OPENAI_API_TYPE = "azure"

OPENAI_API_BASE = 'https://gen-ra-sec-research.openai.azure.com/'
OPENAI_API_VERSION = "2025-01-01-preview"

llm =AzureChatOpenAI(openai_api_version=OPENAI_API_VERSION,
                     openai_api_key=azure_api_key,
                    #  openai_api_key=OPENAI_API_KEY,
                     azure_endpoint=OPENAI_API_BASE,
                     openai_api_type=OPENAI_API_TYPE,
                    #  deployment_name = 'Azure-OpenAI-Common-Resource',
                     deployment_name='gpt-35-turbo',
                     model_name = 'gpt-35-turbo',
                     temperature=0)
 

llm_text_splitter=RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=40)

def summarize_article_llm(text):
    global report_text
    report_text = ''
    today =date.today()
    print("hellofromsummari")
    print("The length of the text is:", len(text))
    chunks = llm_text_splitter.create_documents([text])


    if len(chunks) == 1:
        report_text, chunks_2 = summarize_short(text)
    else:
        report_text, chunks_2 = summarize_long(text)
    # print('report_text',report_text)
    
    if len(text) > 8000:
        # chunks_2 = llm_text_splitter.create_documents(output['intermediate_steps'])
        pass

    else:
        chunks_2 = chunks


    combine_prompt_doc = '''
        Provide the following specific details from the document:
        "Name of Regulation:"(Extract the Title from the text. Pick any Values(Numbers) or any combination of words which specify the title/heading from the text. Just give the name as output )
        "Change:"(Extract all the changes of the Regulation. The Changes could be in terms of the product Regulation/marking changes,Bill revision, Updated definitions, application of regulations/standards or other. If more than one change exists then give it pointwise. Please extract all the possible changes which you identify from the text. Mention the regulation/article/standard number if mentioned or referred.)
        "Enforcement date:"(Extract the end date/ valid till/ completion date of the Regulation from the text,Specify "NA" if not mentioned)
        "Impact:"(Compare the category the text talks about with the following products- ["Microscopes","Optics","Cameras","Cell Culture Solutions,"NDT Solutions","Ultrasonic Flaw Detectors",
        "Phased Array Flaw Detectors","Eddy Current Flaw Detectors","Thickness Gauges","Automated Inspection Systems","Transducers and Probes","Scanners","X-Ray Fluorescence","Handheld",
        "Desktop","In-Line","Remote Visual Inspection","Videoscopes","Fiberscopes","Lightsources"].
        Give "High Impact" and if the regulation talks about affects equal or more than 90 percent of the above products,"Mild Impact" if 60 percent and else give "low Impact".give high/mid/low as output)
        "Start Date of the Regulation:" (Extract the Start Date/Publishing date/ Issue Date/ Enforcement date/ coming into force date of the Regulation,and if not found mention NA)
        "Relative Website links(add all the relatied websites from the text):"
        "Current Applied Standard:"
        "New/Update in the applied Standard:"extract the Latest applied standard name(do not ingore number of regulation if present)"
        "Valid Date:"(Extract for the Regulation valid/end date,such that till when the regualtioin is valid)
        "Recommendations:"(Give Overall Summary by providing any information that need to be paid attention to, along with recommendations for organizations which manufacture the following listed products: ["Microscopes","Optics","Cameras","Cell Culture Solutions,"NDT Solutions","Ultrasonic Flaw Detectors",
        "Phased Array Flaw Detectors","Eddy Current Flaw Detectors","Thickness Gauges","Automated Inspection Systems","Transducers and Probes","Scanners","X-Ray Fluorescence","Handheld","Desktop","In-Line","Remote Visual Inspection","Videoscopes","Fiberscopes","Lightsources"].)"
    '{text}'.
        '''

    prompt = PromptTemplate.from_template(combine_prompt_doc)

    llm_chain = LLMChain(llm=llm, prompt=prompt)
    stuff_chain = StuffDocumentsChain(llm_chain=llm_chain, document_variable_name="text")

    doc_text = stuff_chain.run(chunks_2)
    # print('doc_text',doc_text)
   
    # Create and return a DataFrame with the summary
    new_row = {"Text": text,  'llm_output': doc_text}
    df = pd.DataFrame([new_row])
    print(df)
   
    return df

# ------------------------------------------------------
# Vector Based LLM Search
#"Summary": (Give summary of given whole document in english, extract all the changes and other important details.By Extracting all the regualtion or (guideline or standards) numbers/name specify  has what specific changes has been there and please specify the numbers(in frequency,quantity,range, limits etc.) if any increase is there.) 

def setup_comparison_regex_llm():
    # print("azure_api_key",azure_api_key)
    prompt_template = """
    \n\n
    Compare against this existing data and mention any changes that have occurred relative to it. 
    If no changes have occurred or you are not sure, do not mention anything.
    Existing data:
    '{question}'
    Provide the following specific details from the document provided below in english:
        "Name of Regulation:"(Extract the specific Regulation/Law from the text.Pick any Values(Numbers) or any combination of words which specify the title/heading from the text.Just give the name as output )
        "Change:"(Extract all the changes of the Regulation.The Changes could be in terms of the product Regulation/marking changes,Bill revision,Updated definitions and other .If more than one change exist then give it pointwise.Please extract all the possible changes which you identify from the text)
        "Enforcement date:"(Extract the enforcement date of the Regulation from the text,Specify "NA" if not mentioned)
        "Impact:"(Compare the category the text talks about with["Microscopes","Optics","Cameras","Cell Culture Solutions,"NDT Solutions","Ultrasonic Flaw Detectors",
        "Phased Array Flaw Detectors","Eddy Current Flaw Detectors","Thickness Gauges","Automated Inspection Systems","Transducers and Probes","Scanners","X-Ray Fluorescence","Handheld",
        "Desktop","In-Line","Remote Visual Inspection","Videoscopes","Fiberscopes","Lightsources"].
        Give "High Impact" and if the regulation talks about affects equal or more than 90 percent of the above products,"Mild Impact" if 60 percent and else give "low Impact".give high/mid/low as output)
        "Start Date of the Regulation:" (Extract the Start Date/Publishing date of the Regulation,and if not found mention NA)
        "Relative Website links(add all the relatied websites from the text):"
        "Current Applied Standard:"
        "New/Update in the applied Standard:"extract the Latest applied standard name(do not ingore number of regulation if present)"
        "Valid Date:"(Extract for the Regulation valid date,such that till when the regualtioin is valid)
        "Recommendations:"(Give Overall Summary on recent regulatory compliance performance and provide recommendations for improvement for evident which manufactures the above listed products)"
    This is the document:
    '{context}'.
    """
    model = AzureChatOpenAI(
    azure_endpoint=OPENAI_API_BASE,
    openai_api_type="azure",
    openai_api_version="2025-01-01-preview",
    openai_api_key=azure_api_key,
    model_name="gpt-35-turbo",
    deployment_name="gpt-35-turbo",
    temperature=0)
    prompt = PromptTemplate(template = prompt_template, input_variables = ["context", "question"])
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt) # change QA chain, reduces complexity by loading summary
    return chain

def setup_comparison_report_llm():
    # print("azure_api_key_2",azure_api_key)
    prompt_template = """
    \n\n
       Please summarize the following document in English within 1000 words and at least 400 words, focusing on several key aspects. First, identify all regulatory changes introduced in the latest amendment along with their key features. Be sure to mention the dates of addition, amendment, or deletion, including the specific article number or name if mentioned. Highlight why these changes are important and how they are likely to impact any industry if discussed.
        Next, identify the objective and scope of introducing these changes and explain what transitional differences exist from previous versions. Provide details on classification updates, categories, and edition changes. Include all other important details while ensuring that your summary remains within 1000 words but not less than 400 words without omitting any critical information.
        Ensure you include all relevant numbers, statistics, references, classes, frequency ranges, categories, dates, and abbreviations used in the article within your summary itself. Provide brief explanations for each abbreviation upon its first occurrence. Mention all dates wherever specified and reference all articles/standards/regulations that are relevant to this document. If classifications are given in bullet points with details in the original document, list them accordingly but do not provide a separate list of these numbers or other details.)
        This is the document:
    '{context}'.
    """

    
    model = AzureChatOpenAI(
    azure_endpoint=OPENAI_API_BASE,
    openai_api_type="azure",
    openai_api_version="2025-01-01-preview",
    openai_api_key=azure_api_key,
    model_name="gpt-35-turbo",
    deployment_name="gpt-35-turbo",
    temperature=0)
    # prompt = PromptTemplate(template = prompt_template, input_variables = ["context", "rmf_text"])
    prompt = PromptTemplate(template = prompt_template, input_variables = ["context", "question"])

    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt) # change QA chain, reduces complexity by loading summary
    return chain

def vector_store_func(text):
    print("New Vector LLM")
    print(text)
    llm_text_splitter=RecursiveCharacterTextSplitter(chunk_size=5000, chunk_overlap=40)
    chunks = llm_text_splitter.split_text(text)
    # print(chunks)
    embeddings = AzureOpenAIEmbeddings(
    azure_endpoint=OPENAI_API_BASE,
    api_key=azure_api_key,
    azure_deployment="text-embedding-3-large",
    openai_api_version="2024-12-01-preview")

    # metadata = []
    # # print("Metadata")
    # for i in range(1, 3):
    #     metadata.append([{"source": "context document", "chunkid": i}])
    # metadata = [{"source": "context document", "chunkid": i} for i in range(1, 3)]
    # print("MetaData:",metadata)
    # vector_store = FAISS.from_texts(texts=chunks[0:2], embedding=embeddings, metadatas= metadata)
    # curr_chunk_lim = min(2, len(chunks))
    # vector_store = FAISS.from_texts(texts=chunks[1:curr_chunk_lim], embedding=embeddings, metadatas= metadata[0:curr_chunk_lim])
    # print("FAISS has no problem")

    print("First chunk processing:")
    ini_chunk = chunks[0] if len(chunks) == 1 else chunks[1]
    vector_store = FAISS.from_texts(ini_chunk, embedding=embeddings)
    print("First chunk processing complete.")
    for i in range(2, len(chunks), 2):
        end_index = min(i + 2, len(chunks))
        if i%2 == 0:
            print("New chunk group processing: ", i, end_index - 1)
        vector_store.add_texts(chunks[i:end_index], embedding=embeddings)
    vector_store.save_local("faiss_index")
    print("vector_store complete")
    return vector_store, chunks

def vector_compare_article_llm(vector_store, chunks, rmf_text):
    print("In vector_compare_article_llm")
    print("rmf_text")
    print(len(rmf_text))
    global report_text
    report_text = ''
    # prev_rir = fil
    # instead of keyword para use the previous rir row 
    if len(rmf_text) > 15000:
        rmf_text = rmf_text[:15000]

    user_question = """
        Regulation Change Enforcement date Impact
        Microscopes, Optics, Cameras, Cell Culture Solutions,
        NDT Solutions, Ultrasonic Flaw Detectors, 
        Phased Array Flaw Detectors, Eddy Current Flaw Detectors,
        Thickness Gauges, Automated Inspection Systems, 
        Transducers and Probes, Scanners, X-Ray Fluorescence, 
        Handheld, Desktop, In-Line, Remote Visual Inspection, 
        Videoscopes, Fiberscopes, Lightsources Start Date
        Current Applied Standard New/Update in the applied Standard
        Latest applied standard Valid Date Recommendations, 
        regulatory compliance performance, manufacturers
    """ + keywords_para + rmf_text

    embeddings = AzureOpenAIEmbeddings(
    azure_endpoint=OPENAI_API_BASE,
    api_key=azure_api_key,
    azure_deployment="text-embedding-3-large",
    openai_api_version="2024-12-01-preview")
    document_db = vector_store.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    docs = document_db.similarity_search(user_question, k=10)
    first_doc =  doc(page_content=chunks[0])
    docs.insert(0, first_doc) 
    # chain = get_conversational_chain()
    chain = setup_comparison_regex_llm()
    # response = chain({"context": docs, "rmf_text": user_question}, return_only_outputs=True)
    response = chain({"input_documents": docs, "question": rmf_text}, return_only_outputs=True)
    print(response["output_text"])
    report_chain = setup_comparison_report_llm()
    report_response = report_chain({"input_documents": docs, "question": rmf_text}, return_only_outputs=True)
    report_text = report_response["output_text"]
    print("SUMMARY ~~~~~~~~~~~~~~~~~~~~~~")
    print(report_text)
    print("SUMMARY END ~~~~~~~~~~~~~~~~~")
    return response["output_text"]

#--------------------------------------------------------------------------------------------------
#RIR extraction from output
#---------------------------------------------------------------------------------------------------


def extract_data_using_regex(llm_output):
    patterns = {
        # "Summary": r"Summary:\s*((?:.|\n)*?)(?=\n[A-Z][a-z]+:|$)",
        "Name of Law and regulations": r"Name of Regulation(?::\"|\":|\"|:)\s*(.*)",
        "Change": r"Change(?::\"|\":|\"|:)((.|\s)*?)(?:\"|)Enforcement", # FIX :"
        "Enforcement date": r"Enforcement date(?::\"|\":|\"|:)\s*(.*)",
        "Relative Websites": r"Relative Website links(?::\"|\":|\"|:)\s*(.*)",
        "Start Date": r"Start Date of the Regulation(?::\"|\":|\"|:)\s*(.*)", # FIX "
        "Current Applied Standard:":r"Current Applied Standard(?::\"|\":|\"|:)\s*(.*)",
        "Valid Date":r"Valid Date(?::\"|\":|\"|:)\s*(.*)", # FIX "
        "Impact":r"Impact(?::\"|\":|\"|:)((.|\s)*?)(?:\"|)Start",  # Adjusted pattern for multiline capture
        "New/Update in the applied Standard":r"Update in the applied Standard(?::\"|\":|\"|:)((.|\s)*?)(?:\"|)Valid",  # Adjusted pattern for multiline capture
        "Recommendations":r"Recommendations(?::\"|\":|\"|:)((.|\s)*)"  # FIX :"
    }
   
    extracted_data = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, llm_output)
        if match:
            extracted_data[key] = match.group(1).strip()
        else:
            extracted_data[key] = ""
    return extracted_data



#____________________________________________________________________________________________
#Open Seach functions

def google_cse(query, date):
 
    cse_date = ''
   
    if date:  
        cse_date = '&sort=date:r:' + parse(date).strftime("%Y%m%d") + ':'
 
    url = f"https://www.googleapis.com/customsearch/v1?key={google_api_key}&cx={search_engine_id}&q={query}&sort=date:d:s{cse_date}"
    result = requests.get(url)
    if result.status_code==200:
        json_data=simplejson.loads(result.content)
        return json_data
    else:
        print(f"Error:Google CSE API request failed with status {result.status_code}")
        return None
    
def json_parse(df, json, query, model, site_db):
    legal_db = site_db.loc[site_db['Approved by Legal'] == 'Yes']
    not_legal_db = site_db.loc[site_db['Approved by Legal'] == 'No']
    for search_result in json['items']:
        curr_title = search_result['title']
        curr_url = search_result['link']
        try:
            curr_date = parse(search_result['snippet'][:13], fuzzy=True).strftime("%Y-%m-%d")
        except:
            curr_date = ''
        curr_excerpt = search_result['snippet']
        query_embedding = model.encode(query)
        title_embedding = model.encode(curr_title)
        excerpt_embedding = model.encode(curr_excerpt)
        total_similarity = util.pytorch_cos_sim(query_embedding, title_embedding) + util.pytorch_cos_sim(query_embedding, excerpt_embedding)
        if len(legal_db[legal_db['URL'].str.contains(urlparse(curr_url).netloc)]) > 0:
            curr_scrapable = 'Yes'
        elif len(not_legal_db[not_legal_db['URL'].str.contains(urlparse(curr_url).netloc)]) > 0:
            curr_scrapable = 'No'
        else:
            curr_scrapable = 'No Info'

        # curr_llm_summary = client.chat.completions.create(
        # model="SL_Openai_Resource_deployment",
        # temperature=0.2,
        # messages=[{"role":"system", "content":" You are a helpful intelligent assistant"},
        #         {"role":"user", "content":f"Summarize this text in english:\n\n{curr_excerpt}. The source of this excerpt is: {curr_url}. Do not provide any links."}]
        # )
        # new_row = {"Article Title": curr_title, "URL": curr_url, "Date": curr_date, "Excerpt": curr_excerpt, "LLM Summary": curr_llm_summary.choices[0].message.content}
        new_row = {"Relevancy": float(total_similarity), "Article Title": curr_title, "URL": curr_url, "Date": curr_date, "Excerpt": curr_excerpt, "Scrapable": curr_scrapable}
        s1 = pd.Series(new_row)
        df = pd.concat([df,s1.to_frame().T], ignore_index=True)
    return df

#_____________________________________________________________________________________________________
#General Functions

#Read the pdf content
def content_pdf(file_path):
    with open(file_path, "rb") as file:
        pdf = PdfReader(file)
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text

def read_pdf(file_path):
    pdf_text=[]
    with fitz.open(file_path) as pdf :
        for page in pdf:
            pdf_text.append(page.get_text())
    print(pdf_text)
    return "\n".join(pdf_text)

def read_docx(file_path):
    doc= docx.Document(file_path)
    return "\n".join([paragraph.text for paragraph in doc.paragraphs])

def process_user_input(text,files):
    print("in process_user_input")
    file_content = " "
    if files :
        print("The file is uploaded")
        for file in files:
            file_extension = os.path.splitext(file.filename)[1].lower()
            print(file.filename, "has been read")
            temp_path = f"temp{file_extension}"
            file.save(temp_path)

            try:
                if file_extension == '.pdf':
                    file_content += read_pdf(temp_path)
                    # print('the file content has been read:',file_content)
                elif file_extension == '.docx':
                    file_content += read_docx(temp_path)
                else:
                    return "Unsupported file type. Please upload either pdf or docx",400
            
            finally:
                os.remove(temp_path)
    
    final_output = (file_content + "\n" + text)
    return final_output, 200



#For combining the results
def accumulate_results(results_list):
    df_list = [pd.DataFrame(data) for data in results_list]
    combined_df = pd.concat(df_list, ignore_index=True)
    return combined_df

def merge_multiple_lists(*lists):
    """
    Merges multiple lists of dictionaries based on a specified key.
    
    :param key: Key to merge the dictionaries on.
    :param lists: A variable number of list arguments containing dictionaries.
    :return: A merged list of dictionaries where each dictionary is unique by the specified key.
    """

    merged_dict = {}
    
    def add_to_merged_dict(lst):
        key = 'title'
        for item in lst:
            if not isinstance(item, dict) or key not in item:
                raise ValueError("All items must be dictionaries containing the specified key")
            if item[key] in merged_dict:
                # If base_url exists, update existing entry
                merged_dict[item[key]].update(item)
            else:
                # If base_url does not exist, create new entry
                merged_dict[item[key]] = item

    for lst in lists:
        add_to_merged_dict(lst)
    return list(merged_dict.values())

#------------------------------------------------------------------------------------------------------
# RIR Generation
#------------------------------------------------------------------------------------------------------

def get_best_match(extracted_name, df, threshold=75):
    # Clean the extracted name
    cleaned_extracted_name = clean_string(extracted_name)
    print("cleaned_extracted_name", cleaned_extracted_name)
    # Extract the best match using fuzzy matching
    best_match = process.extractOne(cleaned_extracted_name, df['cleaned_ra_interpretation'], scorer=fuzz.token_sort_ratio)

    if best_match[1] >= threshold:
        print("Best Matched Regulation Score", best_match[1])
        # Get the original value and corresponding sheet_name
        original_value = df.loc[df['cleaned_ra_interpretation'] == best_match[0], 'Col9_RA_interpretation_English'].values[0]
        sheet_name = df.loc[df['cleaned_ra_interpretation'] == best_match[0], 'Col2_Region_Country_Category'].values[0]

        return original_value, sheet_name
    else:
        return None, None



def get_df_by_region(req_data):

    global filtered_values
    country = req_data.get('country')
    region = req_data.get('region')
    key = get_key(region, country)
    print('The key used for the provided region and country is',key)
    filtered_values = filter_dataframe_by_key(data, key)
    return filtered_values


                      

def check_matched_regulation(req_data,article_title):
    global filtered_values
    country = req_data.get('country')
    region = req_data.get('region')
    filtered_values = get_df_by_region(req_data)
    filtered_data = filtered_values[filtered_values['Col4_Title 2'].isin(['Law/regulation name (in local language)','Law/regulation name (in English & Japanese)',	'Common name (in local language)',	'Common name (in English & Japanese)',	'Law/regulation no.',	'Standard name (in local language)',	'Standard name (in English & Japanese)','Standard name (in local language)',	'Standard name (in English & Japanese)', 'External link to regulation'
    ])]

    filtered_data['Col9_RA_interpretation_English']= filtered_data['Col9_RA_interpretation_English'].str.replace('\n', ' ').str.replace('\u3000', ' ').str.replace('\t', ' ')
    filtered_data = filtered_data[filtered_data['Col9_RA_interpretation_English'] != '0'].drop_duplicates()
    # filtered_data['cleaned_ra_interpretation'] = [clean_string(choice) for choice in filtered_data['Col9_RA_interpretation_English']]
    print("The regulation list is ready",filtered_data['cleaned_ra_interpretation'])  
    
    matched_regulation, sheet_name = get_best_match(article_title, filtered_data)

    if matched_regulation:
        print(f"Matched Regulation: {matched_regulation}")
        print("sheet_name",sheet_name)
        # filtered_values = get_df_by_region(req_data)
        print("filtered_values",filtered_values)
        var_change=matched_regulation
        
    else:
        print("No close match found.")
        var_change="None"
        sheet_name = f"{region}_{country}"  
    
    return var_change, sheet_name

def rir_generate(req_data,df_summary_content,url_given,sheet_name,article_title=None, var_change=None, publish_date=None):
    global reports_folder
    global report_text

    print("df_summary_content_rir",df_summary_content)
    extracted_data = extract_data_using_regex(df_summary_content)
    country = req_data.get('country')
    region = req_data.get('region')
    print('extracted_data',extracted_data)

    # selected_region = "World Wide"

    if country =="Japan (JPN)":
        varRegional_Global="Global"
    else:
        varRegional_Global="Regional"  

        

    print("llm output")
    url_given = str(url_given[0])

    law_and_regulations = extracted_data.get("Name of Law and regulations")
   
    Start_Date=str(extracted_data.get("Start Date"))
    if Start_Date == "NA":
        Start_Date = publish_date if publish_date != None else "NA"

    End_Date= str(extracted_data.get("Enforcement date"))
    Date_of_Report=str(date.today())
    Project_Covered="Genpact India RA/QA"
    Department="Genpact India RA/QA"
    name_title = article_title if article_title != "" else law_and_regulations
    Name_And_Title = f"{sheet_name}_{name_title}"
    Department_Company="Genpact India RA/QA"
    Report_Prepeared_Date=str(date.today())
    # Excecutive= str(extracted_data.get("Summary"))
    Excecutive= report_text + f'\n\n URL for the site:{url_given}'
    if var_change:
        Current_Applied_Standard=var_change 
    else:
        var_change, sheet_name= check_matched_regulation(req_data,article_title)
    Valid_date=extracted_data.get("Valid Date")
    # Change_Regulation=extracted_data.get("Change")
    Change_Regulation= extracted_data.get("Change")
    Compliance_Status = "NA"
    New_Update= article_title if article_title else extracted_data.get("New/Update in the applied Standard")
    Date_Transition_Period="NA"
    # Impact=extracted_data.get("Impact")
    Impact= "NA"
    Action_req=f"Please verify whether {law_and_regulations} is compliant with evident products or not"
    summary_and_recommendations = "NA"
    Global=varRegional_Global
    Comments="NA"
    Implementaion_neccesary="NA"
    Overall_Impact_Assessment = ""
    Summary_and_Recommendations=f"Evident product shall adhere to the standard {name_title}"

    print(reports_folder)
    # Define template for RIR report
    template = os.path.join(reports_folder, "template.docx")
    document = MailMerge(template)
    field_names = document.get_merge_fields()
    # print("Template field_names", field_names)


    document.merge(Start_Date=Start_Date,End_Date=End_Date, Date_of_Report=Date_of_Report, 
                Project_Covered=Project_Covered,Department=Department, 
                Name_And_Title=Name_And_Title,Department_Company=Department_Company,
                Report_Prepeared_Date=Report_Prepeared_Date,Excecutive=Excecutive, 
                Current_Applied_Standard=Current_Applied_Standard,Valid_date=Valid_date,
                Date_Transition_Period=Date_Transition_Period,Change_Regulation=Change_Regulation,
                Compliance_Status=Compliance_Status,New_Update=New_Update,
                Impact=Impact,Action_req=Action_req,Global=Global,Comments=Comments,Implementaion_neccesary=Implementaion_neccesary,
                Overall_Impact_Assessment=Overall_Impact_Assessment ,Summary_and_Recommendations=Summary_and_Recommendations
                )
    print("document merge")
    
    output_path = os.path.join(tempfile.gettempdir(),"RIR_EVIDENT.docx")
    print(output_path)
    document.write(output_path)
    print(f"RIR_EVIDENT.docx","the file is saved")

    executive_dict = {
        "Executive Summary": Excecutive
    }
    print("executive_dict",executive_dict)

    department = {
        "Project Covered" : Department
    }

    time_period_report = {
        "Start Date": Start_Date,
        "End Date": End_Date,
        "Date of Report": Date_of_Report }
    print(time_period_report)

    report_by = {
        "Name & Title": Name_And_Title,
        "Department/ Company": Department_Company,
        "Date": Report_Prepeared_Date }
    print("report_by",report_by)
            
    summary_changes = {
        "Current applied standard": Current_Applied_Standard,
        "New/Update of applied standard": New_Update,
        "Valid Date": Valid_date, 
        "Date Transition Period": Date_Transition_Period,
        "Change / Gap Description": Change_Regulation,
        "Compliance Status Impact / Risk? (High/Low/None)":Impact }
    print("summary_changes",summary_changes)

    analysis_and_action = {
        "Compliance Status" : Compliance_Status,
        "Global / Regional" : Global,
        "Requirement/Action to be compliant" : Action_req,
        "Comments/Remarks " : Comments,
        "Implementation necessary until? " : Implementaion_neccesary
    }
    print("analysis_and_action",analysis_and_action)

    overall_impact_assesment = {
        "Overall Impact Assessment" : Overall_Impact_Assessment,
    }
    print("overall_impact_assesment",overall_impact_assesment)

    summary_and_recommendations = {
        "Summary and Recommendations" : Summary_and_Recommendations
    }
    print("summary_and_recommendations",summary_and_recommendations)

    
    print("dict made")
    df_executive_summary = pd.DataFrame([executive_dict])
    df_department = pd.DataFrame([department])
    df_time_period_report = pd.DataFrame([time_period_report])
    df_report_by = pd.DataFrame([report_by])
    df_summary_changes = pd.DataFrame([summary_changes])   
    print(df_summary_changes)     
    df_analysis_and_action = pd.DataFrame([analysis_and_action])
    df_overall_impact_assesment = pd.DataFrame([overall_impact_assesment])
    df_summary_and_recommendations = pd.DataFrame([summary_and_recommendations])
    print(df_summary_and_recommendations)

    # df_executive_summary = pd.DataFrame(list(executive_dict.items()), columns=['Key', 'Value'])
    # print(df_executive_summary)
    # df_department = pd.DataFrame(list(department.itmes()), columns=['Key', 'Value'])
    # df_time_period_report = pd.DataFrame(list(time_period_report.items()), columns=['Key', 'Value'])
    # df_report_by = pd.DataFrame(list(report_by.items()), columns=['Key', 'Value'])
    # df_summary_changes = pd.DataFrame(list(summary_changes.items()), columns=['Key', 'Value'])        
    # df_analysis_and_action = pd.DataFrame(list(analysis_and_action.items()), columns=['Key', 'Value'])
    # df_overall_impact_assesment = pd.DataFrame(list(overall_impact_assesment.items()), columns=['Key', 'Value'])
    # df_summary_and_recommendations = pd.DataFrame(list(summary_and_recommendations.items()), columns = ['Key', 'Value'])

    executive_json = df_executive_summary.to_json(orient='records')
    time_period_report_json = df_time_period_report.to_json(orient='records')
    department_json = df_department.to_json(orient='records')
    report_by_json = df_report_by.to_json(orient='records')
    summary_changes_json = df_summary_changes.to_json(orient='records')
    analysis_and_action_json = df_analysis_and_action.to_json(orient='records')
    overall_impact_assesment_json = df_overall_impact_assesment.to_json(orient='records')
    summary_and_recommendations_json = df_summary_and_recommendations.to_json(orient='records')
    print("Json Converted")
    # print(executive_json, department_json, time_period_report_json, report_by_json, summary_changes_json, analysis_and_action_json, overall_impact_assesment_json, summary_and_recommendations_json)
    if time_period_report_json:            
        # return jsonify(executive_json,time_period_report_json,report_by_json,summary_changes_json), 200
        return executive_json, time_period_report_json,department_json, report_by_json, summary_changes_json, analysis_and_action_json, overall_impact_assesment_json, summary_and_recommendations_json
    else:
        return {'error': 'Result Not Available'}

#--------------------------------------------------------------------------------------
#WEB EXTRACTION COUNTRY/REGION CODES

#------------------------------------------------------------------------------------------

keywords = keywords_list

keywords_para = (" ").join(keywords_list)
#------------------------------------------------------------------------------------------
#__________________________________________________________________________________________
# MAIN APP
#__________________________________________________________________________________________

Website_Extraction = {
    "https://news.gov.bc.ca" : bc_laws,
    "http://www.shanghai.gov.cn" : Shangai,  
    "https://www.elegislation.gov.hk":elegislation,
    "https://ec.europa.eu" : ec,
    "https://eur-lex.europa.eu" : eux,
    "https://health.ec.europa.eu" : health_ec,
    "https://www.japaneselawtranslation.go.jp" : japlaw,
    "https://www.law.go.kr" : korea,
    "https://www.hsa.gov.sg" : hsa,
    "https://sso.agc.gov.sg" : sso,
    "https://www.ecfr.gov" : ecfr,
    "http://www.health.qld.gov.au" : health_au,
    "https://laws.e-gov.go.jp" : e_gov,
    "https://www.emsd.gov.hk" : emsd,
    "https://www.jaish.gr.jp" : jaish,
    "https://www.mhlw.go.jp" : mhlw,
    "https://www.accessdata.fda.gov" : fda_access,
    "https://www.fda.gov":fda,
    "https://legislation.nsw.gov.au" : nsw_au,
    "https://www.govinfo.gov": govinfo,
}


# Get the BUILD folder
current_directory = os.path.dirname(os.path.abspath(__file__))
static_folder_path = os.path.join(current_directory, 'build')
 
app = Flask(__name__, static_folder=static_folder_path)
# app = Flask(__name__)
CORS(app)
 
@app.route("/", defaults={'path': ''})
@app.route('/<path:path>')
 
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

# def open_browser():
#     # webbrowser.open_new("http://127.0.0.1:5000")
#     webbrowser.open_new("https://evident-regscope-ai-g7a3h0ana5ehh5cq.eastus2-01.azurewebsites.net/")

# open_browser()
#___________________________________________________________________________________________________
# Flask Cache 
#___________________________________________________________________________________________________

app.config['CACHE_TYPE'] = 'simple'  
cache = Cache(app)
 
def generate_data(conditions):
    req_data = conditions
    print("Received Data:", req_data)
    
    url_df = req_data['selectedData']
    selected_url = [entry['url'] for entry in url_df]
    
    date_str = str(req_data['date'])
    print("date", date_str)
    
    selected_date = pd.to_datetime(date_str).tz_localize(None)
    print("selected_date", selected_date)
    
    today = datetime.today()
    print(today)
    
    days = (today - selected_date).days
    print(days)
    
    table_results = pd.DataFrame()
    
    for url in selected_url:
        print(url)
        if url in Website_Extraction:
            print(Website_Extraction[url])
            table = Website_Extraction[url]
            print(table)
            
            if isinstance(table, list):
                result = [func(days) for func in table]
                table_results = pd.concat([table_results, result], ignore_index=True)
            else:
                table_result = table(days)
                table_results = pd.concat([table_results, table_result], ignore_index=True)

        else:
            print(f"{url} not found in dictionary")
    
    print("table_result")
    return table_results
 
 
def hash_conditions(conditions):
    condition_str = json.dumps(conditions, sort_keys=True)
    return hashlib.md5(condition_str.encode('utf-8')).hexdigest()
 
#___________________________________________________________________________________________________
# Flask Routing
#___________________________________________________________________________________________________


@app.route('/api/view-results', methods=['POST'])
def view_results():
    global cached_data
    print("Keywords in use", keywords)
    try:
        conditions = request.get_json()
        print(f"conditions:{conditions} ")
       
        cache_key = hash_conditions(conditions)
        print(cache_key)
        cached_data = cache.get(cache_key)
        print(f"cached data:{cached_data}")
        if cached_data is not None:
            print("Returning cached data.")
            table_result = cached_data
           
        else:
            print("Generating new data.")
            table_result = generate_data(conditions)
            cache.set(cache_key, table_result, timeout=720000)
           
 
        print(table_result, table_result.info())
        json_result = table_result.to_json(orient='records')
        if json_result:            
            # result=json.loads(json_result)
            return jsonify(json_result), 200
        else:
            return jsonify({'error': 'Result Not Available'}),405
 
       
    except Exception as e:
        return jsonify({"error": f"Error starting process: {e}"}),500



@app.route('/api/view-details', methods=['POST'])
def view_details():
    #country-title add in the RIR report
    try:
            req_data = request.get_json()
        # cache_key_1 = hash_conditions(req_data)  
        # cached_data_1 = cache.get(cache_key_1)
        # if cached_data_1 is not None:
        #     print("Returning cached data.")
        #     return jsonify(cached_data_1), 200
        # else:
            selected = req_data['selected']
            print("req_data:",req_data)
            # print("Country:",req_data.get('country'))
            data = pd.DataFrame(selected)
            url_given = data['URL']
            article_title= data['Article Title']
            article_title = article_title[0]
            print(data.columns)
            print(article_title)

            var_change,sheet_name = check_matched_regulation(req_data,article_title)

            if var_change == "None" :
                print(var_change)
                for index, row in data.iterrows():
                    df_summary_content = summarize_article_llm(row["Summary"])
                    print("df_summary_content",df_summary_content)
                    llm_output = df_summary_content['llm_output'][0]
            else:
                rmf_data=filter_main_sheet(sheet_name)
                for index, row in data.iterrows():
                    new_vector_store, chunks = vector_store_func(row["Summary"])
                    llm_output = vector_compare_article_llm(new_vector_store, chunks, rmf_data)

            
            executive_json, time_period_report_json,department_json, report_by_json, summary_changes_json, analysis_and_action_json, overall_impact_assesment_json, summary_and_recommendations_json = rir_generate(req_data,llm_output,url_given,sheet_name,article_title,var_change)
            # response_data = {
            #             "executive_summary": executive_json,
            #             "time_period_report": time_period_report_json,
            #             "department": department_json,
            #             "report_by": report_by_json,
            #             "summary_changes": summary_changes_json,
            #             "analysis_and_action": analysis_and_action_json,
            #             "overall_impact_assessment": overall_impact_assesment_json,
            #             "summary_and_recommendations": summary_and_recommendations_json
            #         }
            # cache.set(cache_key_1, response_data, timeout=3600)  
            if executive_json:
                return jsonify(executive_json, time_period_report_json,department_json, report_by_json, summary_changes_json, analysis_and_action_json, overall_impact_assesment_json, summary_and_recommendations_json), 200
            else:
                return jsonify({'error': 'Result Not Available'}),405
    except Exception as e:
        return jsonify({"error": f"Error starting process: {e}"}),500

        
@app.route('/api/open-search',methods=["POST"])
def search():
    try:
        model=SentenceTransformer('distilbert-base-nli-mean-tokens')
    except Exception as e:
        model=None
        print(f"error loading model: {e}")
        return jsonify({"error":"Model not loaded"}),500
       
    req_data = request.get_json()
    query=req_data['searchQuery']
    print(query)
    date = req_data.get('date')
    if date:
        date = pd.to_datetime(date).tz_localize(None)
        date = str(date)
        print(date)
    # date=date.get("date")
    if not query:
        return jsonify({"error":"Query parameter is required"}),405
    df=pd.DataFrame(columns=["Relevancy","Article Title","URL","Date","Excerpt","Scrapable"])
    output_json=google_cse(query,date)
    df=json_parse(df,output_json,query,model,url_db)
    df=df.sort_values('Relevancy',ascending=False)
    # articles=df.to_dict(orient="records")
    print(df)
    json_result = df.to_json(orient='records')

    if json_result:            
        return jsonify(json_result), 200
    else:
        return jsonify({'error': 'Result Not Available'}),405


# def email_send(document_save):
#     print("Document:",document_save)
#     Outlook = win32com.client.Dispatch("Outlook.Application",pythoncom.CoInitialize())
#     for account in Outlook.Session.Accounts: 
#         if account.DisplayName == "Bhavya.Walecha@genpact.com":   # Sender mail id 
#             mail = Outlook.CreateItem(0)
#             mail._oleobj_.Invoke(*(64209, 0, 8, 0, account))
#             mail.To = 'pawan.rastogi1@genpact.com'  
#             # Receiver mail id
#             # mail.To = recipient_email # Receiver mail id
#             mail.Subject = 'Test'
#             print("Subject",mail.Subject)

#             body = """
# Dear admin,

# We hope this email finds you well. Please find the attachment.
#             """

#             body += """

# Thank you.

# Regards,
#     Genpact Team
#             """

#             mail.Body = body
            
#             mail.Attachments.Add(Source=str(document_save))
#             mail.Send()
#             print("The mail has been sent!")



@app.route("/api/download", methods=["GET"])
def download():
    dir = os.path.abspath(tempfile.gettempdir())
   
    if not dir.exists():
        return abort(404, description="Directory does not exist")
    
    file_path = "RIR_EVIDENT.docx"
    
    if not (dir / file_path).exists():
        return abort(404, description="File does not exist")
    
    document_save = os.path.join(dir,file_path)
    # email_send(document_save)
    
    return send_from_directory(directory=dir, path=file_path, as_attachment=True)



@app.route('/api/manual-submit', methods=['POST'])
def manual_submit():
    try:
        url_given = []
        print("Received Data:", request.form)
        req_data = request.form
        region = request.form.get('region')
        country = request.form.get('country')
        text = request.form.get('text')
        url = request.form.get('url')
        article_title = request.form.get('Article Title')
        url_given.append(url)
        user_text = str(text)
        article_title =str(article_title)

        print("Received url_given:", url_given)
        print("Received article_title:", article_title)


        files = request.files.getlist('file')
        print(files)


        user_input, status=process_user_input(user_text,files)
        
        if user_input == "Unsupported file type. Please upload either pdf or docx":
            return jsonify(user_input), status
            
        # user_input = user_text
        print("The file content:",user_input)

        text = user_input 
        # print("The text has been read")

        var_change, sheet_name = check_matched_regulation(req_data,article_title)
        print("var_change",var_change)

        if var_change == "None" :
            print("The ")
            df_summary_content = summarize_article_llm(text)
            llm_output = df_summary_content['llm_output'][0]

        else:
            print("sheet_name",sheet_name)
            rmf_data=filter_main_sheet(sheet_name)
            print('rmf_data', rmf_data)
            
            new_vector_store, chunks = vector_store_func(text)
            llm_output = vector_compare_article_llm(new_vector_store, chunks, rmf_data)
        
        # print("llm_output",llm_output)
        
        executive_json, time_period_report_json,department_json, report_by_json, summary_changes_json, analysis_and_action_json, overall_impact_assesment_json, summary_and_recommendations_json = rir_generate(req_data,llm_output,url_given,sheet_name,article_title,var_change)

        if executive_json:
            return jsonify(executive_json, time_period_report_json,department_json, report_by_json, summary_changes_json, analysis_and_action_json, overall_impact_assesment_json, summary_and_recommendations_json), 200
        else:
            return jsonify({'error': 'Result Not Available'}),405


        # print("Received Data:", country, region, text, url)

    except Exception as e:
        return jsonify({"error": f"Error starting process: {e}"}),500

def update_keywords_file(keywords):
    with open('website_extraction/keywords.py', 'w', encoding='utf-8') as f:
        f.write("keywords_list = " + str(keywords))

@app.route('/api/keywords', methods=['GET'])
def get_keywords():
    return jsonify({"keywords": keywords})

@app.route('/api/keywords', methods=['POST'])
def add_keywords():
    data = request.json
    new_keyword = data.get("keyword")
    if new_keyword and new_keyword not in keywords:
        keywords.append(new_keyword)
        update_keywords_file(keywords)
        return jsonify({"message": "Keyword(s) has been added", "keywords": keywords}), 201

    return jsonify({"message": "Keyword(s) already existed or invalid input"}), 400

@app.route('/api/keywords/<keyword>', methods=['DELETE'])
def delete_keyword(keyword):
    if keyword in keywords:
        keywords.remove(keyword)
        update_keywords_file(keywords)
        return jsonify({"message": "Keyword has been removed from list", "keywords": keywords}), 200
    return jsonify({"message": "Keyword not found!"}), 404

if __name__== '__main__':
    port= int(os.environ.get("PORT",5000))
    app.run(host='0.0.0.0',port=port)
