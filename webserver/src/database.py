import os
import pyodbc, struct
from azure import identity
import json
import traceback
import logging

connection_string = os.environ.get('AZURE_SQL_ODBC_CONNECTIONSTRING')

def save_chat_rating(chatId, dialog_id, rating):
    try:
        with get_conn() as conn:
            cursor = conn.cursor()
            
            # Use MERGE to update or insert the rating based on chatId and dialog_id
            cursor.execute('''
                MERGE INTO [dbo].tblBotChat AS target
                USING (VALUES (?, ?, ?)) AS source (chatId, dialogId, rating)
                ON target.chatid = source.chatId AND target.dialogId = source.dialogId
                WHEN MATCHED THEN
                    UPDATE SET target.rating = source.rating
                WHEN NOT MATCHED THEN
                    INSERT (chatid, dialogId, rating)
                    VALUES (source.chatId, source.dialogId, source.rating);
            ''', chatId, dialog_id, rating)
            
            cursor.commit()

    except Exception as e:
        tb = traceback.format_exc()
        logging.error("Error occurred during insert/update operation. Stack Trace: " + tb)
        return False
    else:
        logging.info(f"Saved chat rating with chatId={chatId} and dialog_id={dialog_id}")
        return True

def save_completion_response(chatId,dialog_id, completion_response ,intent,language,country,domain):
    try:
        # Reason for comment - @amit.gupta@fortive.com
        # The completion response/db_message coming from line number 674-677 
        # of asgi.py, already adds news messages to the history.
        # so there is no need to again extend the new messages 
        # to history in the following lines (line 112)

        updatedCompletedResponse=completion_response
        logging.debug("updatedCompletedResponse: ", updatedCompletedResponse)
        logging.info(chatId,type(chatId))
        with get_conn() as conn:
            cursor = conn.cursor()               
            cursor.execute('''
            MERGE [dbo].[tblBotChat] AS [chth]
            USING (SELECT ?, ?,?,?,?,?,?) as src (ChatId,dialogId, ChatHistory,intent,language,country,domain)
            ON ([chth].ChatId = src.ChatId) AND ([chth].dialogId = src.dialogId)
            WHEN MATCHED THEN
                UPDATE SET [ChatHistory] =  src.ChatHistory, [dialogId]=src.dialogId,[updated_date]=GETDATE(),[intent]=src.intent ,[language]=src.language,[country]=src.country,[domain]=src.domain       
            WHEN NOT MATCHED THEN
                INSERT ([ChatId],[dialogId],[ChatHistory],[updated_date],[intent],[language],[country],[domain])
                VALUES (src.ChatId, src.dialogId, src.ChatHistory, GETDATE(),src.intent,src.language,src.country,src.domain)
            OUTPUT $action;
            ''',chatId, dialog_id,json.dumps(updatedCompletedResponse),intent,language,country,domain)
            cursor.commit()
    except:
        tb = traceback.format_exc()
        logging.error("error occurred: " + tb)
    else:
        tb = "No error"


def read_chat_history( chatId):
    try:
        logging.info("Inside read_chat_history - ChatID: ", chatId)
        with get_conn() as conn:
            cursor = conn.cursor()
            # Define the SQL query to retrieve chat history
            query = '''
                SELECT [ChatHistory]
                FROM [dbo].[tblBotChat]
                WHERE [ChatId] = ?
                ORDER by updated_date desc;
            '''

            # Execute the query with chatId as a parameter (use tuple)
            cursor.execute(query, (chatId,))

            # Fetch the result 
            result = cursor.fetchall()

            # Close the cursor (connection will be closed when exiting the 'with' block)
            cursor.close()
            chat_history_list =[]
            # Check if the result is not None before trying to access its contents
            if result is not None:
                # Use json.loads with a try-except block to handle potential JSON decoding errors
                try:
                    
                    for row in result:
                        print("row :: ",row)
                        chat_history_list.extend(json.loads(row[0]))
                    return chat_history_list  # Return ChatHistory as a list
                except json.JSONDecodeError as json_error:
                    logging.error(f"Error decoding JSON in read_chat_history:: {str(json_error)}")
                    return []  # Return an empty list if there is an error decoding JSON
            else:
                return []  # No matching record found
    except Exception as e:
        logging.error(f"Error occured in read_chat_history: {str(e)}")

        return []

