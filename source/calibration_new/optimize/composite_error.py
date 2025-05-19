class CompositeError:
    def __init__(self, terms):
        self.terms = terms

    def compute(self, camera, data):
        return sum(weight * err.compute(camera, data) for err, weight in self.terms)
