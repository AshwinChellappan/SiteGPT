import openai

total_max_tokens=16000
max_tokens=1024
model_name="gpt-3.5-turbo"
def get_static_response_map(content):
    intent_map ={
        'safety': f"It sounds like you are interested in learning more about safety. Please refer to the safety page https://www.fluke.com/en-us/learn/blog/safety. Or if you are looking for safety information for a specific product, check the product specific safety rating or manual. You can also talk to a specialist by visiting the following URL: https://www.fluke.com/en-us/support/about-us/contact-us",
        'safe': f"It sounds like you are interested in learning more about safety. Please refer to the safety page https://www.fluke.com/en-us/learn/blog/safety. Or if you are looking for safety information for a specific product, check the product specific safety rating or manual. You can also talk to a specialist by visiting the following URL: https://www.fluke.com/en-us/support/about-us/contact-us",
        's':f"For questions regarding the safe use of Fluke tools, please refer to your owners manual. You must comply with your employer’s safety standards and obtain necessary training before making electrical measurements.If you need help, {content}",
        'legal': f"It sounds like you are interested in talking to someone in legal or human resources. If I misunderstood your prompt, please rephrase your question. Otherwise, please refer to the contact page for additional resources https://www.fluke.com/en-us/support/about-us/contact-us",
        'spam': f"It sounds like you are interested in talking to someone in legal or human resources. If I misunderstood your prompt, please rephrase your question. Otherwise, please refer to the contact page for additional resources https://www.fluke.com/en-us/support/about-us/contact-us",
        'competitors':f"I am not sure how to answer this question. Can you please rephrase it to something more specific to Fluke’s products and services?",
        'compet':f"I'm Sorry, I can't seem to answer that question.  I'm always learning and will be able to answer more questions in the future.  In the meantime, if you need support for this question, {content}",
        'sanctioned':f"It sounds like you are interested in talking to someone in legal or human resources. If I misunderstood your prompt, please rephrase your question. Otherwise, please refer to the contact page for additional resources https://www.fluke.com/en-us/support/about-us/contact-us",
        'compliance':f"It sounds like you are interested in talking to someone in legal or human resources. If I misunderstood your prompt, please rephrase your question. Otherwise, please refer to the contact page for additional resources https://www.fluke.com/en-us/support/about-us/contact-us",
        'infringement':f"It sounds like you are interested in talking to someone in legal or human resources. If I misunderstood your prompt, please rephrase your question. Otherwise, please refer to the contact page for additional resources https://www.fluke.com/en-us/support/about-us/contact-us",
        'violation':f"It sounds like you are interested in learning more about safety. Please refer to the safety page https://www.fluke.com/en-us/learn/blog/safety. Or if you are looking for safety information for a specific product, check the product specific safety rating or manual. You can also talk to a specialist by visiting the following URL: https://www.fluke.com/en-us/support/about-us/contact-us",
        'confidential':f"It sounds like you are interested in talking to someone in legal or human resources. If I misunderstood your prompt, please rephrase your question. Otherwise, please refer to the contact page for additional resources https://www.fluke.com/en-us/support/about-us/contact-us",
        'personal':f"I am not sure how to answer this question. Can you please rephrase it to something more specific to Fluke’s products and services?",
        'conf':f"It sounds like you are interested in talking to someone in legal or human resources. If I misunderstood your prompt, please rephrase your question. Otherwise, please refer to the contact page for additional resources https://www.fluke.com/en-us/support/about-us/contact-us",
        'hr':f"It sounds like you are interested in talking to someone in legal or human resources. If I misunderstood your prompt, please rephrase your question. Otherwise, please refer to the contact page for additional resources https://www.fluke.com/en-us/support/about-us/contact-us",
        'discounts':f"I am not sure how to answer this question. Can you please rephrase it to something more specific to Fluke’s products and services?",
        'unrelated':f"I am not sure how to answer this question. Can you please rephrase it to something more specific to Fluke’s products and services?",
        'unrelat':f"I'm Sorry, I can't seem to answer that question.  I'm always learning and will be able to answer more questions in the future.  In the meantime, if you need support for this question, {content}",
        'contact':f"I am not sure how to answer this question. Can you please rephrase it to something more specific to Fluke’s products and services?",
        'warranty':f"For information about the warranty coverage for Fluke tools, {content}",
        'w':f"For information about the warranty coverage for Fluke tools, {content}",
        'blacklist_word':f"I'm Sorry, I can't seem to answer that question.  I'm always learning and will be able to answer more questions in the future.  In the meantime, if you need support for this question, {content}",
        'no_search_content' :f"I'm Sorry, I can't seem to answer that question.  I'm always learning and will be able to answer more questions in the future.  In the meantime, if you need support for this question, {content}"
    }
    return intent_map

