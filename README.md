# RealValuator deployment guide

This guide will walk you through building, testing, pushing, and deploying the RealVal application using Docker, Azure Container Registry, and Terraform.

---

## 1. Prerequisites

- [Docker](https://www.docker.com/get-started)
- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
- [Terraform](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli)
- Azure subscription with permission to create resources

---

## 2. Build and test locally

1. **Build the Docker image:**
    ```bash
    docker build -t realval:latest .
    ```

2. **Run the Docker container locally:**
    ```bash
    docker run -p 8501:8501 realval:latest
    ```

3. **Open your browser and verify:**
    ```
    http://localhost:8501
    ```

If everything works locally, proceed to cloud deployment.

---

## 3. Azure Container Registry (ACR) setup

> **Skip this step if you already have an Azure Container Registry (ACR).**

1. **Create an ACR instance:**
    ```bash
    az acr create --resource-group Real_Valuator --name realvalacr --sku Basic
    ```

2. **Log in to your ACR:**
    ```bash
    az acr login --name realvalacr
    ```

---

## 4. Build, tag and push Docker image to ACR

1. **Tag the image for ACR:**
    ```bash
    docker tag realval:latest realvalacr.azurecr.io/realval:latest
    ```
    *Or build directly with the target tag:*
    ```bash
    docker build -t realvalacr.azurecr.io/realval:latest .
    ```

2. **Push the image to your ACR:**
    ```bash
    docker push realvalacr.azurecr.io/realval:latest
    ```

---

## 5. Deploy infrastructure with Terraform

1. **Initialize Terraform:**
    ```bash
    terraform init
    ```

2. **Review the execution plan:**
    ```bash
    terraform plan
    ```

3. **Apply the configuration:**
    ```bash
    terraform apply
    ```
    Confirm the action when prompted.

4. **Display outputs (such as app URL):**
    ```bash
    terraform output
    ```

---

## 6. Access Deployed App
http://realvaluatorapp.northeurope.azurecontainer.io:8501/

