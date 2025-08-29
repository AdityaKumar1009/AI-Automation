# LLM Workflow Builder

A powerful drag-and-drop visual workflow builder for creating custom LLM applications with advanced RAG (Retrieval-Augmented Generation) capabilities.

## Features

- 🎯 **User Query Component**: Accept user input and questions
- 📚 **Knowledge Base Component**: Upload and process documents with Gemini embeddings and ChromaDB storage
- 🧠 **LLM Engine Component**: Integration with OpenAI GPT and Google Gemini
- 💬 **Output Component**: Chat interface for displaying results
- 🔍 **Web Search**: Optional integration with SerpAPI and Brave Search
- 🔄 **Drag & Drop**: Intuitive React Flow-based interface
- ⚡ **Real-time Execution**: Live workflow execution with status tracking

## Architecture

### Frontend (React + TypeScript)
- React Flow for drag-and-drop interface
- Custom node components for each workflow step
- Real-time execution monitoring
- Chat interface for follow-up questions

### Backend (FastAPI + Python)
- RESTful API with automatic documentation
- PostgreSQL database with SQLAlchemy
- ChromaDB for vector storage
- OpenAI and Gemini API integration
- Document processing with PyMuPDF

## Setup Instructions

### Prerequisites
- Node.js 16+ and npm
- Python 3.8+
- PostgreSQL database
- OpenAI API key
- (Optional) Google API key, SerpAPI key, Brave API key

### Database Setup
1. Create a PostgreSQL database named `mydb2`
2. Update database credentials in `.env` file

### Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys and database URL

# Run the server
python main.py
```

The backend will be available at `http://localhost:8000`
- API documentation: `http://localhost:8000/docs`

### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

The frontend will be available at `http://localhost:3000`

## Environment Variables

Create a `.env` file in the backend directory:

```env
DATABASE_URL=postgresql://crazeformarvel:12345@localhost:5432/mydb2
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
SERPAPI_KEY=your_serpapi_key_here
BRAVE_API_KEY=your_brave_api_key_here
CHROMA_DB_PATH=./chroma_db
```

## Usage

1. **Create Components**: Drag components from the palette to the canvas
2. **Configure Components**: Click on each component to configure settings
3. **Connect Components**: Draw connections between component handles
4. **Execute Workflow**: Click "Execute Workflow" to run the pipeline
5. **View Results**: Results appear in the Output component with chat interface

### Component Types

#### User Query Component
- Entry point for user questions
- Connects to: Knowledge Base, LLM Engine

#### Knowledge Base Component
- Upload PDF, TXT, MD files
- Automatic text extraction and embedding generation
- Provides context to LLM Engine
- Connects to: LLM Engine

#### LLM Engine Component
- Choose between GPT-3.5, GPT-4, Gemini models
- Custom system prompts
- Optional web search integration
- Temperature control
- Connects to: Output

#### Output Component
- Display AI responses
- Show source citations
- Chat interface for follow-up questions
- Copy responses to clipboard

## API Endpoints

### Workflows
- `GET /api/workflows` - List workflows
- `POST /api/workflows` - Create workflow
- `GET /api/workflows/{id}` - Get workflow
- `PUT /api/workflows/{id}` - Update workflow
- `DELETE /api/workflows/{id}` - Delete workflow

### Components
- `GET /api/components/workflow/{workflow_id}` - List workflow components
- `POST /api/components` - Create component
- `PUT /api/components/{id}` - Update component
- `DELETE /api/components/{id}` - Delete component

### Documents
- `POST /api/documents/upload` - Upload document
- `GET /api/documents` - List documents
- `DELETE /api/documents/{id}` - Delete document

### LLM & Execution
- `POST /api/llm/chat` - Direct LLM chat
- `POST /api/llm/execute-workflow/{workflow_id}` - Execute workflow
- `GET /api/llm/executions/{execution_id}` - Get execution status

## Development

### Backend Development
- Models are in `app/models.py`
- API routes are in `app/routers/`
- Services are in `app/services/`
- Database config in `app/database.py`

### Frontend Development
- Main workflow builder: `src/components/WorkflowBuilder.tsx`
- Node components: `src/components/nodes/`
- Drag palette: `src/components/ComponentPalette.tsx`
- Execution panel: `src/components/ExecutionPanel.tsx`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details
