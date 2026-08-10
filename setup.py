
from setuptools import setup, Extension
import pybind11
 
ext_modules = [
    Extension(
        "graph_decimate_kernel",
        ["src/structures/graph_decimate_kernel.cpp"],
        include_dirs=[pybind11.get_include()],
        language="c++",
        extra_compile_args=["/O2", "/openmp"],
    ),
]
 
setup(
    name="graph_decimate_kernel",
    ext_modules=ext_modules,
)
 