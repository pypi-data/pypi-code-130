# initialize the global variables that define the environment
import os
import socket
import sys

# network
hostname = socket.gethostname()
localController = "localhost"
externalUrl = "example.com"

# directory structure
rootDir = sys.path[0]+"/"        # directory containing this application
keyDir = rootDir+"keys/"
stateDir = rootDir+"state/"
soundDir = rootDir+"sounds/"
dataDir = rootDir+"data/"

# logging and debugging
sysLogging = True
debugEnable = False

# Localization
latLong = (0.0, 0.0)
elevation = 0 # elevation in feet
tempScale = "F"
defaultCountryCode = "1"
defaultAreaCode = "000"

# Metrics
sendMetrics=False
logMetrics=True
backupMetrics=True
purgeMetrics=False
purgeDays=5
logChanged=True

# REST parameters
restServicePorts = [7378, 7377, 7376, 7375, 7374, 7373, 7372, 7371]
restServicePort = 7378
restAdvertPort = 4244 # 7379
restNotificationPort = 7370
ipv4MulticastAddr = "224.0.0.1"
ipv6MulticastAddr = "ff02::1"
multicastAddr = ipv4MulticastAddr
restAdvertInterval = 10
restTimeout = 60
restRetryInterval = 10

# Alerts and events
alertConfig = {}
eventConfig = {}

# optionally import local variables
try:
    from conf import *
except ImportError:
    pass
