import requests
from abc import ABCMeta, abstractmethod
from mplime.mplime import *


class Model(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self):
        self.explainer = None

        
    @abstractmethod
    def evaluate(self, e):
        evaluation, cls = None, None
        return evaluation, cls

    
    def explain_instance(self, x, max_cardinality, mode="super", verbose=False):
        """it returns an explanation of x using MP-LIME

        Args:
            x (List): an explained instance
            max_cardinality (int): the maximum cardinality of a family of minimal patterns
            mode: search mode ("exact", "super", or "disjoint")
            verbose: verbose? (optional, default: False)
        
        Returns:
            List: a family of minimal patterns    
        """

        if mode not in ["exact", "super", "disjoint"]:
            raise ValueError("set mode: exact, super, disjoint")
        
        if self.explainer is None:
            self.explainer = MPLIME(self.evaluate)
        self.explainer.search_minimal_patterns(x, max_cardinality, mode)
        if verbose:
            self.explainer.show()
        
        return self.explainer.minimal_pattern_family
    


class ApiModel(Model):
    def __init__(self, api_url, content_type="application/octet-stream"):
        super(ApiModel, self).__init__()
        self.api_url = api_url
        self.content_type = content_type
        if content_type == "application/octet-stream":
            import pickle as serializer
        elif content_type == "application/json":
            import json as serializer
        else:
            raise ValueError("set application/{octet-stream,json}")
            
        
    def evaluate(self, e):
        payload = {"pattern": e} 
        resp = requests.post(self.api_url,
                             data=serializer.dumps(payload),
                             headers={"Content-Type": self.content_type})
        resp.raise_for_status()
        # if status is 200, raise_for_status returns None
        resp = serializer.loads(resp.content)
        return resp["evaluation"], resp["cls"]

