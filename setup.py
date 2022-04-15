from setuptools import setup

setup(
    name='keywordsearch',
    version='0.8',
    packages=[''],
    install_requires=[
        'deepspeech-gpu',
        'librosa',
        'webrtcvad',
        'numpy'
    ],
    author='Thomas Fink',
)
