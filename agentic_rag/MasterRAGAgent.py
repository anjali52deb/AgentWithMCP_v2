from rag_controller import MasterRAGAgent

query = "What is the new MongoDB index configuration update?"
agent = MasterRAGAgent(embedding_provider="gpt")
response = agent.run(query=query, mode="auto")

print("🔍 Final Answer:", response)



agent = MasterRAGAgent()
agent.run(file="docs/user_manual.pdf")
