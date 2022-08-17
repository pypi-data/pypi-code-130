from src.mdrunner import Model
from enum import Enum, auto


class ModelType(Enum):
    In = auto()
    A = auto()
    B = auto()
    C = auto()
    Out = auto()


class In1(Model):
    model_type = ModelType.In

    def init(self):
        """This model is expecting external input data from
        runner.add(params, <this_model>)"""
        pass

    def run(self):
        self.add(name='x', val=self.p1 * self.p2)


class In2(Model):
    model_type = ModelType.In

    def init(self):
        """This model is expecting external input data from
         runner.add(params, <this_model>)"""
        pass

    def run(self):
        """external inputs will end up as model params"""
        pass


class In3(Model):
    model_type = ModelType.In

    def init(self):
        """This model is expecting external input data from
         runner.add(params, <this_model>)"""
        self.push(ModelType.Out)
        pass

    def run(self):
        """external inputs will end up as model params"""
        pass


class A1(Model):
    model_type = ModelType.A

    def init(self):
        self.get(ModelType.In)

    def run(self):
        self.add(name='x', val=self.In.p1 * self.In.p2)


class A2(Model):
    model_type = ModelType.A

    def init(self):
        self.get(ModelType.In)
        self.push(ModelType.Out)

    def run(self):
        self.add(name='x', val=self.In.p1 * self.In.p2)


class B1(Model):
    model_type = ModelType.B

    def init(self):
        self.get(ModelType.In)
        self.get(ModelType.A)
        pass

    def run(self):
        self.add(name='x', val=self.A.x * self.In.p3)


class B2(Model):
    model_type = ModelType.B

    def init(self):
        self.get(ModelType.In)
        self.get(ModelType.A)
        self.push(ModelType.Out)
        pass

    def run(self):
        self.add(name='x', val=self.A.x * self.In.p3)


class B3(Model):
    model_type = ModelType.B

    def init(self):
        self.get(ModelType.In)
        self.get(ModelType.A)
        self.push(ModelType.Out)

    def run(self):
        self.add(name='x', val=self.In.x + self.A.x)


class C3(Model):
    model_type = ModelType.C

    def init(self):
        self.get(ModelType.In)
        self.get(ModelType.A)
        self.get(ModelType.B)
        self.push(ModelType.Out)

    def run(self):
        self.add(name='x', val=self.In.x + self.A.x + self.B.x)



class Out1(Model):
    model_type = ModelType.Out

    def init(self):
        """we are expecting other models to send params to us"""
        pass

    def run(self):
        # find the total value of all pushed x values
        x = 0.0
        for model in self.pushed_models:
            if 'x' in model._params:
                x += model.x
        self.add(name='x', val=x)
