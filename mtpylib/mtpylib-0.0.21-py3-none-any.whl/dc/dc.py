#!/use/bin/env python3


import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from re import sub
import httpserver_loading
import subprocess, shlex
import threading
import pathlib
import uuid
import process_helper

print("dc v2 start")