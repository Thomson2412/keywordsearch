from setuptools import setup

setup(
    name='keywordsearch',
    version='0.8',
    packages=[''],
    install_requires=[
        'deepspeech',
        'deepspeech-gpu',
        'librosa',
        'numpy',
        'pyglet'
    ],
    author='Thomas Fink',
)
