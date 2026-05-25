# DataMind - Streamlit Frontend

This document explains how to use the new Streamlit-based frontend for DataMind.

## What Changed?

The frontend uses Streamlit (`app_streamlit.py`) for a modern, interactive experience.

## Features

### 1. **Chat with Bob** 💬
- Interactive chat interface with AI assistant Bob
- Quick suggestion buttons for common queries
- Real-time responses from the DataMind Core service
- Intent-based routing (Discovery, Lineage, Generation, Cost agents)
- Session management for conversation context

### 2. **Lineage Explorer** 🔗
- Visualize data lineage from Neo4j knowledge graph
- Search by asset name (e.g., `fct_orders`)
- Choose direction: upstream, downstream, or both
- View lineage paths in a clear, readable format
- Distinguish between dbt models and Snowflake tables

### 3. **Cost Dashboard** 💰
- Monitor Snowflake query costs over the last 7 days
- Key metrics: Total Queries, Total Credits, Total USD
- Interactive bar chart showing daily cost breakdown
- Detailed data table with all cost information

## Running the Streamlit App

### Option 1: Direct Python Execution
```bash
cd datamind/datamind_frontend
streamlit run app_streamlit.py
```

The app will open automatically at `http://localhost:8501`

### Option 2: Docker
The Dockerfile has been updated to use Streamlit:

```bash
cd datamind
docker-compose up --build
```

### Option 3: Manual Docker Build
```bash
cd datamind/datamind_frontend
docker build -t datamind-frontend-streamlit .
docker run -p 8501:8501 --env-file ../.env datamind-frontend-streamlit
```

## Configuration

### Environment Variables
The app reads from `datamind/.env`:
- Backend services are configured to connect to:
  - Core Service: `http://localhost:8001`
  - Knowledge Service: `http://localhost:8002`

### Port Configuration
- Default Streamlit port: **8501**
- Can be changed in the Dockerfile or via command line:
  ```bash
  streamlit run app_streamlit.py --server.port=8080
  ```

## Dependencies

Updated `requirements.txt` includes:
- `streamlit>=1.32.0` - Main framework
- `plotly>=5.22.0` - Interactive charts
- `pandas>=2.0.0` - Data manipulation
- `httpx>=0.27.0` - HTTP client for API calls
- `python-dotenv>=1.0.0` - Environment configuration

## Why Streamlit?

| Feature | Benefit |
|---------|---------|
| **Navigation** | Callback-based | Session state + rerun |
| **Styling** | Custom CSS in Python | Markdown + Custom CSS |
| **Interactivity** | Callbacks | Direct Python execution |
| **State Management** | dcc.Store | st.session_state |
| **Deployment** | Gunicorn/Waitress | Built-in server |
| **Learning Curve** | Moderate | Easy |

## Advantages of Streamlit

1. **Simpler Code**: More Pythonic, less boilerplate
2. **Faster Development**: Rapid prototyping and iteration
3. **Better UX**: Modern, responsive interface out of the box
4. **Easier Deployment**: Built-in server, cloud deployment options
5. **Active Community**: Large ecosystem of components and extensions

## Service Health Monitoring

The sidebar displays real-time status of backend services:
- 🟢 Green dot = Service online
- 🔴 Red dot = Service offline

## Troubleshooting

### Services Not Connecting
1. Ensure Core service is running on port 8001
2. Ensure Knowledge service is running on port 8002
3. Check `.env` file configuration

### Port Already in Use
```bash
# Kill process on port 8501
# Windows
netstat -ano | findstr :8501
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8501 | xargs kill -9
```

### Dependencies Not Found
```bash
pip install -r requirements.txt
```

## Migration Notes

## Frontend Architecture

The Streamlit app provides:
- Clean, modern UI with minimal code
- Run it with: `python app.py`
- It will start on port 8050

Both frontends can coexist and connect to the same backend services.

## Future Enhancements

Potential improvements for the Streamlit version:
- [ ] Add authentication/authorization
- [ ] Implement file upload for data ingestion
- [ ] Add export functionality for reports
- [ ] Create custom Streamlit components for graph visualization
- [ ] Add real-time streaming for long-running queries
- [ ] Implement caching for better performance

## Support

For issues or questions:
1. Check backend service logs
2. Verify environment configuration
3. Review Streamlit documentation: https://docs.streamlit.io