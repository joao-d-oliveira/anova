# Basketball PDF Analysis Pipeline

A web application that allows users to upload basketball statistics PDFs, analyzes the data using Anthropic's Claude API, and generates comprehensive scouting reports with game predictions.

## Features

- Upload multiple PDF files containing basketball statistics
- Analyze PDFs directly using Anthropic's Claude API
- Extract team and player statistics with AI-powered analysis
- Run game simulations to predict outcomes
- Generate detailed DOCX reports with analysis and predictions
- Simple and intuitive web interface
- Docker containerization for easy deployment
- AWS ECS deployment support with Terraform

## Project Structure

```
anona/
├── app/                            # Main application code
│   ├── main.py                     # FastAPI application entry point
│   ├── routers/                    # API endpoints
│   ├── services/                   # Business logic
│   ├── database/                   # Database connection and models
│   ├── static/                     # Static files for web interface
│   ├── templates/                  # HTML templates
│   ├── data/                       # Sample input/output data
│   │   ├── input_samples/          # Sample PDF input files
│   │   └── output_samples/         # Sample generated reports
│   ├── prompts/                    # Prompt templates for Claude
│   └── tests/                      # Application tests
├── data/                           # Additional data directory
├── terraform/                      # Terraform configuration for AWS deployment
├── docker-compose.yml              # Docker Compose configuration
├── Dockerfile                      # Docker configuration
├── docker-test.sh                  # Docker test script
├── DEPLOYMENT.md                   # Deployment documentation
├── aws-ecs-deployment.md           # AWS ECS specific deployment guide
├── requirements.txt                # Project dependencies
└── README.md                       # Project documentation
```

## Requirements

- Python 3.12
- FastAPI
- Uvicorn
- Anthropic API key (for Claude)
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

2. Create a `.env` file with required environment variables:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   DB_HOST=localhost
   DB_NAME=anova
   DB_USER=anova_user
   DB_PASSWORD=your_secure_password
   ```

3. Build and start the containers:
   ```
   docker-compose up --build
   ```

   For testing the Docker setup:
   ```
   ./docker-test.sh
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

4. Create a `.env` file with required environment variables:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   DB_HOST=localhost
   DB_NAME=anova
   DB_USER=anova_user
   DB_PASSWORD=your_secure_password
   ```

5. Set up a PostgreSQL database with the credentials specified in your `.env` file.

6. Start the application:
   ```
   uvicorn app.main:app --reload
   ```

7. Access the application at http://localhost:8000

## AWS Deployment

The application can be deployed to AWS ECS using Terraform. Before proceeding, ensure you have:

- AWS Account with appropriate permissions
- AWS CLI installed and configured
- Docker installed locally
- ECR repository created for the application image
- PostgreSQL RDS instance (can be created during deployment)

1. Navigate to the terraform directory:
   ```
   cd terraform
   ```

2. Configure your AWS credentials and update `terraform.tfvars`.

3. Run the deployment script:
   ```
   ./deploy.sh
   ```

For more detailed AWS deployment instructions, see:
- [aws-ecs-deployment.md](aws-ecs-deployment.md) for ECS-specific deployment guide
- [terraform/README.md](terraform/README.md) for Terraform configuration details

## Input Format

The application accepts PDF files containing basketball statistics in various formats:
- Team overall statistics
- Individual player statistics
- Combined statistics

Sample PDF files can be found in the `app/data/input_samples` directory.

## Output Format

The application generates a DOCX report with the following sections:
- Matchup overview
- Team comparison
- Game plan
- Team player analysis
- Opponent player analysis
- Simulation results

Sample output reports can be found in the `app/data/output_samples` directory.

## Development

### Adding New Features

1. **Anthropic API Integration**: Modify `app/services/anthropic_api.py` to enhance PDF analysis or game simulation.
2. **Prompts**: Update the prompt templates in the `app/prompts` directory to improve analysis quality.
3. **Report Generation**: Update `app/services/report_gen.py` to include additional sections or formatting.
4. **Docker**: Update the Dockerfile or docker-compose.yml for container changes.
5. **AWS Deployment**: Update the Terraform configuration for infrastructure changes.

### Testing

Test the application with various PDF files to ensure robust extraction and analysis.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
