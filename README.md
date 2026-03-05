# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/oemof/oemof-network/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                      |    Stmts |     Miss |   Branch |   BrPart |      Cover |   Missing |
|------------------------------------------ | -------: | -------: | -------: | -------: | ---------: | --------: |
| src/oemof/network/\_\_init\_\_.py         |       14 |        0 |        0 |        0 |    100.00% |           |
| src/oemof/network/energy\_system.py       |       98 |        1 |       34 |        1 |     98.48% |       244 |
| src/oemof/network/graph.py                |       26 |        1 |       18 |        1 |     95.45% |       120 |
| src/oemof/network/groupings.py            |       69 |        5 |       28 |        2 |     90.72% |180-182, 217, 221 |
| src/oemof/network/network/\_\_init\_\_.py |        9 |        0 |        0 |        0 |    100.00% |           |
| src/oemof/network/network/edge.py         |       43 |        1 |       12 |        2 |     94.55% |107, 117->exit |
| src/oemof/network/network/entity.py       |       27 |        0 |        2 |        0 |    100.00% |           |
| src/oemof/network/network/helpers.py      |       27 |        1 |        0 |        0 |     96.30% |        40 |
| src/oemof/network/network/nodes.py        |      100 |        1 |       22 |        1 |     98.36% |       231 |
| **TOTAL**                                 |  **413** |   **10** |  **116** |    **7** | **96.41%** |           |


## Setup coverage badge

Below are examples of the badges you can use in your main branch `README` file.

### Direct image

[![Coverage badge](https://raw.githubusercontent.com/oemof/oemof-network/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/oemof/oemof-network/blob/python-coverage-comment-action-data/htmlcov/index.html)

This is the one to use if your repository is private or if you don't want to customize anything.

### [Shields.io](https://shields.io) Json Endpoint

[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/oemof/oemof-network/python-coverage-comment-action-data/endpoint.json)](https://htmlpreview.github.io/?https://github.com/oemof/oemof-network/blob/python-coverage-comment-action-data/htmlcov/index.html)

Using this one will allow you to [customize](https://shields.io/endpoint) the look of your badge.
It won't work with private repositories. It won't be refreshed more than once per five minutes.

### [Shields.io](https://shields.io) Dynamic Badge

[![Coverage badge](https://img.shields.io/badge/dynamic/json?color=brightgreen&label=coverage&query=%24.message&url=https%3A%2F%2Fraw.githubusercontent.com%2Foemof%2Foemof-network%2Fpython-coverage-comment-action-data%2Fendpoint.json)](https://htmlpreview.github.io/?https://github.com/oemof/oemof-network/blob/python-coverage-comment-action-data/htmlcov/index.html)

This one will always be the same color. It won't work for private repos. I'm not even sure why we included it.

## What is that?

This branch is part of the
[python-coverage-comment-action](https://github.com/marketplace/actions/python-coverage-comment)
GitHub Action. All the files in this branch are automatically generated and may be
overwritten at any moment.