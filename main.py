# main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from mcp_server.routes.auth_router import router as auth_router  
app.include_router(auth_router)

from mcp_server.routes.agent_router import router as agent_router
app.include_router(agent_router)

# from mcp_server.routes.protected_router import router as protected_router
# app.include_router(protected_router)

from mcp_server.routes.api_protected_router import router as protected_router
app.include_router(protected_router)

# from mcp_server.routes.gemini_media_router import router as gemini_media_router
# app.include_router(gemini_media_router, prefix="/media")


@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/version")
def version():
    return {"version": "1.0.0", "module": "MCP + Gemini Media Agent"}



### ---- for testing ----
if __name__ == "__main__":
    ##-------------------------------------------------------
    from models.llm import invoke_gtp, invoke_gemini
    ##-------------------------------------------------------

    # Local test block
    mainPrompt = "what special about Sunday as day?"
    mainSession = "session007"
    mainModel = 'gemini'

    class DummyRequest:
        session_id: str = mainSession
        query: str = mainPrompt
        model: str = mainModel

    dummy_request = DummyRequest()
    print("Gemini test:", invoke_gemini(dummy_request))
    # dummy_request.model = "gpt"
    # print("GPT test:", invoke_gtp(dummy_request))

    # To run the API server, uncomment below:
    # import uvicorn
    # uvicorn.run(app, host="0.0.0.0", port=8000)


######################################################################
