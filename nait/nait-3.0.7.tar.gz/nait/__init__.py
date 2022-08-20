# Nait 3.0.7


"""
A module that provides functions and classes for 
creating and training neural networks.

Nait 3.0.7

https://pypi.org/project/nait/
"""


import random
import types
import copy
import json
import math
import time


class Model():
    
    """
    Model(layers)
    Nait 3.0.7

    https://pypi.org/project/nait/
    """

    def __str__(self):

        return "Model(\n  " + ",\n  ".join([layer.__str__() for layer in self.layers]) + "\n)"

    def __init__(self, layers):

        self.layers = layers

    def _predict(self, layers, inputs):

        outputs = inputs
        for layer in layers:
            outputs = layer.forward(outputs)

        return outputs

    def _loss(self, outputs, y): return sum([(outputs[i] - y[i]) ** 2 for i in range(len(outputs))])
    def _unsquared_loss(self, outputs, y): return sum([abs(outputs[i] - y[i]) for i in range(len(outputs))])

    def _evaluate(self, layers, x, y): return sum([self._loss(self._predict(layers, x[i]), y[i]) for i in range(len(x))])
    def _unsquared_evaluate(self, layers, x, y): return sum([self._unsquared_loss(self._predict(layers, x[i]), y[i]) for i in range(len(x))])

    def train(self, x=[], y=[], epochs=5000, rate=1, batch_size=10, sample_size=None, square_loss=True, visual=True, loss_function=None):

        """
        train(x=[], y=[], epochs=5000, rate=1, batch_size=10, sample_size=None, square_loss=True, visual=True, loss_function=None)
        Nait 3.0.7

        https://pypi.org/project/nait/
        """

        assert len(x) == len(y)

        if loss_function == None:
            start_loss = self._unsquared_evaluate(self.layers, x, y)
        else:
            start_loss = loss_function(self, x, y)
        start_time = time.time()
        rate /= (10**3)

        length, filled, empty = 32, "■", "."

        print(f"[{empty * length}] - 0.0% - epoch: 0/{epochs} - _s - loss: {start_loss}" + " " * 18, end="\r")
        
        interrupted = False
        
        try:

            for epoch in range(1, epochs + 1):

                batch = []

                for _ in range(batch_size):
                    batch.append(copy.deepcopy(self).mutate(rate))

                batch.append(self.layers)

                if loss_function == None:

                    x_sample = x
                    y_sample = y

                    if sample_size != None:
                        x_sample = random.sample(x, sample_size)
                        y_sample = [y[x.index(inputs)] for inputs in x_sample]

                    if square_loss:
                        losses = [self._evaluate(layers, x_sample, y_sample) for layers in batch]
                    else:
                        losses = [self._unsquared_evaluate(layers, x_sample, y_sample) for layers in batch]
                        
                    self.layers = batch[losses.index(min(losses))]

                    visual_loss = self._unsquared_evaluate(self.layers, x, y)

                else:

                    losses = []

                    for layers in batch:
                        temp_model = Model([])
                        temp_model.layers = layers

                        losses.append(loss_function(temp_model, x, y))

                    self.layers = batch[losses.index(min(losses))]

                    visual_loss = min(losses)

                if visual:

                    remaining = math.ceil(((time.time() - start_time) / epoch) * (epochs - epoch))
                    unit = "s"

                    if remaining >= 60:
                        remaining //= 60
                        unit = "m"

                    progress = (epoch * length) // epochs

                    print(f"[{filled * progress}{empty * (length - progress)}] - {round(epoch / epochs * 100, 1)}% - epoch: {epoch}/{epochs} - {remaining}{unit} - loss: {visual_loss}" + " " * 18, end="\r")

        except KeyboardInterrupt:

            interrupted = True

        if visual:

            end_time = math.floor(time.time() - start_time)
            unit = "s"

            if end_time >= 60:
                end_time //= 60
                unit = "m"

            if interrupted == False: 
                print(f"[{filled * length}] - 100.0% - epoch: {epochs}/{epochs} - 0s - loss: {visual_loss}" + " " * 18)
                
            else: 
                print("\ntraining interrupted")

            print(f"improvement: {start_loss - visual_loss} ({round((start_loss - visual_loss) / start_loss * 100, 2)}%) - time: {end_time}{unit}")

        return visual_loss

    def predict(self, inputs):
        
        """
        predict(inputs)
        Nait 3.0.7

        https://pypi.org/project/nait/
        """

        return self._predict(self.layers, inputs)

    def mutate(self, rate):
        
        """
        mutate(rate)
        Nait 3.0.7

        https://pypi.org/project/nait/
        """
        
        rates = [rate*2, rate, rate/2]

        rate = random.choice(rates)

        return [layer.mutate(rate) for layer in self.layers]


