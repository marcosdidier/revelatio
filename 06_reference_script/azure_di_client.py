"""Azure Document Intelligence — prebuilt Layout wrapper.

Returns the raw analyze result as a dict (text + tables + paragraphs + spans),
plus wall-clock latency. The pipeline's downstream stages parse this dict.
"""
import os
import time
from pathlib import Path

from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
from azure.core.credentials import AzureKeyCredential


def analyze_pdf(pdf_path: Path) -> tuple[dict, float]:
    endpoint = os.environ["AZURE_DI_ENDPOINT"]
    key = os.environ["AZURE_DI_KEY"]
    client = DocumentIntelligenceClient(
        endpoint=endpoint, credential=AzureKeyCredential(key)
    )

    t0 = time.perf_counter()
    with open(pdf_path, "rb") as f:
        poller = client.begin_analyze_document(
            "prebuilt-layout",
            AnalyzeDocumentRequest(bytes_source=f.read()),
        )
    result = poller.result()
    elapsed = time.perf_counter() - t0
    return result.as_dict(), elapsed
