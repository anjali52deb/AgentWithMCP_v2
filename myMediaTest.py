
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    from types import SimpleNamespace
    from base64 import b64encode
    import mimetypes
    load_dotenv()

    GEMINI_KEY = os.getenv("GEMINI_API_KEY")
    OPENAI_KEY = os.getenv("OPENAI_API_KEY")

    print("\n=== Testing Gemini Model Conversation ===")
    session_id = "test_session_456"

    # 📎 Simulate uploading a file (image/pdf/csv)
    file_path = "sample.pdf"  # ✅ Change to your test file name
    user_input = "Hi there!, Please analyze this attached file."
    
    # file_path = "D:\MyDownloads\Low-Res_EN-Slide2.jpg"  
    # user_input = "Hi there!, Please analyze this attached file."
    
    # file_path = "D:\_ _GenAI-and-ML\Datafiles\MiscDataset\sales-data-sample.csv" 
    # user_input = "What insights can you draw from this sales dataset?"
    # file_path = "D:\__Azure Training(Office)\DataBricks-Workshop-11Aug2021\Azure Databricks Hands-on Lab Guide.pdf" 
    # # user_input = "Summarize my resume and identify skills listed." 

    # file_path = "D:\MyDownloads\LLM_Flow_Send_to_Response.docx" 
    # user_input = "Summarize the main points of this business proposal."

    # file_path = "D:\__AZURE\__Project_Azure_Stream\TelcoEventData.json"
    # user_input = "Please describe the data schema and key-value structure in this file."

    # file_path = "E:\AgentWithMCP_v1\datastore\PurchaseOrders.xml"
    # user_input = "Explain the structure and list top-level elements in this XML file."

    # file_path = "D:\__AZURE\PowerBI-ALL\PowerBI ALL.pptx"
    # user_input = "Extract the key messages from this company presentation."

    # file_path = "D:\MyDownloads\Car-Lease-vs-Buying.xlsx"
    # user_input = "What kind of financial data is captured here?"

    # file_path = "D:\MyDownloads\AzureFunctionStarterProject.zip"
    # user_input = "List the contents of this archive and describe what type of files it contains."
    
    # ==================================================================
    # # ✅ Update path to your test video
    # file_path = r"E:\Training Materials\Azure Udemy Training\Udemy - AZ-300 Azure Architecture Technologies Certification Exam\33. 70-535 2018 Edition - Hybrid Applications\1. Introduction to Hybrid Applications.mp4"
    # file_path = r"E:\Training Materials\Azure Udemy Training\Udemy - AZ-300 Azure Architecture Technologies Certification Exam\59. Wrapping Up and Errata\1. Thank You!.mp4"
    # user_input = "summarize this video in 10 line"

    # # ✅ Update path to your test audio
    file_path = r"E:\__Test_Files_For_AgenticAI\audio-video\11 Adele - Someone Like You.mp3"
    file_path = r"E:\__Test_Files_For_AgenticAI\audio-video\Jai Ho.mp3"
    user_input = "I want to know lyrics and chords from this song"
    
    # ==================================================================
    file_name = os.path.basename(file_path)
    mime_type, _ = mimetypes.guess_type(file_path)

    with open(file_path, "rb") as f:
        encoded = b64encode(f.read()).decode("utf-8")
        data_url = f"data:{mime_type};base64,{encoded}"

    from types import SimpleNamespace
    attachment = SimpleNamespace(
        filename=file_name,
        dataUrl=data_url
    )

    agent_request = SimpleNamespace(
        session_id=session_id,
        query=user_input,
        model="gemini",
        attachments=[attachment]
    )

    response = invoke_langchain(agent_request)
    print("\n🧠 LLM Response:\n", response)
    print("\n✅ Testing completed.")

# =====================================================
# for YOUTUE ONLY
# =====================================================
# if __name__ == "__main__":
#     import os
#     import re
#     from dotenv import load_dotenv
#     from types import SimpleNamespace
#     load_dotenv()
#     GEMINI_KEY = os.getenv("GEMINI_API_KEY")
#     OPENAI_KEY = os.getenv("OPENAI_API_KEY")

#     print("\n=== Testing Gemini Model with YouTube Link ===")
#     session_id = "test_session_youtube"
#     user_input = "May I know lyrics of this YouTube video: https://www.youtube.com/watch?v=jUrKa6thMCU "
#     # user_input = "May I know lyrics of this Hindi YouTube video: https://www.youtube.com/watch?v=qgDTT2E3lSQ "
#     # user_input = "May I know lyrics of this Bengali YouTube video: https://www.youtube.com/watch?v=DGc0o4YI6xk "
    
#     # 🧪 Create request with no attachments — only a query containing a YouTube URL
#     agent_request = SimpleNamespace(
#         session_id=session_id,
#         query=user_input,
#         model="gemini",
#         attachments=[]
#     )
#     response = invoke_langchain(agent_request)
#     print("\n🧠 LLM Response:\n", response)
#     print("\n✅ YouTube test completed.")
