#!/bin/sh
conda install pip
pip install -r requirements.txt
pip install -U bitsandbytes
pip install -U git+https://github.com/huggingface/transformers.git
pip install -U git+https://github.com/huggingface/accelerate.git
pip install -q datasets loralib sentencepiece
pip install git+https://github.com/csebuetnlp/normalizer

touch ./hf_token.txt
mkdir ./DataProcessor/logs
mkdir ./Data/
mkdir ./Data/Prompts


