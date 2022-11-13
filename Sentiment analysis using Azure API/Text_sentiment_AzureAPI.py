import os
import numpy as np
import time
from typing import List, Tuple, Sized
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import ServiceResponseError, HttpResponseError
from dotenv import load_dotenv, find_dotenv


class DummyResponse():
    def __init__(self):
        self.sentiment = None
        self.confidence_scores = DummyConfidence()
        self.sentences = DummySentence()


class DummyConfidence():
    def __init__(self):
        self.positive = None
        self.neutral = None
        self.negative = None


class DummySentence():
    def __init__(self):
        self.sentiment = None
        self.confidence_scores = DummyConfidence()
        self.text = None

def get_azure_text_analytics_keys():
    load_dotenv(find_dotenv())
    # need to fill credential here
    AZURE_TA_KEY= '#########'
    AZURE_TA_ENDPOINT='https://##########'
    key = AZURE_TA_KEY
    endpoint = AZURE_TA_ENDPOINT
    return key, endpoint

def authenticate_client():
    key, endpoint = get_azure_text_analytics_keys()
    ta_credential = AzureKeyCredential(key)
    text_analytics_client = TextAnalyticsClient(
        endpoint=endpoint,
        credential=ta_credential)
    return text_analytics_client

def client_score_batch(batch_data: List[str], max_text_len=5_000, max_tries=5) -> Tuple[List,List]:
    assert 0 < len(batch_data) <= 10, 'Batch data must between 0 and 10!'
    client = authenticate_client()
    _batch_data = [d[:max_text_len] for d in batch_data] # Azure API has a limit of max text length
    for i in range(max_tries):
        try:
            responses = client.analyze_sentiment(_batch_data)
            break
        except (ServiceResponseError, HttpResponseErro) as e:
            print(f'Error on batch data {_batch_data}: {e}')
            print('Retry in 5 seconds...')
            time.sleep(5)
    else:
        responses = [DummyResponse() for i in range(len(_batch_data))]

    return responses

def get_n_batches(data: Sized, batch_size: int):
    assert batch_size > 0 and isinstance(batch_size, int)
    return int(np.ceil(len(data)/batch_size))

def batch_generator(iterable:Sized, batch_size:int):
    assert 0 < batch_size, 'Batch size should be at least 1!'
    l = len(iterable)
    for idx in range(0, l, batch_size):
        yield iterable[idx:min(idx + batch_size, l)]

def parse_response(response):
    get_confidence = lambda s: max(s.positive, s.neutral, s.negative)
    parsed = dict()
    parsed['overall'] = (response.sentiment, get_confidence(response.confidence_scores))
    parsed['sentence'] = [(r.text, r.sentiment, get_confidence(r.confidence_scores)) for r in response.sentences]
    return parsed

def sentiment_analysis(document:List[str], batch_size=10):
    output = []
    n_batches = get_n_batches(documents, batch_size)
    for i, batch_data in enumerate(batch_generator(documents, batch_size)):
        print(f'scoring on batch {i+1}/{n_batches} ...')
        responses = client_score_batch(batch_data)
        output += [parse_response(r) for r in responses]
    return output