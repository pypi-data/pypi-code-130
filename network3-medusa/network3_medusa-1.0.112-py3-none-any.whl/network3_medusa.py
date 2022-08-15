import os
import sys
import json
import click
import subprocess
import requests
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from hedera import Client, AccountId, PrivateKey, Hbar, FileCreateTransaction, FileContentsQuery, FileId, FileAppendTransaction, FileInfoQuery

OPERATOR_ID = AccountId.fromString(os.getenv("OPERATOR_ID"))
OPERATOR_PRIVATE_KEY = PrivateKey.fromString(os.getenv("OPERATOR_PRIVATE_KEY"))
WEBEX_ROOM = os.getenv("WEBEX_ROOM")
WEBEX_TOKEN = os.getenv("WEBEX_TOKEN")

class Network3Medusa():
    def __init__(self, command):
        self.command = command

    def network3_medusa(self):
        self.py2output()
        raw_json=self.output.stdout.decode('utf-8')
        if self.command == "show interface":
            json_dict = json.loads(raw_json)
            first = True
            for interface in json_dict['TABLE_interface']['ROW_interface']:
                if first:
                    first = False
                    raw_json=str(interface).replace("\'", "\"")
                    self.add_file_to_hedera(f"[{ raw_json },")
                elif interface == json_dict['TABLE_interface']['ROW_interface'][-1]:
                    raw_json=str(interface).replace("\'", "\"")
                    self.append_file_to_hedera(f"{ raw_json }]")
                else:
                    raw_json=str(interface).replace("\'", "\"")
                    self.append_file_to_hedera(f"{ raw_json },")

            query = FileInfoQuery().setFileId(self.fileId)
            info = query.execute(self.client)
            print("File size according to `FileInfoQuery`: ", info.size)            
            if WEBEX_ROOM:
                self.send_webex_notification()
        elif self.command == "show running-config":
            first = True
            for line in raw_json.split('\n'):
                if first:
                    first = False
                    print(line)
                    self.add_file_to_hedera(f"{ line } \n")
                else:
                    print(line)
                    self.append_file_to_hedera(f"{ line } \n")
            query = FileInfoQuery().setFileId(self.fileId)
            info = query.execute(self.client)
            print("File size according to `FileInfoQuery`: ", info.size)
        else:
            self.add_file_to_hedera(raw_json)
            if WEBEX_ROOM:
                self.send_webex_notification()
        
    def py2output(self):
        self.output = subprocess.run(["python", "call_cli.py", self.command], capture_output=True)

    def add_file_to_hedera(self, raw_json):
        self.client = Client.forTestnet()
        self.client.setOperator(OPERATOR_ID, OPERATOR_PRIVATE_KEY)
        tran = FileCreateTransaction()
        fileContents = raw_json
        print(fileContents)
        resp = tran.setKeys(OPERATOR_PRIVATE_KEY.getPublicKey()).setContents(fileContents).setMaxTransactionFee(Hbar(2)).execute(self.client)
        print("nodeId: ",  resp.nodeId.toString())
        self.nodeId = resp.nodeId.toString()
        receipt = resp.getReceipt(self.client)
        self.fileId = receipt.fileId
        query = FileInfoQuery().setFileId(self.fileId)
        info = query.execute(self.client)
        print("file: ",  self.fileId.toString())
        print("File size according to `FileInfoQuery`: ", info.size)
    def append_file_to_hedera(self, interface):
        tran = (FileAppendTransaction()
                .setFileId(self.fileId)
                .setContents(interface)
                .setMaxChunks(500)
                .setMaxTransactionFee(Hbar(2))
                .freezeWith(self.client))
        resp = tran.execute(self.client)
        self.receipt = resp.getReceipt(self.client)

    def send_webex_notification(self):
        template_dir = Path(__file__).resolve().parent
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        adaptive_card_template = env.get_template('sent_to_hedera.j2')
        adataptive_card_output = adaptive_card_template.render(roomid = WEBEX_ROOM, command = self.command, nodeid = self.nodeId, fileid = self.fileId.toString())
        webex_adaptive_card_response = requests.post('https://webexapis.com/v1/messages', data=adataptive_card_output, headers={"Content-Type": "application/json", "Authorization": f"Bearer { WEBEX_TOKEN }" })
        print('The POST to WebEx had a response code of ' + str(webex_adaptive_card_response.status_code) + 'due to' + webex_adaptive_card_response.reason)

@click.command()
@click.option('--command',
    prompt='Command',
    help=('A valid Command'),
    required=True)

def cli(command):
    invoke_class = Network3Medusa(command)
    invoke_class.network3_medusa()

if __name__ == '__main__':
    Network3Medusa.main()