# import Data_Processing_Transformation as DPT
import Feature_Extraction
import Message_Classifier
from Kaggle_Miner import mine_conversations
from Kaggle_IDF import Kaggle_IDF
from datetime import datetime
from pm4py.objects.log.exporter.xes import factory as xes_exporter
import Extraction_from_json



if __name__ == '__main__':


    """ Hyper-parameters """
    # How long is a conversation active for? In minutes
    conversation_duration = 15.0  # Minutes

    # Pandas chunk size
    chunksize = 10 ** 3

    # Stop datetime
    stop_datetime = datetime.strptime("2020-01-10T00:00:00.000Z", '%Y-%m-%dT%H:%M:%S.%fZ')

    """ Runner Code """
    idf = Kaggle_IDF(chunksize, stop_datetime, "Data/Synthetic/synthetic_data.csv")
    print("Done mining words")


    log = mine_conversations(idf, "Data/Synthetic/synthetic_data.csv", stop_datetime, chunksize, conversation_duration)
    print("Done mining conversations")


    xes_exporter.export_log(log, "synthetic_data_processed.xes")






