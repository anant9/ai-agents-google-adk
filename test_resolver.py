import sys
import os

sys.path.append(os.getcwd())

from ResearchAgent.tools import _resolve_reference_doc_path

print("Testing exact match:")
print(_resolve_reference_doc_path("brand_guidelines.txt"))

print("\nTesting typo match (missing s):")
print(_resolve_reference_doc_path("brand_guideline.txt"))

print("\nTesting absolute paths:")
print(_resolve_reference_doc_path(os.path.join(os.getcwd(), r"doc- brand_guideline.txt")))

print("\nTesting crazy prompt string:")
print(_resolve_reference_doc_path("doc- brand_guideline.txt"))
