import json
import re
import time
import os
from .config import openai
# from config import openai
from fastapi.middleware.cors import CORSMiddleware
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from starlette.middleware.errors import ServerErrorMiddleware
from starlette.requests import Request
from starlette.types import ASGIApp
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from .auth.auth_handler import get_user_upn_from_token_header
from .auth.auth_handler import get_user_membership_information_from_auth_header
from .auth.auth_handler import get_user_membership_information_from_id_token_header
from .database import save_completion_response, save_chat_rating ,read_chat_history
from .auth.docs import get_search_client
from .intent import get_user_intent
from .product_recommendation import get_product_recommendation
import requests
from nltk.tokenize import sent_tokenize
from .lead_generation_evaluation import summarise_chat_queries
from .bot_config import get_history_prompt, get_completion ,get_recommendation_prompt ,get_price_prompt ,get_main_prompt, get_static_response_map,get_contact_info,total_max_tokens,max_tokens,model_name
from .utilities import trim_history_and_index_combined
from azure.search.documents.models import QueryType

import logging
import random

from dotenv import load_dotenv
from itertools import count


async def global_execution_handler(request: Request, exc: Exception) -> ASGIApp:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content="Unknown Error",
    )

app = FastAPI()

app.add_middleware(
    ServerErrorMiddleware,
    handler=global_execution_handler,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


@app.post("/v1/chat/ratings")
async def post_ratings_data(data: dict, request: Request):
    """ Posts the chat rating value to the Azure Sql"""
    chatId = data["chatId"]
    chatRating = data["chatRating"]
    #messages = data["messages"]
    dialog_id = data["dialogId"]
    result = save_chat_rating(
        chatId,
        dialog_id,
        chatRating
        )

    return result


def completion_stream(chatId, messages, chat_completion):
    message = {'role': '', 'content': ''}
    for chunk in chat_completion:
        delta = chunk['choices'][0]['delta']
        if 'role' in delta:
            message['role'] = delta['role']
        elif 'content' in delta:
            message['content'] += delta['content']

        string = json.dumps(chunk, separators=(',', ':'))
        string = ''.join(('data: ', string, '\n\n'))
        yield string

    yield 'data: [DONE]'

    messages.append(message)
    save_completion_response(chatId, messages)


def search_index(query: str, top: int = 10, filter: str = "",query_language="en"):
    # load authenticated client
    search_client = get_search_client(language=query_language)
    # get results using query text,
    search_results = search_client.search(
        search_text=query, 
        top=top, 
        filter=filter,
        query_type=QueryType.SEMANTIC,
        query_language=query_language,semantic_configuration_name="default",)
    # print full metadata and search
    search_results = list(search_results)
    logging.debug(
        f"COGNITIVE SERVICE INDEX RESPONSES ON INDEX {os.getenv('AZURE_SEARCH_INDEX')}:")
    logging.debug([result['id'] for result in search_results])
    # collate content into single string
    # document_content = {result['id']:result['content'] for result in search_results}
    # content = " ".join([result['content'] for result in search_results])
    return search_results

# Define a route to handle POST requests

def url_ok(url):
    try :
        r = requests.head(url)
        return r.status_code == 200
    except:
        return False

def update_href_tag(text):
    text = re.sub(r'<a[^>]*>([^<]*)</a>', r'\1', text)

   # Regular expression to match URLs outside of <a> tags
    url_pattern = r'https?://\S+'

    # Regular expression to match <a> tags
    a_tag_pattern = r'<a\s+[^>]*>.*?</a>'

    # Function to add <a> tags around URLs that are not part of an <a> tag
    def add_a_tag(match):
        url = match.group(0)
        if url.endswith(".") or url.endswith(")"):
            url = url[:-1]
        # Check if the URL is already part of an <a> tag

        if ((not re.search(a_tag_pattern, url) ) and url_ok(url=url)):
            return f'<a href="{url}">learn_more_link</a>'
        else:
            return "remove_sentence"

    sentences = sent_tokenize(text)

    sentences_without_urls = [
        re.sub(url_pattern, add_a_tag, sentence)
        for sentence in sentences

    ]

    final_sentence = [sentence for sentence in sentences_without_urls if not "remove_sentence" in sentence]

    recreated_paragraph = ' '.join(final_sentence)
    button_number_count = 1
    counter = count(button_number_count)
    recreated_paragraph = re.sub(r'learn_more_link', lambda x: "link" + str(next(counter)), recreated_paragraph )
    print("Modified Text:")
    print(recreated_paragraph)

    return recreated_paragraph

def is_query_about_balcklist_word(query):
    blacklist_words=['klein', 'transmille' , 'keysight', 'starrett', 'megger']

    res = any(ele in query.lower() for ele in blacklist_words)

    return res, "blacklist_word"

def static_chat_completion_response(chat_id, model, intent, intent_content):

    logging.debug("Inside static_chat_completion_response for intent :"+intent)

    chat_completion= {
            "choices": [
                {
                "content_filter_results": {
                    "hate": {
                    "filtered": False,
                    "severity": "safe"
                    },
                    "self_harm": {
                    "filtered": False,
                    "severity": "safe"
                    },
                    "sexual": {
                    "filtered": False,
                    "severity": "safe"
                    },
                    "violence": {
                    "filtered": False,
                    "severity": "safe"
                    }
                },
                "finish_reason": "stop",
                "index": 0,
                "message": {
                    "content": intent_content,      
                    "role": "assistant"
                }
                }
            ],
            "created": 1694151829,
            "id": chat_id,
            "model": model,
            "object": "chat.completion",
            "prompt_annotations": [
                {
                "content_filter_results": {
                    "hate": {
                    "filtered": False,
                    "severity": "safe"
                    },
                    "self_harm": {
                    "filtered": False,
                    "severity": "safe"
                    },
                    "sexual": {
                    "filtered": False,
                    "severity": "safe"
                    },
                    "violence": {
                    "filtered": False,
                    "severity": "safe"
                    }
                },
                "prompt_index": 0
                }
            ],
            "usage": {
                "completion_tokens": None,  #Hard coded , care to be taken in case it is getting used.
                "prompt_tokens": None,  #Hard coded , care to be taken in case it is getting used.
                "total_tokens": None   #Hard coded , care to be taken in case it is getting used.
            }
            }
    return chat_completion

def get_source_content_from_cog_search(results):
    source_content = []
    for result in results:
        # check to see if url is present
        #print("sourcepage:",result['sourcepage'], "sourcefile:",result['sourcefile'])
        url = ""
        if ("sourcefile" in result.keys()):
            if (result["sourcefile"] is not None) and (result["sourcefile"] != ""):
                url = result["sourcefile"]
        # create template
        template = f"URL: {url} CONTENT: {result['content']} "
        if "www.fluke.com_en_" not in url and "www.fluke.com/en/" not in url:
            source_content.append(template)
    return source_content

def get_filter_string(instructions:str, messages:list, data:dict):
    request_country = data["siteInfo"].get("country", "Unknown")
    language = data["siteInfo"].get("language", "Unknown")
    country_list = [request_country, 'global']
    filterString = ""
    print("Request Country:",request_country)
    print("Request Language:",language)
    # Create 2 filter strings, if we don't get proper answer from the user country and language combo , then fetch default language documents
    if request_country == "Unknown" and  language == "Unknown":
        filterString = "not group_ids/any()"
    elif request_country == "Unknown":
        filterString = "languagecode eq '{}'".format(
                        language.replace("'", "''"))
    elif language == "Unknown":
        filterString = "countrycode eq '{}'".format(
                        request_country.replace("'", "''"))
    else:

        country_list_str = ','.join(country_list)
        filterString = f"(search.in(countrycode, '{country_list_str}', ','))"

        filterString += " and (languagecode eq '{}')".format(
                        language.replace("'", "''"))
    return filterString

# This method is used to query cognitive search and return the results
def get_search_result(history:list,instructions:str, messages:list,data:dict):
    # set default filter string
    #filterString = 'not group_ids/any()'
    # filterString=get_filter_string(instructions, messages, data)
    filterString=None
    print("Filter String:",filterString)
    search_message=[]
    language = data["siteInfo"].get("language", "en")
    if len(history) == 0:
        #call the cognitive search index
        results = search_index(
            query=instructions, top=10, filter=filterString,
            query_language=language)
        # create list of source content
        search_string=instructions
    else:
      #user message should appear at the end ...add srachquery string
      history_system_context = {
                'role': 'system',
                'content': get_history_prompt()
            }
      search_message.append(history_system_context)
      search_message.extend(history[:4])
      search_message.extend(messages)
      logging.debug(search_message)
      chat_completion=get_completion(prompt=search_message,data=data,model=openai.default_deployment,max_token=50)
      search_string =chat_completion.choices[0].message["content"]
      logging.debug("search string :",search_string)
      results = search_index(
            query=search_string, top=5, filter=filterString,query_language=language)
    return search_string, results

# Define a route to handle POST requests
@app.post("/v2/chat/completions")
async def post_data(data: dict, request: Request):
    """Posts chat completion utilizing Cog Search for system prompting and persisting conversation to the Azure Sql"""

    messages = data["messages"]
    instructions = messages[-1]["content"]
    siteInfo= data["siteInfo"]
    domain =siteInfo["domain"]
    dialog_id = data["dialogId"]
    language = siteInfo.get("language", "Unknown")
    country = siteInfo.get("country", "Unknown")
    #appGroups = get_user_membership_information_from_auth_header(request)
    stream = data.get("stream", False)
    #userPrincipalName = get_user_upn_from_token_header(request)
    chatId = data["chatId"]
    model = openai.default_deployment

    bot_message=[]
    logging.info("Domain name ::"+domain)
    history = read_chat_history(chatId=chatId)

    logging.debug("history ::", history)

    search_string, results = get_search_result(history,instructions, messages,data)

    source_content = get_source_content_from_cog_search(results)
    

    # trim history and index
    history, search_content = trim_history_and_index_combined(history, source_content, 
                                                                                total_max_tokens - max_tokens - 300,
                                                                                model_name=model_name)

    # join by newline characters
    search_content = "\n".join(search_content)
    print("search content::",search_content)

    print("history from trim_history_index: ", history)

    # #get intent of user
    intent = get_user_intent(data=instructions)
    logging.debug(instructions)
    logging.info("intent :", intent)

    content = get_contact_info(domain,country=country,language=language)
    if is_query_about_balcklist_word(search_string)[0]:
        intent =is_query_about_balcklist_word(search_string)[1]
    
    if search_content.strip() == "":
        intent = "no_search_content"

    if intent.lower() in  get_static_response_map(content=content).keys():
        intent_content = get_static_response_map(content=content)[intent.lower()]
        chat_completion = static_chat_completion_response(chatId, model, intent, intent_content)
    
    elif intent.lower() in  {'recommendation','recommend'}:

        # top_5_purchases, top_5_products = get_product_recommendation(instructions)
        # prev_purchases =", ".join([f"{row['title']}" for index, row in top_5_purchases.iterrows()])
        # products = ", ".join([f"{row['title']}" for index, row in top_5_products.iterrows()])

        #context_template = get_recommendation_prompt(search_content,content,products,prev_purchases)
        context_template = get_recommendation_prompt(search_content, content)

        system_context = {
                'role': 'system',
                'content': context_template
            }
        
        logging.debug(system_context)
        logging.info("context_template :"+ context_template)

        bot_message.append(system_context)
        if history:
            bot_message.extend(history)
        bot_message.extend(messages)
        logging.debug(bot_message)
        chat_completion=get_completion(prompt=bot_message,data=data,model=openai.default_deployment,max_token=None)
    elif intent.lower() in  {'price'}:

        context_template = get_price_prompt(search_content,intent)

        system_context = {
                'role': 'system',
                'content': context_template
            }
        
        logging.debug("context_template :"+ context_template)

        bot_message.append(system_context)
        if history:
            bot_message.extend(history)
        instructions = messages[-1]["content"] + f' Point to price of {country} in {language}'
        #instructions.join("Point to US price")
        messages[-1]["content"] = instructions
        bot_message.extend(messages)
        logging.debug(bot_message)

        chat_completion=get_completion(prompt=bot_message,data=data,model=openai.default_deployment,max_token=None)
    
    else:
        # create context template
        context_template = get_main_prompt(search_content,instructions,content,intent)
            # create system context
        prompt_context = {

            "role": "user",

            "content": "Answer form the information given only. Don't answers anything which is not related to FLUKE "

        }
        system_context = {
                'role': 'system',
                'content': context_template
            }
            # append cog search context to messages
            # log system context to module, derived from cog search
  
        logging.info("context_template :"+ context_template)
        bot_message.append(prompt_context)
        bot_message.append(system_context)
        if history:
            bot_message.extend(history)
        bot_message.extend(messages)
        logging.debug(bot_message)

        # load_dotenv()
        # openai.api_key = os.getenv("AZURE_OPENAI4_KEY")
        # # your endpoint should look like the following https://YOUR_RESOURCE_NAME.openai.azure.com/
        # openai.api_base = os.getenv("AZURE_OPENAI4_ENDPOINT")
        # openai.api_type = os.getenv("AZURE_OPENAI4_API_TYPE")
        # # This may change in the future
        # openai.api_version = os.getenv("AZURE_OPENAI4_API_VERSION")
        # # This will correspond to the custom name you chose for your deployment when you deployed a model.
        # openai.default_deployment = os.getenv("AZURE_OPENAI4_DEPLOYMENT")

        chat_completion=get_completion(prompt=bot_message,data=data,model=openai.default_deployment,max_token=None)

        # openai.api_key = os.getenv("AZURE_OPENAI_KEY")
        # # your endpoint should look like the following https://YOUR_RESOURCE_NAME.openai.azure.com/
        # openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
        # openai.api_type = os.getenv("AZURE_OPENAI_API_TYPE")
        # # This may change in the future
        # openai.api_version = os.getenv("AZURE_OPENAI_API_VERSION")
        # # This will correspond to the custom name you chose for your deployment when you deployed a model.
        # openai.default_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
        
    chat_completion['choices'][0]['message']['content'] =update_href_tag(chat_completion['choices'][0]['message']['content'])
    prod_list = ['ii900', 'ii910', '1777', '1775', '754', '1738', '789', '725', 'Ti480', 'TiS75', 'SMFT-1000/KIT', 'SMFT-1000/PRO', 'SMFT-1000/FPC', 'SMFT', 'SMFT-100', 'PVA-1500/FPC', 'PVA-1500/FPC3', 'PVA-1500HE2', 'PVA-1500T2', 'PVA', 'SOL-DMM87V-KIT', 'SOL-INS37-KIT', 'SOL-INS87-KIT', 'SOL-TI-27HZKIT', 'SOL-TRNG-FULL', 'SOL']
    pattern = r'\b(?:' + '|'.join(prod_list) + r')\b'
    if re.search(pattern, chat_completion['choices'][0]['message']['content'], flags=re.IGNORECASE):
        chat_completion['choices'][0]['message']['content'] += ' Interested in speaking to an expert or viewing a product demo? Complete this <a href="https://forms.fluke.com/IG-GLOBAL-MULTI-2019-DemoContactRequest-USEN-LP-1-A?lcid=9f3dd16e-49fc-ee11-a1ff-6045bd006295&plt=200000000&cra=100000000&redir=https://www.fluke.com/en-us/fluke/thank-you-for-contacting-fluke&utm_source=web&utm_medium=chatbot&utm_campaign=kaizen-chatbot" target="_blank">form</a>, and our experts will reach out to you.'
    # elif intent.lower() in  {'recommendation','recommend'}:
    #     disc_msgs = [' Surprise! Take advantage of the discount code now before it expires! Click here to accept terms and see your 10% discount code eligible on fluke.com or authorized Fluke distributors!', ' Ready, set, save! Enjoy 10% off before it expires! Click here to accept terms and see your 10% discount code eligible on fluke.com or authorized Fluke distributors!!', ' Psst... Want to score a deal? Take advantage of the discount code now before it expires! Click here to accept terms and see your 10% discount code eligible on fluke.com or authorized Fluke distributors! Shh, it\'s our little secret!']
    #     disc_msg = random.choice(disc_msgs)
    #     chat_completion['choices'][0]['message']['content'] += disc_msg

    if stream:
        compl_gen = completion_stream(
            chatId, bot_message, chat_completion)
        return StreamingResponse(compl_gen)
    else:
        messages.append({
            "role": chat_completion['choices'][0]['message']['role'],
            "content": chat_completion['choices'][0]['message']['content']
        })
        save_completion_response(chatId,dialog_id, messages,intent,language,country,domain)
        return JSONResponse(chat_completion)


@app.get("/v1/models")
async def list_models():
    """Returns a list of models to get app to work."""
    result = openai.Deployment.list()
    print(result)

    return result

@app.post("/v1/chat_summary")
async def post_data(data: dict):
    """Basic route for testing the API works"""
    print("Chat Summary!")
    result = summarise_chat_queries()
    return JSONResponse(result)

@app.post("/")
async def post_data(data: dict):
    """Basic route for testing the API works"""
    print("Hello World!")
    result = {"message": "Data received", "data": data}
    return result