class Layer():
    
    """
    Layer(inputs=4, neurons=4, activation="linear")
    Nait 3.0.7
    
    https://pypi.org/project/nait/
    """

    def __str__(self):

        return "Layer(" + ", ".join([layer.__str__() for layer in self.neurons]) + ", '" + str(self.activation.function) + "')"

    def __init__(self, inputs=4, neurons=4, activation="linear"):

        self.neurons = [Neuron([0 for _ in range(inputs)], 0) for _ in range(neurons)]
        self.activation = Activation(activation)

    def forward(self, inputs):
        
        """
        forward(inputs)
        Nait 3.0.7
        
        https://pypi.org/project/nait/
        """

        return [self.activation.calculate(neuron.parse(inputs)) for neuron in self.neurons]

    def mutate(self, rate):
        
        """
        mutate(rate)
        Nait 3.0.7
        
        https://pypi.org/project/nait/
        """

        mutated_layer = copy.deepcopy(self)
        mutated_layer.neurons = [neuron.mutate(rate) for neuron in mutated_layer.neurons]

        return mutated_layer


class Neuron():
    
    """
    Neuron(weights, bias)
    Nait 3.0.7
    
    https://pypi.org/project/nait/
    """

    def __str__(self):

        text = "Neuron([" + ", ".join([str(round(weight, 1)) if round(weight, 1) != weight else str(weight) for weight in self.weights]) + "], "
        text += str(round(self.bias, 1)) if round(self.bias, 1) != self.bias else str(self.bias)
        text += ")"

        return text

    def __init__(self, weights, bias):

        self.weights = weights
        self.bias = bias

    def parse(self, inputs):
        
        """
        parse(inputs)
        Nait 3.0.7
        
        https://pypi.org/project/nait/
        """

        return sum([inputs[i] * self.weights[i] for i in range(len(inputs))]) + self.bias

    def mutate(self, rate):
        
        """
        mutate(rate)
        Nait 3.0.7
        
        https://pypi.org/project/nait/
        """

        weights = [self.weights[i] + random.uniform(rate, -rate) for i in range(len(self.weights))]
        bias = self.bias + random.uniform(rate, -rate)

        return Neuron(weights, bias)


class Activation():
    
    """
    Activation(function)
    Nait 3.0.7
    
    https://pypi.org/project/nait/
    """

    def __init__(self, function):

        self.function = function

    def calculate(self, x):
        
        """
        calculate(x)
        Nait 3.0.7
        
        https://pypi.org/project/nait/
        """

        if self.function.lower() == "linear": return x
        elif self.function.lower() == "step": return 1 if x > 0 else 0
        elif self.function.lower() == "relu": return max(0, x)
        elif self.function.lower() == "tanh": return math.tanh(x)
        elif self.function.lower() == "hardmax": return min(max(x, 0), 1)
        elif self.function.lower() == "sigmoid": return 1 / (1 + math.exp(-x))
        elif self.function.lower() == "softmax": return 1 / (1 + math.exp(-x))
        elif self.function.lower() == "leaky relu": return x if x > 0 else x * 0.1
        else: raise ValueError(f"Invalid activation function '{self.function}'")


def evaluate(model, x, y, squared=False):
    
    """
    evaluate(model, x, y)
    Nait 3.0.7

    https://pypi.org/project/nait/
    """
    
    if squared:
        return model._evaluate(x, y)
    else:
        return model._unsquared_evaluate(x, y)


def save(model, path):
    
    """
    save(model, path)
    Nait 3.0.7

    https://pypi.org/project/nait/
    """

    with open(path, "w") as file:
        file.write(json.dumps({"layers": [{"neurons": [[neuron.weights, neuron.bias] for neuron in layer.neurons], "activation": layer.activation.function} for layer in model.layers]}))


def load(path):
    
    """
    load(path)
    Nait 3.0.7

    https://pypi.org/project/nait/
    """
    
    with open(path, "r") as file:
        data = json.loads(file.read())

    layers = []

    for layer_data in data["layers"]:
        layer = Layer()
        layer.neurons = [Neuron(neuron_data[0], neuron_data[1]) for neuron_data in layer_data["neurons"]]
        layer.activation = Activation(layer_data["activation"])
        layers.append(layer)

    model = Model(layers)

    return model