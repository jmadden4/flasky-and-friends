
#import json
#import configparser
#import re
#from base64 import b64encode
#from flask import url_for
#from app import create_app
#from app import create_app, db
#from app.models import User, Role, Post, Comment

#import os
#from kafka import KafkaProducer
#from kafka.errors import KafkaError
#from config.kafka import KafkaConfig

#producer = KafkaProducer(bootstrap_servers=['localhost:9092'])
#KAFKA_HOME = os.environ.get('KAFKA_HOME')
#print KAFKA_UTILS_PATH
#print 'who diskey'


import sys, os
#from kafka import KafkaProducer
#from kafka.errors import KafkaError
import json
from flask import current_app
from app import create_app, db   
#import configparser
#from flask import current_app, request, url_for
#from kafka import 
#from current_app import kafka

#print KAFKA_VAR

#KAFKA_HOME_PATH_OS=os.environ.get('KAFKA_HOME')
#exec 'kafka-utils/list-topics.sh'
def startKafka():
	global diskeyStartKafka
	print 'going to start zookeepr & kafka now'
	#diskeyStartKafka = os.system('/home/joe/workspace/flasky/kafka-utils/KafkaQuickstart.sh')	
	#exec os.system('/home/joe/workspace/flasky/kafka-utls/KafkaQuickStart.sh') in globals(), locals()
	def subfunction():
		return True

#producer = KafkaProducer(bootstrap_servers=['localhost:9092'])
#print os.environ.get('KAFKA_HOME')
#ListOfTopics = os.system('/home/joe/workspace/flasky/kafka-utils/list-topics.sh')
#print 'obtainedTopics!'
#print ListOfTopics
#print 'lets launch a consumer'
#os.system('/home/joe/workspace/flasky/kafka-utils/start-consumer.sh')
