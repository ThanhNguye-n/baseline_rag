# import modules
from elasticsearch import Elasticsearch
from getpass import getpass
from urllib.request import urlopen
import json
from time import sleep

ELASTIC_CLOUD_ID  = "Multimodel_RAG:dXMtY2VudHJhbDEuZ2NwLmNsb3VkLmVzLmlvOjQ0MyRkY2NiOTA4MmJkYTc0MzFkOWJmZTk3ZGRhOTc2MzJmNSQwNmIxZDk4ZDQyYjk0Y2JmOWI4ZTA5ZDkzMTk2NDQ3ZQ=="
ELASTIC_API_KEY  = "ano2cUI0NEJ5QjlHQmJDQmZiSWo6dHg2TFEwcDVScEdzQ1kweE5xT09WQQ=="

es = Elasticsearch(
    cloud_id=ELASTIC_CLOUD_ID, api_key=ELASTIC_API_KEY, request_timeout=600
)

print(es.info())  # should return cluster info