def get_contact_info(domain,country,language):
    if domain =="fcal" and country == "eu":
        content = f'''Please contact the FlukeCal Customer Care Center.
          You can find relevant contact information at https://{country}.flukecal.com/{language}/about/contact.
          If you are looking for product information , please visit https://{country}.flukecal.com/{language}/products.
          If you are looking for support , please visit https://{country}.flukecal.com/{language}/support.
          If you are looking for specific articles or application notes , please visit https://{country}.flukecal.com/{language}/blog.'''
    elif domain == "fcal":
        content = f'''Please contact the FlukeCal Customer Care Center.
        You can find relevant contact information at https://{country}.flukecal.com/about/contact.
        If you are looking for product information , please visit https://{country}.flukecal.com/products.
        If you are looking for support, please visit https://{country}.flukecal.com/support.
        If you are looking for specific articles or application notes, please visit https://{country}.flukecal.com/blog.'''
    elif domain == "fnet" and country == "us":
        content = f'''Please contact the Fluke Networks Customer Care Center. 
        You can find your region specific relevant contact information at https://wwww.flukenetworks.com/contact.
        If you are looking for product information , please visit https://www.flukenetworks.com/products.
        If you are looking for support please visit https://www.flukenetworks.com/support.
        If you are looking for specific articles or application notes please visit https://www.flukenetworks.com/blog.'''
    elif domain == "fnet"  :
        content = f'''Please contact the Fluke Networks Customer Care Center. 
        You can find your region specific relevant contact information at https://{language}.flukenetworks.com/contact.
        You can find product information at https://{language}.flukenetworks.com/products.
        If you are looking for support please visit https://{language}.flukenetworks.com/support.
        If you are looking for specific articles or application notes please visit https://{language}.flukenetworks.com/blog.'''
    elif domain == "fpi" and country == "us":
        content = f'''Please contact the Fluke Networks Customer Care Center. 
        You can find your region specific relevant contact information at https://www.flukeprocessinstruments.com/en-us/service-and-support.
        If you are looking for product information , please visit https://www.flukeprocessinstruments.com/en-us/products.
        If you are looking for support please visit https://www.flukeprocessinstruments.com/en-us/service-and-support.
        If you are looking for specific articles or application notes please visit https://www.flukeprocessinstruments.com/en-us/service-and-support/knowledge-center.'''
    
    elif domain == "fpi":
        content = f'''Please contact the Fluke Networks Customer Care Center. 
        You can find your region specific relevant contact information at https://www.flukeprocessinstruments.com/{language}/service-and-support.
        If you are looking for product information , please visit https://www.flukeprocessinstruments.com/{language}/products.
        If you are looking for support please visit https://www.flukeprocessinstruments.com/{language}/service-and-support.
        If you are looking for specific articles or application notes please visit https://www.flukeprocessinstruments.com/{language}/service-and-support/knowledge-center.'''
    elif domain == "fluke":
        content = f'''Please contact the Fluke Customer Care Center.
        You can find relevant contact information at https://www.fluke.com/{language}-{country}/support/about-us/contact-us.
        If you are looking for product information , please visit https://www.fluke.com/{language}-{country}/products.
        If you are looking for support please visit https://www.fluke.com/{language}-{country}/support.
        If you are looking for specific articles or application notes please visit https://www.fluke.com/{language}-{country}/learn.'''
    return content

def get_completion(prompt,data, model=openai.default_deployment,max_token=None): # Andrew mentioned that the prompt/ completion paradigm is preferable for this class
    response = openai.ChatCompletion.create(
                deployment_id=model,
                frequency_penalty=data.get("frequency_penalty", 0),
                max_tokens=data.get("max_tokens", max_token),
                n=data.get("n", 1),  # Number of messages
                presence_penalty=data.get("presence_penalty", 0),
                temperature=data.get("temperature", 0.0),
                top_p=data.get("top_p", 1),  # Nucleus Sampling
                messages=prompt,
                stream=data.get("stream", False),
            )  
    return response


def get_history_prompt():
    history_context = f"""Below is a history of the conversation so far, and a new question asked by the user that needs to be answered by searching in a knowledge base about Fluke products.
    If the person has provided a model number, such as BP881, TP88/WWG, FLUKE-STICKYBEAT, C550, or FL-45 EX, that must be a keyword you generate.
    Generate a search query based on the conversation and the new question. 
    Do not include cited source filenames and document names e.g info.txt or doc.pdf in the search query terms.
    Do not include any text inside [] or <<>> in the search query terms."""
    return history_context

def get_recommendation_prompt(search_content,content):
    context_template = f"""

            You are a chatbot for Fluke.com.

            Keep your response concise and under 50 words if possible.

            Don't justify your answers. Don't give information not mentioned in the CONTEXT INFORMATION.

            Answer the QUESTION from the CONTEXT below only and follow the INSTRUCTIONS verbatim.

 

            CONTEXT :

            **************

 
            1. Here is the search context {search_content}.

        
            **************
 

            INSTRUCTIONS :

            1. Keep your response concise and under 50 words if possible.

            2. Please provide a brief explanation of your recommendations using the CONTEXT provided above.Each source has a CONTENT followed by colon and the actual information, always include the URL for each fact you use in the response. List the URLs separately

            3. Find the best product recommendations based on the description provided for the product.

            4. Refer to the top pick accessories to recommend the best product for the user.

            5. If answers are not present in the above Context, Generate a message that includes contact and product information instead of apologizing give {content}.

            6. Talk like a person, do not just give a list of recommendations.

            7. List the recommendations along with the URL mentioned in the CONTEXT.

           

            """
    return context_template

