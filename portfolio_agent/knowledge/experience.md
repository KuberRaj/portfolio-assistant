# Professional Experience

## Associate Consultant

Kunal Kuber Raj works as an Associate Consultant with responsibilities spanning agentic AI development, cloud data engineering, application integration, technical analysis, and delivery support.

The work described in this document is intentionally presented at a public, client-neutral level. Confidential client names, internal URLs, credentials, proprietary implementation details, and restricted business data are excluded.

## Agentic AI Development

Kunal has hands-on experience designing agent-based applications in Python. These applications use root agents, specialized sub-agents, custom tools, session context, and structured workflows to complete multi-stage technical tasks.

Typical responsibilities include:

- Defining the purpose and boundaries of root agents and sub-agents
- Designing agent instructions for reliable tool selection
- Building Python functions that agents can invoke as tools
- Passing state between workflow stages
- Validating tool inputs before executing operations
- Returning natural-language progress updates and execution summaries
- Handling failures without exposing internal implementation details
- Preventing agents from fabricating unsupported outcomes
- Designing workflows that separate reasoning from deterministic execution

## Google Agent Development Kit Experience

Kunal has worked with Google Agent Development Kit for approximately one year and has used it to develop modular, tool-enabled agent workflows.

Areas of experience include:

- Defining ADK root agents
- Registering Python functions as agent tools
- Designing sub-agent responsibilities
- Using ADK sessions for conversational continuity
- Running agents through the ADK command-line interface and development UI
- Exposing agents through the ADK API server
- Integrating React applications with ADK session and streaming endpoints
- Processing Server-Sent Events from the ADK `run_sse` endpoint
- Filtering tool events and rendering model responses in a chatbot interface
- Maintaining conversational responses instead of exposing raw tool output

## Data Ingestion and Processing Workflows

Kunal has worked on agent-assisted data workflows that perform ingestion, validation, quality checks, and reconciliation.

A typical workflow includes:

1. Receiving a source file, API location, or cloud-storage path
2. Validating the input and source configuration
3. Extracting or reading source data
4. Storing files or intermediate artifacts in Google Cloud Storage
5. Preparing or executing BigQuery jobs
6. Performing data-quality checks
7. Performing reconciliation checks
8. Generating a natural-language summary of the processing result

Kunal's data pipeline experience includes an API-based extraction stage that stores extracted data in a Google Cloud Storage bucket before downstream processing.

## BigQuery Experience

Kunal has worked with BigQuery for data ingestion and validation workflows. Agentic applications can create and execute BigQuery jobs for operations such as:

- Creating target tables
- Loading data into tables
- Running ingestion queries
- Executing data-quality checks
- Executing reconciliation checks
- Validating record counts and processing outcomes
- Storing application-related datasets

Kunal has also worked with BigQuery datasets used for access-control and registered-user information, including hashed passwords and timestamps. Public portfolio descriptions intentionally exclude sensitive schemas, values, credentials, and operational details.

## Google Cloud Storage Experience

Kunal uses Google Cloud Storage for source files, generated outputs, intermediate artifacts, and data-pipeline handoffs.

Relevant experience includes:

- Reading files from GCS paths
- Writing generated files to destination GCS paths
- Organizing artifacts through folders and prefixes
- Validating source and destination locations
- Uploading generated code and processing outputs
- Using GCS as an intermediate stage between extraction and BigQuery processing

## Cloud Migration and Artifact Analysis

Kunal has worked on solutions that analyze Azure Data Factory artifacts and map their processing logic to Google Cloud-oriented implementations.

This work includes:

- Reading and validating ADF pipeline artifacts
- Understanding parent-and-child pipeline relationships
- Identifying activity dependencies
- Interpreting expressions and parameters
- Tracing source-to-target data movement
- Generating human-readable pipeline summaries
- Producing migration-oriented code artifacts
- Managing generated files before uploading them to cloud storage

The objective is not simple file conversion. The workflow analyzes the intent and orchestration represented by the original artifacts, then produces equivalent or migration-ready outputs for the target environment.

## Data Quality and Reconciliation

Kunal has experience with automated workflows that perform data-quality and reconciliation checks after ingestion.

Checks can include:

- Required-field validation
- Record-count comparison
- Duplicate detection
- Null-value checks
- Source-to-target consistency checks
- Schema and datatype validation
- Processing-status reporting
- Exception and mismatch summaries

These validations are typically executed through deterministic queries or Python tools, while agents coordinate the workflow and explain the outcome in natural language.

## Frontend and Agent Integration

Kunal uses React.js and Tailwind CSS to build interfaces for agentic applications.

Relevant frontend experience includes:

- Building chat interfaces for AI agents
- Creating compact and expanded chatbot views
- Integrating streaming backend responses
- Managing ADK user and session identifiers
- Rendering loading and typing indicators
- Handling connection and agent errors
- Maintaining conversation state while switching UI modes
- Designing responsive layouts for desktop and mobile
- Presenting agent responses in a readable, conversational format

Kunal has also explored an admin-only frontend feature for editing backend configuration files. The proposed design includes a file list, a code-editor interface, and controlled support for JSON, YAML, and CONF files.

## Technical Communication and Delivery Support

Kunal contributes to technical communication activities such as:

- Preparing implementation summaries
- Documenting pipeline logic
- Explaining dependencies and open items
- Creating meeting minutes
- Summarizing project status
- Presenting technical concepts through simple analogies
- Converting tool-generated results into stakeholder-friendly language

This communication focus also influences agent design. Agents are instructed to provide concise commentary and meaningful progress updates instead of returning only raw JSON or silently waiting for tool completion.

## Engineering Principles

Kunal's implementation approach emphasizes:

- Clear separation between agent reasoning and deterministic tools
- Input validation before tool execution
- Grounding responses in available evidence
- Minimal exposure of internal paths and implementation details
- Reusable and modular workflow components
- Natural-language summaries for technical operations
- Controlled handling of errors and incomplete information
- Public-safe documentation that avoids confidential client details
