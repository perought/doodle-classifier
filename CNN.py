import numpy as np
import matplotlib.pyplot as plt
from matplotlib.image import imread
from DoodleClassifier import *
import pickle
from PIL import Image, ImageGrab, ImageFilter

"""
conv2d
conv1d
pooling
p
fc
softmax
normalize?
"""

classes = {
    0: "airplane", 
    1: "automobile", 
    2: "bird", 
    3: "cat", 
    4: "deer", 
    5: "dog", 
    6: "frog", 
    7: "horse", 
    8: "ship", 
    9: "truck"
}

class CNN(object):
    def __init__(self, layers=[3, 8, 16], f=3):
        self.images = np.zeros(shape=[50000, 32, 32, 3], dtype=float)
        self.labels = np.zeros(shape=[50000], dtype=int)
        self.load_data()
        # self.visualize_data()

        self.batch_size = 16
        self.test_img = self.images[:self.batch_size] / 255. - 0.5
        self.layers = layers[1:]
        self.L = len(layers) - 1
        self.filters = np.array([np.random.rand(layers[x + 1], 3, 3, layers[x]) / 9 for x in range(len(layers) - 1)])
        self.biases = np.array([np.zeros((x, 1, 1)) for x in self.layers])
        print("filter:", self.filters.shape)    # (2,)
        for i in range(self.L):
            print(self.filters[i].shape)    # (8, 3, 3, 3), (16, 3, 3, 8)
        self.conv()
        
        # gaussian_blur_3x3 = np.array([[1, 2, 1], [2, 4, 2], [1, 2, 1]]) / 16
        # sobel = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
        # self.lena(filename="valve.png", Filter=sobel)
    
    def conv(self): # it is "conv2d"
        for l in range(self.L): # first iteration | second iteration
            f = self.filters[l].shape[0]
            h = self.test_img[0].shape[0]
            w = self.test_img[0].shape[1]
            print("h: {}, w: {}".format(h, w))  # h: 32, w: 32 | h: 15, w: 15
            output = np.zeros((self.batch_size, h - 2, w - 2, self.layers[l]))
            print("test_img:", self.test_img.shape) # (16, 32, 32, 3) | (16, 15, 15, 8)
            for i in range(h - 2):
                for j in range(w - 2):
                    for x in range(self.batch_size):
                        output[x, i, j] = np.sum(self.test_img[x, i:i+3, j:j+3] * self.filters[l])
            
            print("output:", output.shape)  # (16, 30, 30, 8) | (16, 13, 13, 16)
            output = self.pooling(output, h - 2, w - 2, self.layers[l])
            print("output:", output.shape)  # (16, 15, 15, 8) | (16, 6, 6, 16)
            self.test_img = self.relu(output, l)
            
        # self.test_img = self.flatten_img(self.test_img)
        self.test_img = self.test_img.reshape(-1, self.batch_size)
        print("test_img:", self.test_img.shape) # (576, 16)
        self.test_img = self.fully_connected()
        print("test_img:", self.test_img.shape) # (10, 16)

    def pooling(self, array, h, w, nc, mode="maxpool", f=2, pad=0, stride=2):
        h_m = int((h + 2 * pad - f) / stride + 1)
        w_m = int((w + 2 * pad - f) / stride + 1)

        pool = np.zeros((self.batch_size, h_m, w_m, nc))

        for i in range(0, h_m + 1, stride):
            for j in range(0, w_m + 1, stride):
                for t in range(self.batch_size):
                    x = int(i / stride)
                    y = int(j / stride)
                    if mode == "maxpool":
                        pool[t, x, y] = np.amax(array[t, i:i+f, j:j+f], axis=(0, 1))
                    elif mode == "mimpool":
                        pool[t, x, y] = np.amin(array[t, i:i+f, j:j+f], axis=(0, 1))
                    elif mode == "averagepool":
                        pool[t, x, y] = np.sum(array[t, i:i+f, j:j+f], axis=(0, 1)) / (f * f)

        return pool

    def fully_connected(self):
        layers = [576, 32, 10]
        biases = np.array([np.zeros((x, 1)) for x in layers[1:]])
        weights = np.array([np.random.randn(layers[x], layers[x - 1]) * np.sqrt(2 / layers[x - 1]) for x in range(1, len(layers))])

        A = self.test_img
        L = len(layers) - 1
        for l in range(L - 1):
            output = self.relu(np.dot(weights[l], A) + biases[l], 0)
            A = output
        z = np.dot(weights[L - 1], A) + biases[L - 1]
        return self.softmax(z - np.max(z))

    def fully_connected_backprop(self):
        pass

    def pooling_backprop(self):
        pass
    
    def conv_backrop(self):
        pass
        
    def relu(self, array, l):
        return np.maximum(array, 0) #  + self.biases[l].T

    def flatten_img(self, array):
        return array.flatten()
        
    def softmax(self, array):
        exps = [np.exp(x) for x in array]
        sum_of_exps = np.sum(exps)
        soft = np.array([x / sum_of_exps for x in exps])
        return soft

    def load_data(self):
        begin = 0
        for i in range(5):
            with open("data/cifar-10-python/data_batch_" + str(i + 1), "rb") as f:
                data = pickle.load(f, encoding="latin1")
                image = data["data"]
                image = image.reshape(10000, 3, 32, 32).transpose(0, 2, 3, 1)
                label = data["labels"]
                end = begin + len(image)
                self.images[begin:end, :] = image
                self.labels[begin:end] = label
                begin = end
    
    def visualize_data(self, row=4, col=4):
        fig, ax = plt.subplots(row, col, figsize=(5, 5))
        fig.tight_layout()

        index = np.random.randint(50000 - row * col)
        for i in range(row):
            for j in range(col):
                ax[i][j].imshow(self.images[index + j + col * i, :].astype("uint8"))
                ax[i][j].set(title=classes[self.labels[index + j + col * i]])
                ax[i][j].axis(False)
        
        plt.show()

    def lena(self, filename="lena.jpg", Filter=None, RGB=True, gray=True):
        """
        Description:
        Applies sobel filter for default arguments
        Reference: https://en.wikipedia.org/wiki/Sobel_operator
        If any filter is given, then sobel operator will not apply to the image.
        Sobel filter or any other filters above works fine

        Arguments:
        Filter: edge, identity, blur or any other filter like:
            sobel = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
            edge1 = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]])
            edge2 = np.array([[1, 0, -1], [0, 0, 0], [-1, 0, 1]])
            identity = np.array([[0, 0, 0], [0, 1, 0], [0, 0, 0]])
            box_blur = np.array([[1, 1, 1], [1, 1, 1], [1, 1, 1]]) / 9
            gaussian_blur_3x3 = np.array([[1, 2, 1], [2, 4, 2], [1, 2, 1]]) / 16
            gaussian_blur_5x5 = np.array([
                    [1,  4,  6,  4, 1], 
                    [4, 16, 24, 16, 4], 
                    [6, 24, 36, 24, 6], 
                    [4, 16, 24, 16, 4],
                    [1,  4,  6,  4, 1]]) / 256
        RGB: input image is form of RGB or grayscale
        gray: output image is form of RGB or grayscale

        Bugs:
        Differences PNG and JPEG images (Found by testing different images, could be wrong):
        plt.imshow arguments vmin and vmax differs. For PNG, vmax is 1, for JPEG vmax is 255
        plt.imshow argument image takes astype("uint8") for PNG bu not for JPEG
        If any of them wrong, displayed image either full black or full white or raises
        "Clipping input data to the valid range for imshow with RGB data ([0..1] for floats or 
        [0..255] for integers)."

        PIL implemetation:
        img = Image.open(filename).convert("L")
        edge = img.filter(ImageFilter.FIND_EDGES)
        edge.show()
        """
        
        PNGorJPG = filename.find(".png")

        img = imread(filename)
        if not RGB:
            img = self.rgb2gray(img)

        h, w = img.shape[0], img.shape[1]
        img = self.gaussian_filter(img, h, w, RGB=RGB)         # remove noise
        img = self.convolution_filter(img, h, w, Filter=Filter, RGB=RGB) # apply sobel filter for RGB or grayscale images
        
        if gray:
            if RGB:
                img = self.rgb2gray(img)
            if PNGorJPG != -1:  # PNG image is given
                plt.imshow(img, cmap="gray", vmin=0, vmax=1)    # vmin,vmax: 0-1 or 0-255?
            if PNGorJPG == -1:  # JPG image is given
                plt.imshow(img, cmap="gray", vmin=0, vmax=255)    # vmin,vmax: 0-1 or 0-255?
        else:
            if PNGorJPG != -1:  # PNG image is given
                plt.imshow(img)
            if PNGorJPG == -1:  # JPG image is given
                plt.imshow(img.astype("uint8"))
        plt.axis(False)
        plt.show()

    def convolution_filter(self, img, h, w, f=3, pad=1, stride=1, Filter=None, RGB=True, remove_noise=False):
        if Filter is not None:
            f = Filter.shape[0]
        h_c = int((h + 2 * pad - f) / stride + 1)
        w_c = int((w + 2 * pad - f) / stride + 1)

        if RGB:
            Rc = np.zeros((h_c, w_c))
            Gc = np.zeros((h_c, w_c))
            Bc = np.zeros((h_c, w_c))

            R = np.pad(img[:,:,0], ((pad, pad), (pad, pad)), "constant", constant_values=0)
            G = np.pad(img[:,:,1], ((pad, pad), (pad, pad)), "constant", constant_values=0)
            B = np.pad(img[:,:,2], ((pad, pad), (pad, pad)), "constant", constant_values=0)
        else:
            Grayc = np.zeros((h_c, w_c))
            Gray = np.pad(img[:,:], ((pad, pad), (pad, pad)), "constant", constant_values=0)

        if not remove_noise:
            Gx = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
            Gy = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]])

        for i in range(h_c):
            for j in range(w_c):
                if RGB and remove_noise or Filter is not None and RGB:
                    Rc[i, j] = np.sum(R[i:i+f, j:j+f] * Filter)
                    Gc[i, j] = np.sum(G[i:i+f, j:j+f] * Filter)
                    Bc[i, j] = np.sum(B[i:i+f, j:j+f] * Filter)

                elif RGB and not remove_noise:
                    r = R[i:i+f, j:j+f]
                    S1 = np.sum((Gx * r))
                    S2 = np.sum((Gy * r))
                    Rc[i, j] = np.sqrt(np.power(S1, 2) + np.power(S2, 2))

                    g = G[i:i+f, j:j+f]
                    S1 = np.sum((Gx * g))
                    S2 = np.sum((Gy * g))
                    Gc[i, j] = np.sqrt(np.power(S1, 2) + np.power(S2, 2))

                    b = B[i:i+f, j:j+f]
                    S1 = np.sum((Gx * b))
                    S2 = np.sum((Gy * b))
                    Bc[i, j] = np.sqrt(np.power(S1, 2) + np.power(S2, 2))

                elif not RGB and remove_noise or Filter is not None and not RGB:
                    Grayc[i, j] = np.sum(Gray[i:i+f, j:j+f] * Filter)

                elif not RGB and not remove_noise:
                    gray = Gray[i:i+f, j:j+f]
                    S1 = np.sum((Gx * gray))
                    S2 = np.sum((Gy * gray))
                    Grayc[i, j] = np.sqrt(np.power(S1, 2) + np.power(S2, 2))
        
        if RGB:
            return np.dstack((Rc, Gc, Bc))
        else:
            return Grayc
    
    def gaussian_filter(self, img, h, w, RGB=True):
        Filter = np.array([
            [2,  4,  5,  4, 2], 
            [4,  9, 12,  9, 4], 
            [5, 12, 15, 12, 5], 
            [4,  9, 12,  9, 4], 
            [2,  4,  5,  4, 2], 
        ]) / 159

        return self.convolution_filter(img, h, w, f=5, pad=2, Filter=Filter, RGB=RGB, remove_noise=True)
    
    def normalize(self, img):
        Max = img.max()
        Min = img.min()

        img = (img - Min) / (Max - Min)

        return img

    def rgb2gray(self, img):
        return np.dot(img[...,:3], [0.2989, 0.5870, 0.1140])


if __name__ == '__main__':
    CNN()
