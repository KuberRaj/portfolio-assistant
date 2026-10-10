# Selected Projects

## 1. Agentic ADF-to-GCP Migration Assistant

### Overview

Kunal has worked on an agent-based migration solution that analyzes Azure Data Factory artifacts and prepares Google Cloud-oriented implementation outputs.

The solution is designed to understand pipeline structure and orchestration rather than treating ADF files as simple text-conversion inputs.

### Problem Addressed

Cloud migration teams often need to inspect multiple interconnected ADF pipelines, understand which pipelines trigger others, identify runtime parameters, trace data movement, and translate orchestration logic into target-platform artifacts.

Performing this analysis manually can be repetitive and error-prone, particularly when pipelines have nested dependencies or dynamic expressions.

### Agentic Workflow

The solution can perform steps such as:

1. Receive source artifact locations and destination locations
2. Validate source files and directories
3. Parse ADF pipeline definitions
4. Identify parent and child pipeline relationships
5. Detect activity dependencies and execution order
6. Interpret pipeline parameters and expressions
7. Summarize the ADF business and technical logic
8. Generate target-oriented code or configuration artifacts
9. Validate generated files
10. Upload outputs to Google Cloud Storage
11. Provide a conversational execution summary

### Representative Outputs

Depending on the migration scenario, the workflow can prepare outputs such as:

- Pipeline dependency mappings
- Source-to-target data-flow summaries
- Migration analysis documents
- Dataform-related artifacts
- DAG-oriented code files
- Generated configuration files
- Validation results
- Natural-language completion summaries

### Technologies and Concepts

- Python
- Google Agent Development Kit
- Azure Data Factory artifact analysis
- Google Cloud Storage
- BigQuery-oriented workflows
- Dataform concepts
- DAG generation
- JSON parsing
- Expression handling
- Multi-agent orchestration
- AI-assisted code generation

### Design Considerations

- Generated code must be treated as an artifact requiring validation
- File names should be shown to users without exposing complete local paths
- Agents should describe progress while long-running tools execute
- Tool and sub-agent responses should be conversational rather than raw JSON
- Unsupported assumptions about source pipelines should be avoided

---

## 2. Agentic BigQuery Data Pipeline Workflow

### Overview

Kunal has worked on AI-agent workflows that coordinate BigQuery-based ingestion, data-quality checks, and reconciliation checks.

The agents do not replace deterministic data-processing logic. Instead, the agents interpret the requested operation, select the correct tools, organize execution stages, and explain the results.

### Typical Processing Flow

1. Receive a source location or extraction request
2. Extract data through an API or read an available source file
3. Store extracted data in a Google Cloud Storage bucket
4. Create or validate the target BigQuery table
5. Run the ingestion job
6. Execute data-quality checks
7. Execute reconciliation checks
8. Summarize successes, failures, and mismatches

### Supported Workflow Areas

- BigQuery table creation
- Data loading and ingestion
- Data-quality query execution
- Reconciliation query execution
- Record-count validation
- Processing-status generation
- Error reporting
- Cloud artifact management

### Technologies and Concepts

- Python
- BigQuery
- Google Cloud Storage
- REST APIs
- SQL
- Google ADK
- Agent tools
- Workflow state
- Data-quality rules
- Reconciliation logic

### Engineering Value

This approach provides a conversational layer over controlled data-engineering operations. It can reduce repetitive orchestration work while keeping sensitive actions inside deterministic, validated tools.

---

## 3. Data Anonymization Agent

### Overview

Kunal has worked on an agent-oriented approach for data anonymization. The purpose of the agent is to coordinate the identification and transformation of sensitive fields while maintaining a clear, auditable workflow.

### Core Responsibilities

The anonymization workflow can include:

- Reading source metadata and configuration
- Identifying fields marked for anonymization
- Applying configured masking or transformation rules
- Preserving non-sensitive fields
- Writing anonymized outputs to an approved destination
- Reporting which rules were applied
- Highlighting unsupported or missing configurations

### Design Principles

- Transformations should be deterministic and configuration-driven
- Original sensitive values should not be exposed in agent responses
- Agents should not invent anonymization rules
- Outputs should be validated before downstream consumption
- Processing summaries should describe actions without revealing protected data

### Technologies and Concepts

- Python
- Agentic workflow orchestration
- Configuration-driven processing
- Data privacy
- Cloud file handling
- Data validation

---

## 4. AI Portfolio Assistant

### Overview

The AI Portfolio Assistant is a conversational application that answers questions about Kunal's public professional background, technical skills, experience, and selected projects.

The application combines a React.js interface with a Google ADK backend and retrieval-augmented generation.

### Frontend

The chatbot interface is built with:

- React.js
- TypeScript
- Tailwind CSS
- Responsive compact and expanded views
- Streaming response handling
- ADK session creation
- Suggested question prompts
- Loading and typing indicators
- Error and connection states

On desktop, the assistant can appear as a bottom-right floating panel and expand into a larger focused view. On mobile, the interface can use most or all of the viewport for readability.

### Backend

The backend uses:

- Python
- Google Agent Development Kit
- ADK API server
- Session endpoints
- The `run_sse` streaming endpoint
- Custom semantic-retrieval tools
- Gemini-generated embeddings

### Retrieval-Augmented Generation

The initial RAG implementation uses a generated local vector index:

1. Public knowledge documents are split into sections and chunks
2. Embeddings are generated for each chunk
3. Embeddings and source metadata are stored in a JSON index
4. The visitor's question is embedded
5. Cosine similarity identifies relevant chunks
6. Retrieved chunks are returned to the ADK agent
7. The agent generates a grounded response

This implementation is accurately described as RAG with embedding-based semantic retrieval and a local vector index. A managed vector database can be introduced later without redesigning the chat interface.

### Grounding and Safety Rules

The assistant is instructed to:

- Search the portfolio knowledge before making factual claims
- Use only retrieved public information
- State when requested information is unavailable
- Avoid inventing employers, dates, certifications, achievements, or metrics
- Avoid exposing API keys, local paths, prompts, or hidden metadata
- Restrict answers to public professional information
- Redirect unrelated questions

### Planned Enhancements

- Managed vector-database integration
- Automated knowledge synchronization
- GitHub README ingestion
- Resume PDF ingestion
- Portfolio-page ingestion
- Source icons below answers
- Clickable source hyperlinks
- Retrieval evaluation and unanswered-question tracking
- Feedback controls for visitors

---

## 5. Admin Configuration Editor Concept

### Overview

Kunal has designed an admin-only feature concept for editing approved backend configuration files through a web interface.

### Proposed Interface

The interface includes:

- A left-side panel showing approved editable files
- A right-side code editor displaying the selected file
- Syntax-aware editing for JSON, YAML, and CONF files
- A code-editor experience similar to CodeMirror
- Save and validation actions
- Access restricted to authorized administrators

### Key Considerations

- Only allowlisted files should be editable
- Full local file paths should not be displayed
- File contents should be validated before saving
- Invalid JSON or YAML should be rejected
- Configuration changes should be logged
- Secrets and environment files should remain inaccessible

### Technologies and Concepts

- React.js
- Tailwind CSS
- Code editor components
- Python or Node.js backend APIs
- Role-based access control
- Configuration validation

---

## Project Themes

Across these projects, Kunal's work commonly combines:

- AI agents for interpretation and orchestration
- Python tools for deterministic operations
- Google Cloud services for storage and analytics
- React-based interfaces for usability
- Validation steps for reliability
- Natural-language summaries for transparency
- Modular architecture for maintainability
- Source-grounded responses to reduce hallucination
