import os 
import sys 

#  Add the parent directory to the path to import db_connection
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db.src.scripts.util.db_connection import db_connect

from chatbot.vector_store import build_vector_store
build_vector_store(db_connect)
