'''
Created on May 11, 2022

@author: wsimon
'''
import os, math
import torch

def func_generateVectorsMemory_Random(numClasses, HD_dim):
    ''' function to generate matrix of HD vectors using random method
        random - each vector is independantly randomly generated
    '''
    return torch.randint(0,2,(numClasses, HD_dim))

def func_generateVectorsMemory_Sandwich(numClasses, HD_dim):
    ''' function to generate matrix of HD vectors using sandwich method
    sandwich - every two neighbouring vectors have half of the vector the same, but the rest of the vector is random
    '''

    vect_matrix = torch.zeros(numClasses, HD_dim)
    for i in range(numClasses):
        if i % 2 == 0:
            vect_matrix[i, :] = torch.randint(0,2,HD_dim)
    for i in range(numClasses - 1):
        if i % 2 == 1:
            vect_matrix[i, 0:int(HD_dim / 2)] = vect_matrix[i - 1, 0:int(HD_dim / 2)]
            vect_matrix[i, int(HD_dim / 2):HD_dim] = vect_matrix[i + 1, int(HD_dim / 2):HD_dim]
    vect_matrix[numClasses - 1, 0:int(HD_dim / 2)] = vect_matrix[numClasses - 2, 0:int(HD_dim / 2)]
    vect_matrix[numClasses - 1, int(HD_dim / 2):HD_dim] = torch.randn(int(HD_dim / 2))
    vect_matrix = vect_matrix>0 
    return vect_matrix

def func_generateVectorsMemory_ScaleRand(numClasses, HD_dim, scaleFact):
    ''' function to generate matrix of HD vectors using scale method with bits of randomization
    scaleRand - every next vector is created by randomly flipping D/(numVec*scaleFact) elements - this way the further values vectors represent are, the less similar are vectors
    '''

    numValToFlip=floor(HD_dim/(scaleFact*numClasses))

    vect_matrix = torch.zeros(numClasses, HD_dim)
    #generate first one as random
    vect_matrix[0, :] = torch.randint(0,2,HD_dim)
    #iteratively the further they are flip more bits
    for i in range(1,numClasses):
        vect_matrix[i, :]=vect_matrix[i-1, :]
        #choose random positions to flip
        posToFlip=random.sample(range(1,HD_dim),numValToFlip)
        vect_matrix[i,posToFlip] = 1-vect_matrix[i,posToFlip]
    return vect_matrix

    

def func_generateVectorsMemory_ScaleNoRand(numClasses, HD_dim, scaleFact):
    ''' function to generate matrix of HD vectors  using scale method with no randomization
    scaleNoRand - same idea as scaleRand, just  d=D/(numVec*scaleFact) bits are taken in order (e.g. from i-th to i+d bit) and not randomly
    '''
    numValToFlip = math.floor(HD_dim / (scaleFact * numClasses))

    # initialize vectors
    vect_matrix = torch.randint(0,2,(numClasses, HD_dim)).to(torch.int8)
    
    # iteratively the further they are flip more bits
    for i in range(1, numClasses):
        vect_matrix[i] = vect_matrix[0]
        vect_matrix[i, 0: i * numValToFlip] = 1 - vect_matrix[0, 0: i * numValToFlip]
    
    return vect_matrix
    
def generateHDVector(vecType, numVec, HDDim, packed, device):
    if vecType == 'sandwich':
        hdVec = func_generateVectorsMemory_Sandwich(numVec, HDDim)
    elif vecType == 'random':
        hdVec = func_generateVectorsMemory_Random(numVec, HDDim)
    elif "scaleNoRand" in vecType:
        hdVec = func_generateVectorsMemory_ScaleNoRand(numVec, HDDim, int(vecType[11:]))
    elif "scaleRand" in vecType:
        hdVec = func_generateVectorsMemory_ScaleRand(numVec, HDDim, int(vecType[9:]))
    else:
        raise TypeError(f'Unrecognized vecType {vecType}')
        
    if not packed:
        return hdVec.to(device).to(torch.int8)
    else:
        hdVecPacked = torch.zeros((numVec,math.ceil(HDDim/32)),dtype=torch.int32,device=device)
        pack(hdVec.to(device).to(torch.int8),hdVecPacked)
        return hdVecPacked
    