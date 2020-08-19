import os
from pprint import pprint

import nltk
import numpy as np
import pandas as pd
import pymongo
from dotenv import load_dotenv
from nltk.corpus import stopwords
from sklearn import datasets, svm
from sklearn.decomposition import NMF, TruncatedSVD
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import train_test_split

from helpers import connect_to_db, decontracted, display_topics
