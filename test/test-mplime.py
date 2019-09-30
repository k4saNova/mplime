
from mplime import Model
from random import random
from functools import reduce
from operator import mul


class SynthesisLinearModel(Model):
    def __init__(self, d):
        super(SynthesisLinearModel, self).__init__()
        self.w = [random()-0.5 for i in range(d)]
        print("weight: [" + ", ".join([f"{wi:.4f}" for wi in self.w]) + "]")
        y = sum(self.w)
        cls = 0 if y > 0 else 1
        print(f"y, cls = {y:.4f}, {cls}", end="\n\n")

        
    def evaluate(self, e):
        y = sum([self.w[i] for i in e])
        cls = 0 if y > 0 else 1
        return abs(y), cls


class SynthesisRuleModel(Model):
    def __init__(self):
        super(SynthesisRuleModel, self).__init__()
        self.rules = [[0,1], [2], [1,3], [3,4,5], [1,8], [7,9]]
        # self.rules = [[0,1], [1,2], [2,3], [3,0], [4]]
        
    def evaluate(self, e):
        cls = sum([reduce(mul,
                          [1 if elm in e else 0 for elm in rule])
                   for rule in self.rules])
        return 1, min(1, cls)
        # return random(), min(1, cls)
        
    
def test_linear_model():
    e = list(range(10))
    model = SynthesisLinearModel(len(e))
    print("super")
    model.explain_instance(e, 10, mode="super", verbose=True)
    print("disjoint")
    model.explain_instance(e, 10, mode="disjoint", verbose=True)
    print("exact")
    model.explain_instance(e, 10, mode="disjoint", verbose=True)

    
def test_rule_model():
    e = list(range(10))
    model = SynthesisRuleModel()
    print("super")
    model.explain_instance(e, 10, mode="super", verbose=True)
    print("disjoint")
    model.explain_instance(e, 10, mode="disjoint", verbose=True)
    print("exact")
    model.explain_instance(e, 10, mode="exact", verbose=True)
        
        
if __name__ == "__main__":
    # test_linear_model()
    test_rule_model()
