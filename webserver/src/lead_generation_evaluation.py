import json
import sys
import logging
import requests
import openai
import datetime
import os
from .database import get_chat_queries ,read_chat_history ,update_query_type_details


def get_completion(prompt, model=openai.default_deployment): # Andrew mentioned that the prompt/ completion paradigm is preferable for this class
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        deployment_id=model,
        messages=messages,
        temperature=0, # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]

def get_summary_prompt(chat_history):
    summary_prompt = f"""
    Your task is to generate a short summary of a chat history between user and assistant

    Summarize the chat history below, delimited by triple 
    backticks, in at most 50 words. 

    Chat History: ```{chat_history}```
    """
    return summary_prompt

def get_category_prompt(chat_history):
    category_prompt = f"""
    Your task is to categorize a chat history between user and assistant

    Categorize the chat history below, delimited by triple backticks, as "buy" or "support".

    Answer in one word only. 
    If the questions are related to purchasing a product or service, then say "buy".
    If the questions are related to getting help with an existing product or service, then say "support"

    For example, "How do I buy a new laptop?" would be categorized as a "buy" question, while "My laptop won't turn on, what should I do?" would be categorized as a "support" question.

    Chat History: ```{chat_history}```
    """
    return category_prompt


def summarise_chat_queries():
    try:
        curr_6 = (datetime.datetime.now() - datetime.timedelta(hours=6))
        result_timestamp_str = curr_6.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]
        chatIdList = set(get_chat_queries(result_timestamp_str))
        print("chatIdList :: ",chatIdList)
        buy_category = 0
        service_category = 0
        for chatId in chatIdList:
            chatHistory = read_chat_history(chatId)
            print("chatHistory :: ",chatHistory)
            if len(chatHistory)>0:
                summary = get_completion(get_summary_prompt(chat_history=chatHistory))
                category = get_completion(get_category_prompt(chat_history=chatHistory))
                print("summary :: ",summary)
                print("category :: ",category)
                query_type_is_defined=1
                result = update_query_type_details(chatId,summary,category,query_type_is_defined)
                print("result :: ",result)
                if category == "buy":
                    buy_category += 1
                elif category == "support":
                    service_category += 1
        return {"buy_category":buy_category,"service_category":service_category}    
    except Exception as e:
        logging.error(f"Error occured in summarise_chat_queries: {str(e)}")
        return {}