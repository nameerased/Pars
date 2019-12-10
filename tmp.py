# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import os
import re
import requests
import csv
import json
from models import Petition
import time


x = Petition.select().count()
print(x)
