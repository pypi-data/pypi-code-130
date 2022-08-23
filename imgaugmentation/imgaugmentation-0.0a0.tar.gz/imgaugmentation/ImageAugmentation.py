import os
import cv2
import matplotlib.pyplot as plt
import numpy as np
class ImageAugmentation():
    def __init__(self, X_train, Y_train):
        self.X_train = X_train
        self.Y_train = Y_train
        self.imgList = []
        self.counter = 1

    def dataAugmentation(self, directory, parent_dir, resize='0', rotate=[90,180,270], scale=[1, 1.5, 1], noiseAmt=0.2,
                         noiseSaltvsPepper=0.004,transformavalue=[0.09,0.43,0.56,0.85,0.99,0.32,0.32,0.99], flip=[0,1],
                         kernel=(5,5), translation=[[1, 0, 25], [0, 1, 50]]):
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        final_lst=[]
        if resize != '0':
            self.resizeImg(resize, f'{parent_dir}/{directory}')
        else:
            self.imgToArray()
        final_lst.append(self.imgList)

        for i in range(len(rotate)):
            final_lst.append(self.rotateImg(f'{parent_dir}/{directory}', rotate[i], scale[i]))
        if noiseAmt != 0:
            final_lst.append(self.addNoise('X_train', salt_vs_pepper=noiseSaltvsPepper, amount=noiseAmt, save=f'{parent_dir}/{directory}'))
        if transformavalue:
            final_lst.append(self.transform('X_train', value=transformavalue, save=f'{parent_dir}/{directory}'))
        for i in flip:
            final_lst.append(self.flipImg(f'{parent_dir}/{directory}', i))
        if kernel != 0:
            final_lst.append(self.blurImg(f'{parent_dir}/{directory}', kernel))
        if translation:
            final_lst.append(self.translationImg(f'{parent_dir}/{directory}', translation))
        return final_lst

    def translationImg(self, path, degree):
        lst_y_train = self.Y_train
        i = 0
        imgLst = []
        listImg = os.listdir(self.X_train)
        for imgPath in listImg:
            image = cv2.imread(f'{self.X_train}/{imgPath}')
            M = np.float32(degree)
            image = cv2.warpAffine(image, M, (image.shape[1], image.shape[0]))
            cv2.imwrite(f'{path}/{self.counter}_{imgPath}', image)
            lst_y_train.append(self.Y_train[i])
            i += 1
            self.counter = self.counter + 1
            imgLst.append(image)
        self.Y_train = lst_y_train
        return imgLst

    def blurImg(self, path,kernal=(5,5)):
        lst_y_train = self.Y_train
        i = 0
        imgLst = []
        listImg = os.listdir(self.X_train)
        for imgPath in listImg:
            image = cv2.imread(f'{self.X_train}/{imgPath}')
            image = cv2.blur(image, kernal)
            cv2.imwrite(f'{path}/{self.counter}_{imgPath}', image)
            lst_y_train.append(self.Y_train[i])
            i += 1
            self.counter = self.counter + 1
            imgLst.append(image)
        self.Y_train = lst_y_train
        return imgLst

    def flipImg(self, path, order):
        lst_y_train = self.Y_train
        i = 0
        imgLst = []
        listImg = os.listdir(self.X_train)
        for imgPath in listImg:
            image = cv2.imread(f'{self.X_train}/{imgPath}')
            image = cv2.flip(image, order)
            cv2.imwrite(f'{path}/{self.counter}_{imgPath}', image)
            lst_y_train.append(self.Y_train[i])
            i += 1
            self.counter = self.counter + 1
            imgLst.append(image)
        self.Y_train = lst_y_train
        return imgLst

    def add_salt_pepper_noise(self,X_imgs, salt_vs_pepper, amount):
        # Need to produce a copy as to not modify the original image
        X_imgs_copy = X_imgs.copy()
        row, col, _ = X_imgs_copy.shape

        num_salt = np.ceil(amount * X_imgs_copy[0].size * salt_vs_pepper)
        num_pepper = np.ceil(amount * X_imgs_copy[0].size * (1.0 - salt_vs_pepper))

        for X_img in X_imgs_copy:
            # Add Salt noise
            coords = [np.random.randint(0, i - 1, int(num_salt)) for i in X_img.shape]
            X_img[coords[0], coords[1]] = 1

            # Add Pepper noise
            coords = [np.random.randint(0, i - 1, int(num_pepper)) for i in X_img.shape]
            X_img[coords[0], coords[1]] = 0
        return X_imgs_copy
    def addNoise(self, X_train='X_train', salt_vs_pepper=0.2, amount=0.004, save='X_train'):
        listImg = os.listdir(X_train)
        imgLst=[]
        i=0
        lst_y_train = self.Y_train
        for imgPath in listImg:
            img = cv2.imread(f'{X_train}/{imgPath}')
            img = self.add_salt_pepper_noise(img,salt_vs_pepper, amount)
            cv2.imwrite(f'{save}/{self.counter}_{imgPath}', img)
            self.counter+=1
            lst_y_train.append(self.Y_train[i])
            i+=1
            imgLst.append(img)
        self.Y_train = lst_y_train
        return imgLst

    def getY_trainValue(self):
        print(self.Y_train)
        return self.Y_train

    def imgToArray(self):
        listImg = os.listdir(self.X_train)
        imgList = []
        for imgPath in listImg:
            img = cv2.imread(f'{self.X_train}/{imgPath}')
            imgList.append(img)
        self.imgList = imgList
        return imgList

    def rotateImg(self, path='X_train', degree=90, scale=1):
        # imgList = self.imgToArray()
        angle = degree
        lst_y_train=self.Y_train
        i=0
        imgLst=[]
        listImg = os.listdir(self.X_train)
        imgList = []
        for imgPath in listImg:
            image = cv2.imread(f'{self.X_train}/{imgPath}')
            (h, w, _) = image.shape
            center = (w / 2, h / 2)
            M = cv2.getRotationMatrix2D(center, angle, scale)
            rotated = cv2.warpAffine(image, M, (w, h))
            cv2.imwrite(f'{path}/{self.counter}_{imgPath}', rotated)
            lst_y_train.append(self.Y_train[i])
            i+=1
            self.counter = self.counter+1
            imgLst.append(rotated)
        self.imgList = imgList
        self.Y_train = lst_y_train
        return imgLst

    def resizeImg(self, dimension='30x30',path="X_train"):
        size = dimension.strip().split("x")
        listImg = os.listdir(self.X_train)
        imgList = []
        for imgPath in listImg:
            img = cv2.imread(f'{self.X_train}/{imgPath}')
            img = cv2.resize(img, (int(size[0]), int(size[1])))
            cv2.imwrite(f'{self.X_train}/{imgPath}', img)
            cv2.imwrite(f'{path}/{self.counter}_{imgPath}', img)
            self.counter = self.counter + 1
            imgList.append(img)
        self.imgList = imgList
        return imgList

    def get_mask_coord(self, imshape, value):
        vertices = np.array([[(value[0] * imshape[1], value[4] * imshape[0]),
                              (value[1] * imshape[1], value[5] * imshape[0]),
                              (value[2] * imshape[1], value[6] * imshape[0]),
                              (value[3] * imshape[1], value[7] * imshape[0])]], dtype=np.int32)
        return vertices
    def get_perspective_matrices(self, X_img, value):
        offset = 15
        img_size = (X_img.shape[1], X_img.shape[0])

        # Estimate the coordinates of object of interest inside the image.
        src = np.float32(self.get_mask_coord(X_img.shape, value))
        dst = np.float32([[offset, img_size[1]], [offset, 0], [img_size[0] - offset, 0],
                          [img_size[0] - offset, img_size[1]]])

        perspective_matrix = cv2.getPerspectiveTransform(src, dst)
        return perspective_matrix
    def perspective_transform(self, X_img, value):
        # Doing only for one type of example
        perspective_matrix = self.get_perspective_matrices(X_img,value)
        warped_img = cv2.warpPerspective(X_img, perspective_matrix,
                                         (X_img.shape[1], X_img.shape[0]),
                                         flags=cv2.INTER_LINEAR)
        return warped_img
    def transform(self, X_train='X_train', value=[],save='X_train'):
        listImg = os.listdir(X_train)
        lst_y_train = self.Y_train
        i=0
        imgLst=[]
        for imgPath in listImg:
            img = cv2.imread(f'{X_train}/{imgPath}')
            img=self.perspective_transform(img, value)
            cv2.imwrite(os.path.join(save, f'{self.counter}_{imgPath}'), img)
            lst_y_train.append(self.Y_train[i])
            i += 1
            self.counter+=1
            imgLst.append(img)
        self.Y_train = lst_y_train
        return imgLst

    def showImg(self, final_lst):
        fig, axes = plt.subplots(len(final_lst), len(final_lst[0]), figsize=(8, 6), constrained_layout=True)
        for i in range(len(final_lst)):
            for j in range(len(final_lst[0])):
                axes[i, j].imshow(final_lst[i][j])
        plt.show()