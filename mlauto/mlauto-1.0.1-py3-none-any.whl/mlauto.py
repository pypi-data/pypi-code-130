import torch
import torchvision
import matplotlib.pyplot as plt
import numpy as np
random_seed = 1
torch.backends.cudnn.enabled = False
torch.manual_seed(random_seed)
from scipy.signal import savgol_filter

import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import os

import socket
import json

def send_data_to_db(data):

  host = '127.0.0.1'  # Standard loopback interface address         
  port = 6000       # Port to listen on (non-privileged ports are > 1023)
  client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  client.connect((host, port))

  from_server = client.recv(4096)
  print(from_server)

  client.send(json.dumps(data).encode())
  

def train(network, epoch, train_loader, it, optimizer, lr, train_loss_lr, lr_scheduler):
  logging_interval = 2 #After every 2 batches

  network.train()
  train_loss = 0
  for batch_idx, (data, target) in enumerate(train_loader):
    it.append(1)
    optimizer.zero_grad() #
    output = network(data)
    loss = F.nll_loss(output, target) #
    train_loss += loss.item()
    loss.backward()
    optimizer.step()

    lr.append(optimizer.param_groups[0]["lr"])
    train_loss_lr.append(loss.item())

    lr_scheduler.step()

  return network, it, optimizer, lr, train_loss_lr, lr_scheduler

def lr_range_finder(network, train_loader, name):

  #DEFINE OPTIMIZER

  start_lr = 1e-8
  momentum = 0.5
  optimizer = optim.SGD(network.parameters(), lr=start_lr, momentum=momentum)
  lr_scheduler = torch.optim.lr_scheduler.ExponentialLR(optimizer, gamma=1.017)

  #LR RANGE FINDER

  lr = []
  train_loss_lr = []
  it = []

  print("Making folder 'results'...")
  try:
    os.mkdir('results')
  except:
    pass

  print("Starting LR finder...")
  n_epochs = 80
  for epoch in range(1, n_epochs+1):
    network, it, optimizer, lr, train_loss_lr, lr_scheduler = train(network, epoch, train_loader, it, optimizer, lr, train_loss_lr, lr_scheduler)
    if len(it)>1000:
      break

  print(lr)

  metrics = {'lr':lr, 'train_loss_lr':train_loss_lr, 'name': name}

  send_data_to_db(metrics)


