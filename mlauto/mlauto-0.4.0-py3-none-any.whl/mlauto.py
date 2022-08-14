import torch
import torchvision
import matplotlib.pyplot as plt
import numpy as np
%matplotlib inline
random_seed = 1
torch.backends.cudnn.enabled = False
torch.manual_seed(random_seed)
from scipy.signal import savgol_filter

import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import os

def train(epoch, train_loader, it, optimizer, lr, lr_loss, lr_scheduler):
  logging_interval = 2 #After every 2 batches

  network.train()
  train_loss = 0
  for batch_idx, (data, target) in enumerate(train_loader):
    it.append(1)
    optimizer.zero_grad()
    output = network(data)
    loss = F.nll_loss(output, target)
    train_loss += loss.item()
    loss.backward()
    optimizer.step()

    lr.append(optimizer.param_groups[0]["lr"])
    lr_loss.append(loss.item())

    lr_scheduler.step()

  return it, optimizer, lr, lr_loss, lr_scheduler

def lr_range_finder(network, train_loader):

  #DEFINE OPTIMIZER

  start_lr = 1e-8
  momentum = 0.5
  optimizer = optim.SGD(network.parameters(), lr=start_lr, momentum=momentum)
  lr_scheduler = torch.optim.lr_scheduler.ExponentialLR(optimizer, gamma=1.017)

  #LR RANGE FINDER

  lr = []
  lr_loss = []

  train_losses = []
  val_losses = []
  it = []

  print("Making folder 'results'...")
  try:
    os.mkdir('results')
  except:
    pass

  print("Starting LR finder...")
  n_epochs = 80
  for epoch in range(1, n_epochs+1):
    it, optimizer, lr, lr_loss, lr_scheduler = train(epoch, train_loader, it, optimizer, lr, lr_loss, lr_scheduler)
    if len(it)>1000:
      break

  print(lr)
  print(lr_loss)

