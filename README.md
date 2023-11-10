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

AI Chat Bot with Plugins (RAG VectorDB - ChromaDB, DuckDuckGo Search, Home Assistant, Vehicle Lookup, YouTube)

[![Build Status](https://drone.va.reichard.io/api/badges/evan/minyma/status.svg)](https://drone.va.reichard.io/evan/minyma)

## Plugins

### ChromeDB Embeddings / Vectors

This utilizes a local embeddings DB. This allows you to ask the assistant
about local information. [Utilizes Retrieval-Augmented Generation (RAG)](https://arxiv.org/abs/2005.11401).

```
User:      What are some common symptoms of COVID-19?
Assistant: Some common symptoms of COVID-19 mentioned in the context are
           fatigue, headache, dyspnea (shortness of breath), anosmia (loss of
           sense of smell), lower respiratory symptoms, cardiac symptoms,
           concentration or memory issues, tinnitus and earache, and peripheral
           neuropathy symptoms.
```

**NOTE:** Instructions on how to load this with your own information are in the
"Normalizing & Loading Data" section. We include a PubMed data normalizer as an
example.

### YouTube

This utilizes `yt-dlp` to download a videos subtitles. Ask questions about YouTube videos!

```
User:      Tell me about this youtube video: https://www.youtube.com/watch?v=ZWgr7qP6yhY
Assistant: The YouTube video you provided is a review of the new MacBook Pro by
           Apple. The host discusses the laptop's features, including its new
           color and chip. They mention that the laptop still retains its ports,
           HDMI, and high-quality display, but also notes some shortcomings like
           the notch and lack of face unlock. The host shares their impressions
           of the new black color [...]
```

### DuckDuckGo

This utilizes DuckDuckGo Search by scraping the top 5 results.

```
User:      Tell me about Evan Reichard
Assistant: Evan Reichard is a Principal Detection and Response Engineer based
           in the Washington DC-Baltimore Area. He has been in this role since
           August 2022. Evan has created a browser extension that helps SOC
           analysts and saves them over 300 hours per month. Additionally,
           there are three professionals named Evan Reichard on LinkedIn and
           there are also profiles of people named Evan Reichard on Facebook.
```

### Vehicle Lookup API

This utilizes Carvana's undocumented API to lookup details on a vehicle.

```
User:      What vehicle is NY plate HELLO?
Assistant: The vehicle corresponding to NY plate HELLO is a 2016 MAZDA CX-5
           Grand Touring Sport Utility 4D with VIN JM3KE4DY6G0672552.
```

### Home Assistant API

This utilizes Home Assistants [Conversational API](https://developers.home-assistant.io/docs/intent_conversation_api/).

```
User:      Turn off the living room lights
Assistant: The living room lights have been turned off. Is there anything else I can assist you with?

User:      Turn on the living room lights
Assistant: The living room lights have been turned on successfully.
```

## Running Server

```bash
# Locally (See "Development" Section)
export OPENAI_API_KEY=`cat openai_key`
export CHROMA_DATA_PATH=/data
export HOME_ASSISTANT_API_KEY=`cat ha_key`
export HOME_ASSISTANT_URL=https://some-url.com

minyma server run

# Docker Quick Start
docker run \
    -p 5000:5000 \
    -e OPENAI_API_KEY=`cat openai_key` \
    -e CHROMA_DATA_PATH=/data \
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
    --normalizer pubmed \
    --database chroma \
    --datapath ./data \
    --filename ./datasets/pubmed_manuscripts.jsonl
```

The above example does the following:

- Uses the `pubmed` normalizer
- Normalizes the `./pubmed_manuscripts.jsonl` raw dataset [0]
- Loads the output into a `chroma` database and persists the data to the `./chroma` directory

**NOTE:** The above dataset took about an hour to normalize on my MPB M2 Max

[0] https://huggingface.co/datasets/TaylorAI/pubmed_author_manuscripts/tree/main

## Configuration

| Environment Variable   | Default Value | Description                         |
| ---------------------- | ------------- | ----------------------------------- |
| OPENAI_API_KEY         | NONE          | Required OpenAI API Key for ChatGPT |
| CHROMA_DATA_PATH       | NONE          | ChromaDB Persistent Data Director   |
| HOME_ASSISTANT_API_KEY | NONE          | Home Assistant API Key              |
| HOME_ASSISTANT_URL     | NONE          | Home Assistant Instance URL         |

# Development

```bash
# Initiate
python3 -m venv venv
. ./venv/bin/activate

# Local Development
pip install -e .

# Creds & Other Environment Variables
export OPENAI_API_KEY=`cat openai_key`

# Docker
make docker_build_local
```
