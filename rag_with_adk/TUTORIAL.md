# Tutorial: Configuring and Running the RAG Agent

This tutorial provides the essential steps to configure and run the Vertex AI RAG agent after you have cloned the project. This guide assumes the agent's code is in its final, working state.

## 1. Prerequisites: Enabling Google Cloud APIs

Before you begin, you must enable several core APIs in your Google Cloud project. This is a one-time setup step.

*   **Goal:** Ensure all required cloud services are active for your project.
*   **Action:** Visit the following links for your Google Cloud project and click "Enable" for each API. It may take a few minutes for the changes to take effect.
    1.  **Vertex AI API:** [https://console.developers.google.com/apis/api/aiplatform.googleapis.com/overview](https://console.developers.google.com/apis/api/aiplatform.googleapis.com/overview)
    2.  **Cloud Resource Manager API:** [https://console.developers.google.com/apis/api/cloudresourcemanager.googleapis.com/overview](https://console.developers.google.com/apis/api/cloudresourcemanager.googleapis.com/overview)

## 2. Configuration: GCS and Service Account Setup

This agent requires a Google Cloud Storage (GCS) bucket to store documents and a dedicated Service Account to securely access it.

### Step 2.1: Create a GCS Bucket

Create a secure, private location to store the documents you want your agent to access.

*   **Command:**
    ```bash
    # Bucket names must be globally unique. Using your project ID is a good practice.
    gcloud storage buckets create gs://<your-unique-bucket-name>
    ```

### Step 2.2: Create a Dedicated Service Account

Create a new, dedicated identity for the agent. This follows the principle of least privilege.

*   **Command:**
    ```bash
    gcloud iam service-accounts create rag-data-accessor --display-name="RAG Data Accessor"
    ```

### Step 2.3: Grant the Service Account GCS Access

Grant the new service account permission to read files from your GCS bucket.

*   **Command:**
    ```bash
    gcloud storage buckets add-iam-policy-binding gs://<your-bucket-name> \
        --member="serviceAccount:rag-data-accessor@<your-project-id>.iam.gserviceaccount.com"
        --role="roles/storage.objectViewer"
    ```

### Step 2.4: Generate and Secure the Service Account Key

Generate a private JSON key file that the agent will use to authenticate.

*   **Command:**
    ```bash
    gcloud iam service-accounts keys create rag_with_adk/rag-accessor-key.json \
        --iam-account=rag-data-accessor@<your-project-id>.iam.gserviceaccount.com
    ```
*   **Security Note:** The `.gitignore` file is already configured to ignore `rag-accessor-key.json`, so you don't have to worry about committing it by accident.

## 3. Running the Agent

With the configuration complete, you can now run the agent.

1.  **Upload a File:** Upload a PDF or other document to the GCS bucket you created.
2.  **Start the Server:** Run `adk web` from the project root.
3.  **Interact:** Use the web UI to create a corpus and add your file using its GCS path (e.g., `gs://<your-bucket-name>/<your-file-name>.pdf`).
