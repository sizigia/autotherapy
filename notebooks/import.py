import os
import pickle
import re
import unicodedata as ud
from pprint import pprint

import nltk
import numpy as np
import pandas as pd
import pyLDAvis
import pyLDAvis.sklearn
import pymongo
import spacy
from dotenv import load_dotenv
from nltk import pos_tag, word_tokenize
from nltk.corpus import stopwords
from sklearn import datasets, svm
from sklearn.decomposition import NMF, LatentDirichletAllocation, TruncatedSVD
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.metrics.pairwise import cosine_similarity

from helpers import (british_to_american, connect_to_db, decontracted,
                     display_topics, remove_hashtags_mentions_urls,
                     restore_spaced_title)
