<p align="center">
    <img src="https://gitea.va.reichard.io/evan/minyma/raw/branch/master/resources/logo.png" width="300">
</p>

<p align="center">
    <a href="https://gitea.va.reichard.io/evan/minyma/raw/branch/master/resources/loading.png">
        <img src="https://gitea.va.reichard.io/evan/minyma/raw/branch/master/resources/loading.png" width="49%">
    </a>
    <a href="https://gitea.va.reichard.io/evan/minyma/raw/branch/master/resources/response.png">
        <img src="https://gitea.va.reichard.io/evan/minyma/raw/branch/master/resources/response.png" width="49%">
    </a>
</p>

---

AI Chat Bot with Vector / Embedding DB Context

[![Build Status](https://drone.va.reichard.io/api/badges/evan/minyma/status.svg)](https://drone.va.reichard.io/evan/minyma)

## Running Server

```bash
# Locally (See "Development" Section)
export OPENAI_API_KEY=`cat openai_key`
minyma server run

# Docker Quick Start
docker run \
    -p 5000:5000 \
    -e OPENAI_API_KEY=`cat openai_key` \
    -e DATA_PATH=/data \
    -v ./data:/data \
    gitea.va.reichard.io/evan/minyma:latest
```

The server will now be accessible at `http://localhost:5000`

## Normalizing & Loading Data

Minyma is designed to be extensible. You can add normalizers and vector db's
using the appropriate interfaces defined in `./minyma/normalizer.py` and
`./minyma/vdb.py`. At the moment the only supported database is `chroma`
and the only supported normalizer is the `pubmed` normalizer.

To normalize data, you can use Minyma's `normalize` CLI command:

```bash
minyma normalize \
    --filename ./pubmed_manuscripts.jsonl \
    --normalizer pubmed \
    --database chroma \
    --datapath ./chroma
```

The above example does the following:

- Uses the `pubmed` normalizer
- Normalizes the `./pubmed_manuscripts.jsonl` raw dataset [0]
- Loads the output into a `chroma` database and persists the data to the `./chroma` directory

**NOTE:** The above dataset took about an hour to normalize on my MPB M2 Max

[0] https://huggingface.co/datasets/TaylorAI/pubmed_author_manuscripts/tree/main

## Configuration

| Environment Variable | Default Value | Description                                                                        |
| -------------------- | ------------- | ---------------------------------------------------------------------------------- |
| OPENAI_API_KEY       | NONE          | Required OpenAI API Key for ChatGPT access.                                        |
| DATA_PATH            | ./data        | The path to the data directory. Chroma will store its data in the `chroma` subdir. |

# Development

```bash
# Initiate
python3 -m venv venv
. ./venv/bin/activate

# Local Development
pip install -e .

# Creds
export OPENAI_API_KEY=`cat openai_key`

# Docker
make docker_build_local
```

# Notes

This is the first time I'm doing anything LLM related, so it was an adventure.
Initially I was entertaining OpenAI's Embedding API with plans to load embeddings
into Pinecone, however initial calculations with `tiktoken` showed that generating
embeddings would cost roughly $250 USD.

Fortunately I found [Chroma](https://www.trychroma.com/), which basically solved
both of those issues. It allowed me to load in the normalized data and automatically
generated embeddings for me.

In order to fit into OpenAI ChatGPT's token limit, I limited each document to roughly
1000 words. I wanted to make sure I could add the top two matches as context while
still having enough headroom for the actual question from the user.

A few notes:

- Context is not carried over from previous messages
- I "stole" the prompt that is used in LangChain (See `oai.py`). I tried some variations without much (subjective) improvement.
- A generalized normalizer format. This should make it fairly easy to use completely different data. Just add a new normalizer that implements the super class.
- Basic web front end with TailwindCSS
