class ModelPrototype:
    def __model__(self):
        pass


def model(model_prototype: ModelPrototype):
    return model_prototype.__model__()
