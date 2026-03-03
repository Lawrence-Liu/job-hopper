# LangGraph Cloud Run Terraform

This Terraform module deploys the LangGraph API to Cloud Run and provisions:
- Required project services
- Artifact Registry Docker repository
- Runtime service account
- Vertex AI runtime permission for Gemini (`roles/aiplatform.user`)
- Cloud Run service
- Optional public invoker IAM binding

Authentication model:
- No `OPENAI_API_KEY` is required.
- Cloud Run uses its service account + Application Default Credentials to call Gemini via Vertex AI.

## 1) Build and push image

From repo root:

```bash
gcloud auth configure-docker us-central1-docker.pkg.dev

docker build -f deploy/langgraph/Dockerfile -t us-central1-docker.pkg.dev/<PROJECT_ID>/<REPO>/langgraph-api:latest .
docker push us-central1-docker.pkg.dev/<PROJECT_ID>/<REPO>/langgraph-api:latest
```

## 2) Deploy with Terraform

```bash
cd infra/terraform/langgraph-cloud-run
cp terraform.tfvars.example terraform.tfvars
# edit terraform.tfvars

terraform init
terraform plan
terraform apply
```

## 3) Verify

After apply, output `service_url` points to your API. Health endpoint:

```bash
curl "$SERVICE_URL/health"
```
