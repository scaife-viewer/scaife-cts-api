# Scaife CTS API

This repository contains the implementation of Nautilus CND for the Scaife Viewer. The project contains a Dockerfile, Kubernetes config and a Python script to load data from CapiTainS guidelined repos.

This repository is part of the [Scaife Viewer](https://scaife-viewer.org) project, an open-source ecosystem for building rich online reading environments.

## Operations
### Updating the scaife.perseus.org deployment

- Update `corpus.json` with the latest releases from GitHub:
```shell
export GITHUB_ACCESS_TOKEN=<token>
python scaife_cts_api/update_corpus_shas.py
```
- Open a new pull request with the changes
