# 36120-25SP-group6-25609227-AT3-fastapi

**Description:**  
FastAPI service for deploying cryptocurrency price prediction models. It includes endpoints for health checks, project information, and next-day high price predictions for a selected token.

This API loads the trained LSTM model from the experimentation phase and exposes it through REST endpoints for integration with the Streamlit dashboard. It incorporates preprocessing, prediction, and error-handling logic to ensure reliable and consistent responses.

---

## Table of Contents
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Testing](#testing)
- [API Endpoints](#api-endpoints)
- [Error Handling](#error-handling)
- [Docker Run Locally](#docker-run-locally)
- [Docker Deployment](#docker-deployment)
- [License](#license)

---

## Project Structure

```
├── app/                  # FastAPI application (entrypoint, routes)
│   ├── main.py
├── src/                  # Source code for inference, services, and transformers
│   ├── inference/
│   │   └── predict.py         # Calls the LSTM model and performs the next-day HIGH price prediction
│   ├── services/
│   │   ├── api.py             # Client for CoinGecko API and utilities for fetching market data
│   │   └── constants.py       # Constants used for API connection and data handling
│   └── transformers/
│       └── sequence_transformer.py # Preprocessing and sequence transformation functions for the LSTM model
├── models/               # Trained ML models and preprocessing pipelines
│   ├── lstm_model.keras
│   └── pipeline_preprocessing.pkl
├── tests/                # Unit and integration tests
│   └── test_main.py
├── install_tensorflow.py # Script for installing the correct TensorFlow version
├── requirements.txt      # Python dependencies (for non-Poetry users)
├── pyproject.toml        # Poetry project configuration
├── Dockerfile            # Docker build instructions
├── README.md             # Project documentation
├── github.txt            # (Project-specific file)
```

---

## Installation

1. Clone the repository:

```bash
git clone https://github.com/Nelkit/36120-25SP-group6-25609227-AT3-fastapi.git

cd 36120-25SP-group6-25609227-AT3-fastapi
```
2. Set Python version (if not already set):

```bash
 pyenv install 3.11.4
 pyenv local  3.11.4
```

3. Activate the poetry environment

```bash
poetry env activate
```

4. Install dependencies with Poetry:

```bash
poetry install
```

>⚠️ **Mac M1/M2 vs Windows Users**  
TensorFlow requires different versions depending on the operating system:
>- **Mac (Apple Silicon, M1/M2)**: It is recommended to install `tensorflow-macos` and `tensorflow-metal` to leverage the integrated GPU.
> - **Windows / Intel Macs**: It is recommended to install standard `tensorflow`.  
> 
>You can run the included script to automatically install the correct version:
>```bash
>poetry run python install_tensorflow.py
>```
>Or install manually depending on your system:
>**Mac:**
>```bash
>poetry add tensorflow-macos tensorflow-metal
>```
>**Windows:**
>```bash
>poetry add tensorflow
>```

---

## Usage

Run the FastAPI server:
```bash
poetry run uvicorn app.main:app --reload
```
Visit http://127.0.0.1:8000 to see the API documentation.

---

## Testing

Run the tests using pytest:
```bash
poetry run pytest tests/
```

The tests are mocked to avoid external dependencies and should run quickly.

---

## API Endpoints
| Endpoint            | Method | Description                                                                                                 |
|---------------------|--------|-------------------------------------------------------------------------------------------------------------|
| `/`                 | GET    | Project overview and metadata.                                                                              |
| `/health`           | GET    | Service health check (returns 200 and a welcome message).                                                   |
| `/predict/{token}`  | GET    | Predicts the next-day HIGH price for Ethereum (only supports 'ETH' as token). Returns prediction in USD.    |

Detailed documentation is automatically available at http://127.0.0.1:8000/docs
 via Swagger UI, or at http://127.0.0.1:8000/redoc
 via ReDoc.

---

## Error Handling

The API provides clear and consistent error responses for common failure scenarios. Below are the main error codes and their meanings for the `/predict/{token}` endpoint:

| Status Code | Meaning                                      | Description                                                        |
|-------------|----------------------------------------------|--------------------------------------------------------------------|
| 200         | OK                                           | Prediction generated successfully.                                 |
| 400         | Invalid token or unsupported cryptocurrency  | The provided token is not supported (only 'ETH' is accepted).      |
| 422         | Validation Error                             | The input parameter is missing or malformed.                       |
| 500         | Error during model inference                 | An internal error occurred during prediction.                      |
| 503         | Failed to fetch data from CoinGecko          | The service could not retrieve data from the external API.         |

**Example error response:**
```json
{
  "detail": "Only Ethereum predictions are available."
}
```

The API always returns a clear error message in the `detail` field to help you diagnose issues quickly.

---

## Docker Run Locally

1. Build the Docker image:

```bash 
docker build -t crypto-forecast-api .
```

2. Run the Docker container:

```bash
docker run -d -p 80:80 crypto-forecast-api
```

---

## Docker Deployment

1.  Login to Docker Hub:
```bash
docker login
```

2. Build the Docker image (specify platform if needed, e.g. linux/amd64):
```bash
docker build --platform linux/amd64 -t nelkit792/crypto-forecast-api . 
```

3. Push the image to Docker Hub:
```bash
docker push nelkit792/crypto-forecast-api
```

5. Deploy on Render.com using an existing Docker image:
   - Select "Existing Image" as the deployment method.
   - Provide the image URL: `docker.io/nelkit792/crypto-forecast-api`

> Note: The project also includes a GitHub Actions workflow for automated Docker image building and pushing to Docker Hub on every pull request to the main branch.

---

## GitHub Actions CI/CD Deployment

This project uses GitHub Actions for continuous integration and deployment (CI/CD). The workflow automatically runs on every push or pull request to the **main branch**. The main steps are:

1. **Install dependencies**: Sets up Python and installs all project dependencies using Poetry.
2. **TensorFlow installation**: Runs the `install_tensorflow.py` script to ensure the correct TensorFlow version is installed for the runner's OS.
3. **Run tests**: Executes all tests in the `tests/` directory to ensure code quality and correctness.
4. **Build and push Docker image**: If tests pass and the branch is `main`, the workflow builds a Docker image and pushes it to Docker Hub.

This ensures that only code that passes all tests and builds successfully is deployed. You can find the workflow configuration in the `.github/workflows/` directory.

---

## License

This project is licensed under the MIT License.
