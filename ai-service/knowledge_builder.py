import requests
import os
from bs4 import BeautifulSoup
import re

class KnowledgeBuilder:
    def __init__(self, knowledge_dir="./knowledge"):
        self.knowledge_dir = knowledge_dir
        os.makedirs(knowledge_dir, exist_ok=True)
    
    def crawl_mysql_docs(self, urls, output_dir="mysql"):
        """抓取MySQL官方文档"""
        save_dir = os.path.join(self.know