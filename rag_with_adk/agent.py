# rag_agent/agent.py

import os

import google.auth
from google.adk.agents import Agent
from google.auth.transport.requests import Request
from google.cloud import aiplatform
from google_auth_oauthlib import flow
from vertexai import rag

from .add_data import add_data
from .create_corpus import create_corpus
from .delete_corpus import delete_corpus
from .delete_document import delete_document
from .get_corpus_info import get_corpus_info
from .list_corpora import list_corpora
from .rag_query import rag_query

root_agent = Agent(
    name="RagAgent",
    # Using Gemini 2.5 Flash for best performance with RAG operations
    model="gemini-2.5-flash",
    description="Vertex AI RAG Agent",
    tools=[
        rag_query,
        list_corpora,
        create_corpus,
        add_data,
        get_corpus_info,
        delete_corpus,
        delete_document,
    ],
)