def get_price_prompt(search_content,content):
    context_template = f"""

            You are a chatbot for Fluke.com.

            Don't justify your answers. Don't give information not mentioned in the CONTEXT INFORMATION.

            Answer the QUESTION from the CONTEXT below only and follow the INSTRUCTIONS.

 

            CONTEXT :

            **************

 
            1. Here is the search context {search_content}.
 

            **************
 

            INSTRUCTIONS :

            1. Each source has a CONTENT followed by colon and the actual information, always include the URL for each fact you use in the response. List the URLs separately

            2. Always point user to the product page for which price is being asked.
            
            3. If answers are not present in the above Context, Generate a message that includes our contact information instead of apologizing give {content}.

            """
    return context_template

def get_main_prompt(search_content,instructions,content,intent):
    context_template = f"""

            You are a chatbot for Fluke.com.

            Keep your response concise and under 50 words if possible.

            Don't justify your answers. Don't give information not mentioned in the CONTEXT INFORMATION.

            Answer the QUESTION from the CONTEXT below only and follow the INSTRUCTIONS verbatim.

 

            CONTEXT :

            **************

 

            {search_content}

 

            **************

 

 

 

 

            QUESTION : {instructions}

 

 

            INSTRUCTIONS :

            1. Keep your response concise and under 50 words if possible. If the question provided is not sufficient to provide an answer, ask the user for additional input to clarify the question.

            2. If answers are not present in the above Context, Generate a message that includes our contact information and other details instead of apologizing give {content}.

            3. Do not answer any QUESTION which is not related to fluke.com

            4. Answer in Brief with the details from the context and also provide the URL's.

            5. Do not Generate a response that contains any reference URLs that mention Russia or Europe Union . 

            6. If the {intent} is related with 'repair' then add this message For RMA queries please visit https://flkext.fluke.com/OA_HTML/jtflogin.jsp

            7. For tabular information return it as an html table. Do not return markdown format.

            """
    return context_template

def get_product_dict():
    prod_dict = {'Product Category': ['ELEC & GROUND TEST',
  'ELEC & GROUND TEST',
  'ELEC & GROUND TEST',
  'ELEC & GROUND TEST',
  'ELEC & GROUND TEST',
  'ELEC & GROUND TEST',
  'ELEC & GROUND TEST',
  'ELEC & GROUND TEST',
  'ELEC & GROUND TEST'],
 'Prod Family': ['EPROD',
  'EPROD',
  'EPROD',
  'EPROD',
  'EPROD',
  'EPROD',
  'EPROD',
  'EPROD',
  'EPROD'],
 'MODEL': ['FLUKE-378 FC',
  'FLUKE-377 FC',
  'FLUKE-376  FC',
  'FLUKE-375  FC',
  'FLUKE-374  FC',
  'FLUKE- 325',
  'FLUKE- 324',
  'FLUKE- 323',
  'FLUKE-302+/EM ESP'],
 'Fluke Part Number': [5111812,
  5111781,
  5065965,
  5065976,
  5065983,
  5065866,
  5065853,
  5065521,
  4156257],
 'DESCRIPTION': ['1000A AC/DC TRMS NONCONTACT VOLTAGE WIRELESS CLAMP W/PQ INDICATOR,IFLEX',
  '1000A AC/DC TRMS NONCONTACT VOLTAGE WIRELESS CLAMP W/ IFLEX',
  '1000A AC/DC TRMS WIRELESS CLAMP W/ IFLEX (AMERICAS)',
  '600A AC/DC TRMS WIRELESS CLAMP (AMERICAS)',
  '600A AC/DC TRMS WIRELESS CLAMP(AMERICAS)',
  '400A AC/DC TRUE RMS CLAMP METER W/TEMP (AMERICAS)',
  '400A AC TRUE RMS CLAMP METER W/TEMP (AMERICAS)',
  '400A AC TRUE RMS CLAMP METER (AMERICAS)',
  '400A AC CLAMP, EMERGING ESP'],
 'Rank': [1, 2, 3, 4, 5, 6, 7, 8, 9],
 'MODEL_prev': ['FLUKE-377 FC',
  'FLUKE-376  FC',
  'FLUKE-375  FC',
  'FLUKE-374  FC',
  'FLUKE- 325',
  'FLUKE- 324',
  'FLUKE- 323',
  'FLUKE-302+/EM ESP',
  None]}
    return prod_dict