def get_chat_queries(recent_6_hr):
    try:
        logging.info("Inside get_chat_queries ")
        print("Inside get_chat_queries where recent_6_hr: ", recent_6_hr)
        with get_conn() as conn:
            cursor = conn.cursor()
            # Define the SQL query to retrieve chat history
            query = f'''
                SELECT *
                FROM [dbo].[tblBotChat]
                WHERE [updated_date] <'{recent_6_hr}' and (query_type_is_defined IS NULL OR query_type_is_defined <> 1)
            '''
            print("query :: ",query)
            # Execute the query with chatId as a parameter (use tuple)
            cursor.execute(query)

            # Fetch the result
            result = cursor.fetchall()

            # Close the cursor (connection will be closed when exiting the 'with' block)
            cursor.close()

            # Check if the result is not None before trying to access its contents
            if result:
                # Use json.loads with a try-except block to handle potential JSON decoding errors
                chat_query_list = []
                for row in result:
                    try:
                        # Check the type of the data before loading it as JSON
                        chat_ID_data = row[1]
                        print("chat_data :: ",chat_ID_data)
                        if isinstance(chat_ID_data, (str, bytes, bytearray)):
                            chat_query_list.append(chat_ID_data)
                        else:
                            logging.warning(f"Unexpected data type: {type(chat_ID_data)}")
                    except json.JSONDecodeError as json_error:
                        logging.error(f"Error decoding JSON get_chat_queries: {str(json_error)}")
                return chat_query_list  # Return ChatHistory as a list
            else:
                return []  # No matching record found
    except Exception as e:
        logging.error(f"Error occured get_chat_queries: {str(e)}")

        return []
    

def update_query_type_details(chatId,query_summary,query_category,query_type_is_defined=1):
    print(f"Inside update_query_type_details for chatId : {chatId} and category :{query_category} ")
    try:
        with get_conn() as conn:
            cursor = conn.cursor()
            print("chatId update_query_type_details:: ",chatId)
            
            # Use MERGE to update or insert the rating based on chatId and dialog_id
            cursor.execute('''
                MERGE INTO [dbo].tblBotChat AS target
                USING (VALUES (?, ?,?,?)) AS source (chatId, query_summary,query_category,query_type_is_defined)
                ON target.chatId = source.chatId
                WHEN MATCHED THEN
                    UPDATE SET target.query_summary = source.query_summary,
                    target.query_category = source.query_category,
                    target.query_type_is_defined = source.query_type_is_defined
                WHEN NOT MATCHED THEN
                    INSERT (chatId, query_summary,query_category,query_type_is_defined)
                    VALUES (source.chatId, source.query_summary, source.query_category, source.query_type_is_defined);
            ''', chatId, query_summary, query_category , query_type_is_defined)
            
            cursor.commit()

    except Exception as e:
        print("Error occured in update_query_type_details: ",e)
        tb = traceback.format_exc()
        logging.error("Error occurred during insert/update operation. Stack Trace: " + tb)
        return False
    else:
        logging.info(f"Saved chat rating with chatId={chatId} ")
        return True

def get_conn():
    # credential = identity.DefaultAzureCredential()
    # token_bytes = credential.get_token("https://database.windows.net/.default").token.encode("UTF-16-LE")
    # token_struct = struct.pack(f'<I{len(token_bytes)}s', len(token_bytes), token_bytes)
    # SQL_COPT_SS_ACCESS_TOKEN = 1256  # This connection option is defined by microsoft in msodbcsql.h
    # conn = pyodbc.connect(connection_string, attrs_before={SQL_COPT_SS_ACCESS_TOKEN: token_struct})
    conn = pyodbc.connect(connection_string, autocommit=True)
    return conn