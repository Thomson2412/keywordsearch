from setuptools import setup

setup(
    name='keywordsearch',
    version='0.8',
    packages=[''],
    install_requires=[
        'librosa',
        'numpy',
        'pydub',
        'pyaudio'
    ],
    extras_require={
        'gpu': ['deepspeech-gpu'],
        'cpu': ['deepspeech']
    },
    author='Thomas Fink',
)
