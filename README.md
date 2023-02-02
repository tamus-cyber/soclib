<img src="./soclib_logo.png" width=128/>

# 🚀 soclib 🚀

This collection of libraries is designed to be used in various SOC applications. We've included most of our common tools and services to make your job easier and more efficient.

## Contents

### 🔍 Reputation Services

- Alienvault OTX
- Cisco Umbrella

### ![Vectra logo](./vectra_logo.png) Vectra API libraries

- Vectra client for [vectra-api](https://github.com/tamus-cyber/vectra-api)
- ElasticVectra for sending logs to ELK

### 🔧 SOC Tools

- IOC enrichment
- URL defanger
- Stakeholder IP lookup
- TAMU directory search
- Quick links generator
- IP geolocation lookup

### 🌐 Web Services

- Website screenshot grabber
- Website description lookup

### Logging

- Elasticsearch
- Slack

### 🤷‍♂️ Miscellaneous

- Linux display session checker

We've also made sure to leave out some tools that might be better suited for separate repos, like case management libraries (Jira, ELK, etc.) and Prometheus exporters.

To ensure the quality of our libraries, we use Pytest for unit testing. Be sure to check out our [TESTING.md](./TESTING.md) for more information.

Thanks for choosing soclib! We hope it makes your SOC work a little bit easier. 💪

## Setup

### Requirements

Install the Python pip modules from `requirements.txt` using:

```bash
pip3 install -r ./requirements.txt
```

### Environment Variables

You will need to set the following environment variables. This can also be done using a `.env` file.

```bash
# Slack
SLACK_ALERT_LEVEL=
SLACK_TOKEN=
SLACK_CHANNEL=

# JIRA
JIRA_USERNAME=
JIRA_TOKEN=
JIRA_PROJECT_KEY=

# Vectra
VECTRA_API_URL=
TEST_STAKEHOLDER=
TEST_DETECTION_ID=
TEST_HOST_ID=
VECTRA_TIMEOUT=[seconds]

# Vectra (Production only)
AZURE_CLIENT_ID=
AZURE_TENANT_ID=
AZURE_CLIENT_SECRET=

# Reputation Services
UMBRELLA_API_KEY=
OTX_API_KEY=

# SOC DB
DB_USER=
DB_HOST_IP=
DB_PORT=
DB_PASS=
READ_ONLY=TRUE
DB_NAME=
```
