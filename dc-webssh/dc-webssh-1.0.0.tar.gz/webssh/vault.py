#! /usr/bin/env python3
# Copyright (C) 2018-2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
# Author: Karthik Kumaar <karthikx.kumaar@intel.com>

import hvac
import json

VCENTER_PW = ""
MONGODB_PW = ""
MONGODB_MP = ""
SFTP = ""
SECRET_KEY = ""


# Load Token
with open('webssh/vault-certs/token.json', 'r') as f:
    token = json.load(f)

client = hvac.Client(url='https://10.224.79.50:8200/',
    token = token["value"],
    cert=("webssh/vault-certs/vaultcert.crt", "webssh/vault-certs/vaultcert.key"),
    #proxies = proxies,
    verify = "webssh/vault-certs/vaultcert.pem"
    ) 

print(client.is_authenticated())

print("inside vault file")
# Get Vcenter Secrets from vault
response = client.secrets.kv.v2.read_secret_version(mount_point='kv', path='vcenter')
VCENTER_PW = response['data']['data']['password']

# Get MongoDB Connection string secret for HW Selection
response = client.secrets.kv.v2.read_secret_version(mount_point='kv', path='mongodb_hw')
MONGODB_PW = response['data']['data']['password']

# Get MongoDB Connection string secret for Marketplace items
response = client.secrets.kv.v2.read_secret_version(mount_point='kv', path='mongodb_mp')
MONGODB_MP = response['data']['data']['password']

# Get SFTP connection secret
response = client.secrets.kv.v2.read_secret_version(mount_point='kv', path='sftp')
SFTP = response['data']['data']['password']

# Get JWT Secret Key connection secret
response = client.secrets.kv.v2.read_secret_version(mount_point='kv', path='jwt')
SECRET_KEY = response['data']['data']['token']

