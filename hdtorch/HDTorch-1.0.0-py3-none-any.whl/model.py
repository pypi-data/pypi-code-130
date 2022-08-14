import torch
from . import _hdtorchcuda
from .hyperdimGenerators import generateHDVector
from .util import rotateVec, xor_bipolar


class HD_classifier:
    ''' Base HD classifier with generic parameters and learning and prediction
    funtions '''
    def __init__(self, HDParams):

        self.numFeat      = HDParams.numFeat
        self.D            = HDParams.D
        self.packed       = HDParams.packed
        self.device       = HDParams.device
        self.bindingStrat = HDParams.bindingStrat
        self.HDFlavor     = HDParams.HDFlavor
        
        if self.HDFlavor == 'bipol' and self.packed:
            raise TypeError('Model cannot be bipol and packed simultanously')
            
        if self.bindingStrat == 'FeatAppend':
            self.bindingFunction = lambda d : self.featureLevelValues[d].view(d.shape[0],1,-1)
        elif self.bindingStrat == 'FeatPermute':
            self.bindingFunction = lambda d : rotateVec(self.featureIDs, d)
        elif self.bindingStrat == 'IDLevelEncoding' and self.HDFlavor == 'binary':
            self.bindingFunction = lambda d : torch.bitwise_xor(self.featureIDs.unsqueeze(0), self.featureLevelValues[d])            
        elif self.bindingStrat == 'IDLevelEncoding' and self.HDFlavor == 'bipol' and not self.packed:
            self.bindingFunction = lambda d : xor_bipolar(self.featureIDs.unsqueeze(0), self.featureLevelValues[d])
        else:
            raise TypeError(f'Unrecognized combination of bindingStrat: {self.bindingStrat}, HDFlavor: {self.HDFlavor}, packed: {self.packed}')
        
        self.modelVectors = torch.zeros((HDParams.numClasses, self.D), device=self.device)
        if self.packed:
            self.modelVectorsNorm= torch.zeros((HDParams.numClasses, math.ceil(self.D/32)), device = self.device, dtype=torch.int32)
        else:
            self.modelVectorsNorm= torch.zeros((HDParams.numClasses, self.D), device = self.device, dtype=torch.int8)
            
        self.numAddedVecPerClass = torch.zeros(HDParams.numClasses, device=self.device)
        self.distanceFunction = self.ham_dist_arr if HDParams.similarityType=='hamming' else self.cos_dist_arr 
        
        self.featureIDs = generateHDVector(HDParams.IDVecType,self.numFeat,HDParams.D,self.packed,self.device)
        self.featureIDs[self.featureIDs==0] = -1 if self.HDFlavor=='bipol' else 0
        
        self.featureLevelValues = generateHDVector(HDParams.levelVecType,HDParams.numSegmentationLevels,HDParams.D,self.packed,self.device)
        self.featureLevelValues[self.featureLevelValues==0] = -1 if self.HDFlavor=='bipol' else 0
        
        
    def learn_HD_projections(self, data):
        ''' From features of one window to HDvector representing that data window
        '''
        outputVector = torch.empty((data.shape[0],self.D),dtype = torch.int8, device = data.device)
        if self.packed:
            a = vcount(self.bindingFunction(data),self.D)
        else:
            a = self.bindingFunction(data).sum(1,dtype=torch.int16)
        
        if self.bindingStrat != 'FeatAppend':
            f =  self.numFeat>>1 if self.HDFlavor=='binary' else 0
            torch.gt(a,f,out=outputVector)
        else:
            outputVector = a.to(torch.int8)
        
        if self.HDFlavor == 'bipol':
            outputVector[outputVector==0] = -1

        if self.packed:
            packedOutput = torch.full((data.shape[0],math.ceil(self.D/32)),-1,dtype = torch.int32, device = data.device)
            pack(outputVector,packedOutput)
        else:
            packedOutput = -1

        return outputVector, packedOutput
    
    def ham_dist_arr(self, vec_a, vec_b):
        ''' calculate relative hamming distance for for np array'''
        vec_c = torch.bitwise_xor(vec_a,vec_b) if self.HDFlavor == 'binary' else vec_a != vec_b
        return hcount(vec_c)/float(self.D) if self.packed else vec_c.sum(2,dtype=torch.int16)/float(self.D)
    
    def cos_dist_arr(self, vA, vB):
        ''' calculate cosine distance of two vectors'''
        output = np.dot(vA, vB) / (np.sqrt(np.dot(vA,vA)) * np.sqrt(np.dot(vB,vB)))
        outTensor = torch.tensor(1.0-output) #because we use later that if value is 0 then vectors are the same
        return outTensor
    
    def givePrediction(self,data, encoded=False):
        if not encoded:
            (temp, tempPacked) = self.learn_HD_projections(data)
            temp = temp if not self.packed else tempPacked
            data = temp.view(-1,1,temp.shape[-1])
        else:
            data = data.view(-1,1,data.shape[-1])
        distances = self.distanceFunction(data, self.modelVectorsNorm.unsqueeze(0))
        #find minimum
        minVal = torch.argmin(distances,-1)

        return (minVal.squeeze(), distances.squeeze())
    
    def trainModelVecOnData(self, data, labels):
        '''learn model vectors for single pass 2 class HD learning '''
        # number of clases
        numLabels = self.modelVectors.shape[0]
    
        # Encode data
        (temp, packedTemp) = self.learn_HD_projections(data)
        temp = temp if not self.packed else packedTemp
        
        #go through all data windows and add them to model vectors
        for l in range(numLabels):
            t = temp[labels==l,:]
            if(t.numel() != 0 and self.packed):
                self.modelVectors[l, :] += vcount(temp[labels==l],self.D) #temp[labels==l].sum(0)
            elif not self.packed:
                self.modelVectors[l] += temp[labels==l].sum(0)
            self.numAddedVecPerClass[l] +=  (labels==l).sum().cpu() #count number of vectors added to each subclass
    
        # normalize model vectors to be binary (or bipolar) again
        if self.HDFlavor == 'binary' and self.packed:
                pack(self.modelVectors > (self.numAddedVecPerClass.unsqueeze(1)>>1),self.modelVectorsNorm)
        elif self.HDFlavor == 'binary' and not self.packed:
                self.modelVectorsNorm = self.modelVectors > (self.numAddedVecPerClass.unsqueeze(1)>>1)
        elif self.HDFlavor == 'bipol':
            self.modelVectorsNorm = torch.where(self.modelVectors>0,1,-1)
