# Day 10 — Assignment

## Instructions

Build and deploy a complete RAG application with FastAPI backend and Streamlit frontend. This is your final project! Install required libraries:

```bash
pip install fastapi uvicorn streamlit requests python-multipart
```

**Important:**
- Build backend first
- Then build frontend
- Test locally
- Deploy to cloud
- Document everything

---

## Tasks

### Task 1: FastAPI Backend

Create a complete FastAPI backend `rag_api.py`:

**Endpoints:**
1. `GET /` - Root endpoint
2. `GET /health` - Health check
3. `POST /index` - Index document (file upload)
4. `POST /query` - Query RAG system
5. `GET /stats` - Get statistics
6. `DELETE /documents/{doc_id}` - Remove document

**Requirements:**
- Use Pydantic models for requests/responses
- Handle file uploads
- Integrate your RAG system
- Add error handling
- Include API documentation

**Test with:** Postman or curl, against the same corpus you have used all week.
Index `../RAG assets/documents/` (61 files) plus
`../RAG assets/sample_rag_manual.pdf` for the upload endpoint, and drive
`POST /query` from `../RAG assets/test_queries.txt`.

Include the four `unanswerable` questions from
`../RAG assets/evaluation_questions.json` in your manual testing — an endpoint that
returns a confident answer with no sources for those is the failure mode most worth
catching before deploying.

**Deliverable:** `task1_fastapi_backend.py`

---

### Task 2: Streamlit Frontend

Create a Streamlit frontend `rag_ui.py`:

**Features:**
1. Document upload section
2. Query interface
3. Answer display
4. Source display
5. Statistics view
6. Chat history (optional)

**Requirements:**
- Connect to FastAPI backend
- Handle errors gracefully
- Add loading states
- Make it user-friendly
- Add styling

**Deliverable:** `task2_streamlit_frontend.py`

---

### Task 3: Complete Integration

Integrate backend and frontend `complete_app.py`:

**Features:**
1. Working API
2. Working UI
3. Full integration
4. Error handling
5. User feedback

**Requirements:**
- Test all features
- Handle edge cases
- Add validation
- Improve UX

**Deliverable:** `task3_complete_app/` (folder with both files)

---

### Task 4: Deployment Preparation

Prepare for deployment:

**Tasks:**
1. Create `requirements.txt`
2. Create `Dockerfile`
3. Create `docker-compose.yml`
4. Add environment variable handling
5. Create deployment documentation

**Requirements:**
- All dependencies listed
- Docker setup working
- Environment variables documented
- Deployment guide written

**Deliverable:** Deployment files + documentation

---

### Task 5: Cloud Deployment

Deploy to a cloud platform:

**Options:**
- Heroku
- Railway
- Render
- AWS/GCP/Azure (advanced)

**Requirements:**
- Deploy backend API
- Deploy frontend (or serve from backend)
- Test deployed version
- Document deployment process

**Deliverable:** Deployed application + deployment guide

---

## One Mini Project

### 🚀 Build and Deploy a Complete RAG Application

Create a production-ready RAG application with full-stack implementation.

**Features:**

1. **FastAPI Backend:**
   - Complete REST API
   - Document management
   - Query endpoints
   - Authentication (optional)
   - Rate limiting (optional)
   - CORS configuration
   - API documentation

2. **Streamlit Frontend:**
   - Modern, clean UI
   - Document upload
   - Interactive query interface
   - Answer display with formatting
   - Source citations
   - Chat history
   - Settings panel
   - Statistics dashboard

3. **Complete Features:**
   - Multiple document support
   - Document management (add/remove)
   - Query history
   - Export results
   - Configuration options
   - Error handling
   - Loading states
   - User feedback

4. **Deployment:**
   - Docker containerization
   - Environment configuration
   - Cloud deployment
   - Health checks
   - Monitoring (optional)

5. **Documentation:**
   - API documentation (auto-generated)
   - User guide
   - Deployment instructions
   - README with setup
   - Architecture diagram

**Project Structure:**
```
rag_application/
├── backend/
│   ├── main.py (FastAPI)
│   ├── rag_system.py
│   └── models.py
├── frontend/
│   └── app.py (Streamlit)
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── README.md
└── DEPLOYMENT.md
```

**Requirements:**
- Production-ready code
- Comprehensive error handling
- User-friendly interface
- Well-documented
- Deployed and accessible
- Tested thoroughly

**Example Usage:**
```bash
# Backend
cd backend
uvicorn main:app --reload

# Frontend
cd frontend
streamlit run app.py

# Or with Docker
docker-compose up
```

**Deliverables:**
- Complete application code
- Docker setup
- Deployment configuration
- Comprehensive documentation
- Deployed application (URL)
- Demo video/screenshots (optional)

---

## Expected Output Section

### Task 1 Expected Output:
```bash
# Start API
uvicorn rag_api:app --reload

# Test endpoint
curl http://localhost:8000/health
# {"status":"healthy"}

# Index document
curl -X POST http://localhost:8000/index \
  -F "file=@../RAG assets/sample_rag_manual.pdf"

# Query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is retrieval-augmented generation?", "k": 3}'
```

### Task 2 Expected Output:
```
Streamlit app running at http://localhost:8501

Features visible:
- File upload widget
- Query input
- Answer display area
- Sources section
- Statistics panel
```

### Task 3 Expected Output:
```
Complete integrated application:
- Backend API running on :8000
- Frontend UI running on :8501
- Full functionality working
- Error handling in place
- User-friendly interface
```

### Task 5 Expected Output:
```
Deployed application:
- Backend: https://your-app.herokuapp.com
- Frontend: https://your-app.herokuapp.com (or separate)
- API docs: https://your-app.herokuapp.com/docs
- Health: https://your-app.herokuapp.com/health
```

### Mini Project Expected Output:

The complete application should be:
- Fully functional
- Well-designed UI
- Production-ready
- Deployed and accessible
- Well-documented

**Example screens:**
```
┌─────────────────────────────────┐
│  🤖 RAG Application             │
├─────────────────────────────────┤
│  📄 Upload Documents            │
│  [Choose File] [Index]           │
├─────────────────────────────────┤
│  💬 Ask a Question              │
│  [Input box]                    │
│  [Ask Button]                   │
├─────────────────────────────────┤
│  📝 Answer                      │
│  [Generated answer displayed]   │
├─────────────────────────────────┤
│  📚 Sources                     │
│  [Source 1] [Source 2] [Source 3]│
└─────────────────────────────────┘
```

---

## Submission Checklist

- [ ] Task 1: FastAPI backend complete
- [ ] Task 2: Streamlit frontend complete
- [ ] Task 3: Integration working
- [ ] Task 4: Deployment files ready
- [ ] Task 5: Deployed to cloud
- [ ] Mini project: Complete application
- [ ] All endpoints tested
- [ ] UI is user-friendly
- [ ] Documentation complete
- [ ] Application deployed and accessible

**Final Checklist:**
- [ ] Code is production-ready
- [ ] Error handling comprehensive
- [ ] Documentation is complete
- [ ] Application is deployed
- [ ] README is informative
- [ ] You're proud of your work! 🎉

**Congratulations on completing the 10-day RAG roadmap!** 🎊🚀

**Good luck with your deployment!** 🌟

