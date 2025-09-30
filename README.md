# 36120-25SP-group6-25609227-AT3-fastapi

**Description:**  
FastAPI service for deploying cryptocurrency price prediction models. Includes endpoints for health check, project info, and next-day HIGH price prediction for a selected token.

---

## Table of Contents

- [Installation](#installation)  
- [Usage](#usage)  
- [API Endpoints](#api-endpoints)  
- [Development](#development)  
- [License](#license)  

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

## Usage

Run the FastAPI server:
```bash
poetry run uvicorn app.main:app --reload
```
Visit http://127.0.0.1:8000 to see the API documentation.

## API Endpoints
| Endpoint                      | Method | Description                                                               |
| ----------------------------- | ------ |---------------------------------------------------------------------------|
| `/`                           | GET    | Shows a brief project description, list of endpoints, and link to GitHub. |
| `/health/`                    | GET    | Returns a status code 200 with a welcome message of your choice           |
| `/predict/<token>`            | GET    | Returns the next-day HIGH price prediction for the specified cryptocurrency token using your trained model.                   |


Detailed documentation is available automatically at http://127.0.0.1:8000/docs
 via Swagger UI.

## Docker Run Locally

1. Build the Docker image:

```bash 
docker build -t cryptocurrency-api-app .
```

2. Run the Docker container:

```bash
docker run -d -p 80:80 cryptocurrency-api-app
```

3. Access the application at http://localhost

## Docker Deployment

1.  Login to Docker Hub:
```bash
 docker login
```

2. Build the Docker image (specify platform if needed, e.g. linux/amd64):
```bash
  docker build --platform linux/amd64 -t nelkit792/cryptocurrency-api-app . 
```

3. Push the image to Docker Hub:
```bash
 docker push nelkit792/cryptocurrency-api-app
```

5. Deploy on Render.com using an existing Docker image:
   - Select "Existing Image" as the deployment method.
   - Provide the image URL: `docker.io/nelkit792/cryptocurrency-api-app`

> Note: The project also includes a GitHub Actions workflow for automated Docker image building and pushing to Docker Hub on every pull request to the main branch.


## License

This project is licensed under the MIT License.