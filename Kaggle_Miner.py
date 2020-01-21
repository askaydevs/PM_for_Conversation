import pandas as pd
from datetime import datetime

import Feature_Extraction
import Message_Classifier
from Conversation import Conversation
from pm4py.objects.log.util.log import log as pmlog
import Text_Preprocessing as TP


""" Main Functions """


def mine_conversations(idf, csv_file_path, stop_datetime, chunksize, conversation_duration):
    datetime_object = datetime.strptime("2015-01-01T00:00:00.000Z", '%Y-%m-%dT%H:%M:%S.%fZ')
    break_loop = False
    open_conversations = []
    log = pmlog.EventLog()
    score_stats = []
    message_classifier = Message_Classifier.MessageClassifier()
    message_classifier.load_models()
    dataprocess = Feature_Extraction.DataProcessing()

    columns = ['id', 'text', 'sent', 'fromUser.username']
    for chunk in pd.read_csv(csv_file_path, chunksize=chunksize, usecols=columns, sep=','):
        # Terminate after late date, to trim dataset.

        if datetime_object > stop_datetime:
            break_loop = True


        if break_loop:
            break

        for index, row in chunk.iterrows():

            try:
                # Start by getting the variables we need
                text = row["text"]

                if str(text) == "nan":
                    continue

                if len(text.split(" ")) <= 2: # Filter out messages with less than n words
                    continue


                datetime_object = datetime.strptime(row["sent"], '%Y-%m-%dT%H:%M:%S.%fZ')



                event_dict = {}
                event_dict["User id"] = row["fromUser.username"]
                event_dict["Date"] = datetime_object
                event_dict["Content"] = text
                event_dict["Class"] = None


                for conversation in open_conversations:
                    time_diff = (datetime_object - conversation.open_time).total_seconds() / 60.0
                    if time_diff > conversation_duration:
                        if len(conversation.message_texts) > 1:
                            try:
                                log.append(conversation.add_to_trace())
                                conversation.write_to_txt()
                            except ValueError:
                                open_conversations.remove(conversation)
                                continue
                        open_conversations.remove(conversation)


                # Now we find our text body
                tf_idf_message = {}
                text_list = TP.preprocess_text(text)
                for word in set(text_list):
                    if word in idf:
                        tf_idf_message[word] = (text_list.count(word) / len(text_list)) * idf[word]

                mention = TP.get_mentions(text)

                added = False
                if len(mention) > 0:
                    for conversation in open_conversations:
                        if conversation.is_person_in_conversation(mention[0][1:]) and not added:
                            conversation.add_message(event_dict, message_text=row['text'], person=row['fromUser.username'],
                                                     idf=idf)
                            added = True
                            break

                if not added:
                    # Find the best matching conversation
                    score = 0
                    best_matching_conversation = None
                    for conversation in open_conversations:
                        conversation_score = conversation.similarity_score(tf_idf_message)
                        if conversation_score > score:
                            score = conversation_score
                            best_matching_conversation = conversation

                    if best_matching_conversation != None and score > 0.05:
                        score_stats.append(score)
                        best_matching_conversation.add_message(event_dict, message_text=row['text'],
                                                               person=row['fromUser.username'],
                                                               idf=idf)

                    else:
                        convo = Conversation(open_time=datetime_object,
                                             event_dict=event_dict, message_text=row['text'], person=row['fromUser.username'],
                                             idf=idf,
                                             classifier=message_classifier, dataprocessing=dataprocess)

                        open_conversations.append(convo)

            except AttributeError as e:
                print(e)
                continue

        print("Conversation mining. Date: " + row["sent"])

    for conversation in open_conversations:
        # if len(conversation.message_texts) > 1:
        log.append(conversation.add_to_trace())
        conversation.write_to_txt()
        # open_conversations.remove(conversation)

    return log