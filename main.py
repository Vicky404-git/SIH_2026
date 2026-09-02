from core.orchestrator import run_agent
from core.rag import build_index

def main():
    print("--- 1. Building Initial RAG Index ---")
    build_index(directory=".", on_progress=print)

    print("\n--- 2. Testing Orchestrator Routing & RAG ---")
    prompt = "How does config throttling work in this codebase?"
    
    res = run_agent(prompt)
    
    print("\n[RESULT]")
    if "error" in res:
        print(f"🚨 ERROR: {res['error']}")
    else:
        print(f"Task Type : {res.get('task_type')}")
        print(f"Model Used: {res.get('model_used')}")
        print(f"Sources   : {res.get('sources')}")
        print(f"Response  :\n{res.get('response')}")

if __name__ == "__main__":
    main()
