# eqlpy Examples README

This directory contains short examples of using eqlpy to store and query encrypted records.

## Prerequisites

### psycopg example

* Python 3
* Docker
* Docker compose
* CipherStash account
* Supported database driver/ORM, either of:
    * sqlalchemy + psycopg2
    * psycopg 3
* (Optinal) direnv or other tools to load environment variables from a file

## Setup

* Follow the Getting started guides for [CipherStash Proxy](https://cipherstash.com/docs/getting-started/cipherstash-proxy) and [CipherStash Encrypt](https://cipherstash.com/docs/getting-started/cipherstash-encrypt) to obtain the following:
    * Dataset ID
    * Workspace ID
    * Client access key
    * Client ID
    * Client key
* Copy the `.envrc.example` to `.envrc` and edit the contents to set the above values inside
    * If you are using tools like direnv, make sure this file is loaded
    * If you are not using such tools, make sure the environment variables are set before executing the examples. If you are on bash (or similar), the following should work: `source .envrc`
* Start PostgreSQL and CipherStash Proxy using `docker compose`: `docker compose up -d`

## Execution

At this point, you should be able to run the examples.

* If you have sqlalchemy and psycopg2, run `python examples/sqlalchemy_examples.py`
* If you have psycopg 3, run: `python examples/psycopg_examples.py`

and follow the prompt/instructions.
