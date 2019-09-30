# Miminal Patterns LIME
This is an implementation of [Minimal Patterns LIME](https://doi.org/10.1007/978-3-030-30487-4_19).


# How to Install 
```sh
# in your python enviroment
$ python setup.py install
```
python 3.6 or higher.


# How to Use
See `test/` and `examples/`.
1. You must impement a function $f: 2^{d} \to \mathcal{C}$ that returns the evaluation 
and the class with an input instance $x\in 2^{d}$. 
```py
from mplime import model
model.explain_instance(x) # <- you must implement this function.
```


# ToDo
Add more documents.


(C) Kohei Asano
