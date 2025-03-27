from setuptools import setup, find_packages

setup(
    name='vgc2',
    version='1.0.4',
    description='The VGC AI Framework emulates the Video Game Championships of Pokémon with AI Trainer agents.',
    url='https://gitlab.com/DracoStriker/pokemon-vgc-engine',
    author='Simão Reis',
    author_email='simao.reis@vortex-colab.com, simao.reis@outlook.pt',
    license='MIT License',
    packages=find_packages(),
    include_package_data=True,
    install_requires=['gymnasium~=1.0.0', 'numpy~=2.2.2', 'setuptools~=75.8.0'],
    classifiers=[
        'Development Status :: 2 - Development',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.10.12',
    ],
)
