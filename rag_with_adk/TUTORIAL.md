# Expert Guide: Building a Production-Ready RAG Agent with the ADK

This tutorial provides a comprehensive, step-by-step guide to building, configuring, and deploying a sophisticated Retrieval-Augmented Generation (RAG) agent using the Google Agent Development Kit (ADK). We will go beyond simple examples to tackle the real-world challenges of authentication, permissions, and robust error handling that are critical for a production-ready application.

This guide is based on a real-world troubleshooting session, capturing the key learnings and final, correct configurations.

## 0. Prerequisites: Enabling Google Cloud APIs

Before you begin, you must enable several core APIs in your Google Cloud project. This is a one-time setup step.

*   **Goal:** Ensure all required cloud services are active for your project.
*   **Action:** Visit the following links and click "Enable" for each API. It may take a few minutes for the changes to take effect.
    1.  **Vertex AI API:** [https://console.developers.google.com/apis/api/aiplatform.googleapis.com/overview](https://console.developers.google.com/apis/api/aiplatform.googleapis.com/overview)
    2.  **Cloud Resource Manager API:** [https://console.developers.google.com/apis/api/cloudresourcemanager.googleapis.com/overview](https://console.developers.google.com/apis/api/cloudresourcemanager.googleapis.com/overview)

## 1. Initial Project Setup

*   **Goal:** Create a valid Python package for your agent.
*   **Action:**
    *   Rename the agent's directory from `8-rag-with-adk` to `rag_with_adk`. Directory names used as Python packages cannot start with a number or contain hyphens.
    *   Update any `vertexai.preview.rag` imports to `vertexai.rag` to use the latest stable library.

## 2. Creating a GCS Bucket

*   **Goal:** Create a secure location to store your documents.
*   **Action:**
    *   Create a new Google Cloud Storage bucket. Bucket names must be globally unique.
    *   **Command:**
        ```bash
        gcloud storage buckets create gs://<your-unique-bucket-name>
        ```

## 3. Creating a Dedicated Service Account

*   **Goal:** Create a specific identity for your agent to securely access GCS, following the principle of least privilege.
*   **Action:**
    *   Create a new service account.
    *   **Command:**
        ```bash
        gcloud iam service-accounts create rag-data-accessor --display-name="RAG Data Accessor"
        ```

## 4. Granting GCS Bucket Permissions

*   **Goal:** Allow the new service account to read files from the GCS bucket.
*   **Action:**
    *   Grant the `Storage Object Viewer` role to the new service account on your GCS bucket.
    *   **Command:**
        ```bash
        gcloud storage buckets add-iam-policy-binding gs://<your-bucket-name> \
            --member="serviceAccount:rag-data-accessor@<your-project-id>.iam.gserviceaccount.com"
            --role="roles/storage.objectViewer"
        ```

## 5. Creating and Securing a Service Account Key

*   **Goal:** Generate a private key that the agent can use to authenticate as the service account.
*   **Action:**
    *   Create a JSON key for the service account and save it directly into your agent's directory.
    *   **Command:**
        ```bash
        gcloud iam service-accounts keys create rag_with_adk/rag-accessor-key.json \
            --iam-account=rag-data-accessor@<your-project-id>.iam.gserviceaccount.com
        ```
    *   **Security Note:** Add `rag-accessor-key.json` to your `.gitignore` file to prevent accidentally committing the private key to version control.

## 6. Updating the Agent's Code for Authentication

*   **Goal:** Modify the `add_data` tool to use the new service account key for authentication.
*   **Action:**
    *   Update `add_data.py` to load the credentials directly from the JSON key file when creating the `storage.Client`.
    *   **Code Snippet:**
        ```python
        from google.oauth2 import service_account
        from google.cloud import storage
        import os

        KEY_FILE_PATH = os.path.join(os.path.dirname(__file__), 'rag-accessor-key.json')
        credentials = service_account.Credentials.from_service_account_file(KEY_FILE_PATH)
        storage_client = storage.Client(credentials=credentials)
        ```

## 7. Fixing Corpus Name Resolution

*   **Goal:** Ensure the agent can correctly find a corpus whether a display name or a full resource name is provided.
*   **Action:**
    *   Update the `get_corpus_resource_name` function in `utils.py` to perform a live lookup of the corpus by its display name if the provided name is not already a full resource name. This prevents errors from guessing the resource ID.