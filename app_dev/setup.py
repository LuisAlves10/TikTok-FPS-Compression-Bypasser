from pathlib import Path

from Cython.Build import cythonize
from setuptools import Extension, find_packages, setup


ROOT = Path(__file__).parent


extensions = [
    Extension(
        name="tiktok_fps_bypasser.secure_core",
        sources=[str(ROOT / "tiktok_fps_bypasser" / "secure_core.pyx")],
    )
]


setup(
    name="tiktok-fps-compression-bypasser",
    version="1.0.0",
    description="Protected Windows build for the TikTok FPS Compression Bypasser",
    packages=find_packages(exclude=("build_tools", "dist", "build")),
    ext_modules=cythonize(
        extensions,
        compiler_directives={
            "language_level": "3",
            "boundscheck": False,
            "wraparound": False,
            "initializedcheck": False,
            "nonecheck": False,
        },
    ),
    include_package_data=True,
    zip_safe=False,
)
