ARG BASE_IMAGE=python:latest
FROM ${BASE_IMAGE} AS base

ENTRYPOINT [ "echo", "Hello World!" ]