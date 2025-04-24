# Basketball PDF Analysis Pipeline

A web application that allows users to upload basketball statistics PDFs, analyzes the data using Claude 3.7 Anthropic API, and generates comprehensive scouting reports with game predictions.

## Features

- Upload multiple PDF files containing basketball statistics
- Analyze PDFs directly using Claude 3.7 Anthropic API
- Extract team and player statistics with AI-powered analysis
- Run game simulations to predict outcomes
- Generate detailed DOCX reports with analysis and predictions
- Simple and intuitive web interface
- Docker containerization for easy deployment
- AWS ECS deployment support with Terraform

## Project Structure

```
anona/
├── app/                       # Main application code
│   ├── main.py                # FastAPI application entry point
│   ├── routers/               # API endpoints
│   ├── services/              # Business logic
│   └── database/              # Database connection and models
├── static/                    # Static files for web interface
├── templates/                 # HTML templates
├── prompts/                   # Prompt templates for Claude 3.7
├── terraform/                 # Terraform configuration for AWS deployment
├── .github/workflows/         # GitHub Actions workflows
├── docker-compose.yml         # Docker Compose configuration
├── Dockerfile                 # Docker configuration
├── DEPLOYMENT.md              # Deployment documentation
├── requirements.txt           # Project dependencies
└── README.md                  # Project documentation
```

## Requirements

- Python 3.12
- FastAPI
- Uvicorn
- Anthropic API key (for Claude 3.7)
- PostgreSQL database
- Docker (for containerized deployment)
- Terraform (for AWS deployment)

## Quick Start with Docker

The easiest way to run the application is using Docker:

1. Clone the repository:
   ```
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Create a `.env` file with your Anthropic API key:
   ```
   echo "ANTHROPICS_API_KEY=your_api_key_here" > .env
   ```

3. Build and start the containers:
   ```
   docker-compose up --build
   ```

4. Access the application at http://localhost:8000

For more detailed deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).

## Manual Installation

If you prefer to run the application without Docker:

1. Clone the repository:
   ```
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up your Anthropic API key:
   ```
   echo "ANTHROPICS_API_KEY=your_api_key_here" > .env
   ```

5. Set up a PostgreSQL database and update the connection settings in `.env`.

6. Start the application:
   ```
   uvicorn app.main:app --reload
   ```

7. Access the application at http://localhost:8000

## AWS Deployment

The application can be deployed to AWS ECS using Terraform:

1. Navigate to the terraform directory:
   ```
   cd terraform
   ```

2. Configure your AWS credentials and update `terraform.tfvars`.

3. Run the deployment script:
   ```
   ./deploy.sh
   ```

For more detailed AWS deployment instructions, see [terraform/README.md](terraform/README.md).

## Input Format

The application accepts PDF files containing basketball statistics in various formats:
- Team overall statistics
- Individual player statistics
- Combined statistics

Sample PDF files can be found in the `data/input_samples` directory.

## Output Format

The application generates a DOCX report with the following sections:
- Matchup overview
- Team comparison
- Game plan
- Team player analysis
- Opponent player analysis
- Simulation results

Sample output reports can be found in the `data/output_samples` directory.

## Development

### Adding New Features

1. **Anthropic API Integration**: Modify `anthropic_api.py` to enhance PDF analysis or game simulation.
2. **Prompts**: Update the prompt templates in the `prompts` directory to improve analysis quality.
3. **Report Generation**: Update `report_gen.py` to include additional sections or formatting.
4. **Docker**: Update the Dockerfile or docker-compose.yml for container changes.
5. **AWS Deployment**: Update the Terraform configuration for infrastructure changes.

### Testing

Test the application with various PDF files to ensure robust extraction and analysis.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
