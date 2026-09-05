import os
import shutil
from core.rag import build_index, search, clear_session
from core.config import load_config, get_ollama_options, set_mem_percent
from core.orchestrator import run_agent, get_model_map, classify_task
from core.memory_manager import check_and_consolidate
from core.model_registry import discover_models

def setup_test_env():
    test_dir = "test_workspace_temp"
    os.makedirs(test_dir, exist_ok=True)
    with open(f"{test_dir}/dummy_config.py", "w") as f:
        f.write("MAX_RAM = 40\nDEBUG = True\n# This is a dummy config file for memory throttling tests.\n")
    with open(f"{test_dir}/dummy_manual.md", "w") as f:
        f.write("# User Manual\n\nTo configure memory throttling, adjust the MAX_RAM variable.\n\nIt restricts context windows.")
    print(f"Setup: Created test directory '{test_dir}' with dummy files.")
    return test_dir

def teardown_test_env(test_dir, project_id):
    print("\n=== Cleaning Up Test Environment ===")
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
        print(f"Teardown: Deleted directory '{test_dir}'")
    db_path = f"memory/{project_id}.db"
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Teardown: Deleted database '{db_path}'")

def run_debug_tests():
    project_id = "debug_test_123"
    test_dir = setup_test_env()
    db_path = f"memory/{project_id}.db"
    
    try:
        print("\n=== 0. Testing Model Registry & Mapping ===")
        discovered = discover_models()
        print(f"Discovered {len(discovered)} models via Ollama API:")
        for m in discovered:
            print(f"  - {m['name']} (Guessed Role: {m['guessed_capability']})")
            
        dynamic_map = get_model_map()
        print(f"\nFinal Active Model Routing Map:\n{dynamic_map}\n")

        print("=== 1. Testing Config & Options ===")
        set_mem_percent(40)
        cfg = load_config()
        print(f"Loaded config: {cfg}")
        opts = get_ollama_options()
        print(f"Ollama options derived from RAM budget: {opts}\n")

        print("=== 2. Testing RAG Indexing ===")
        indexed_count = build_index(directory=test_dir, db_path=db_path, on_progress=print)
        print(f"Stored chunks: {indexed_count}\n")

        print("=== 3. Testing Agent Loop & Tool Execution ===")
        prompt = "Search the knowledge base for memory throttling and summarize it."
        result = run_agent(prompt, project_id=project_id)
        print(f"Agent Status: {result.get('status')}")
        print(f"Agent Result:\n{result.get('result')}")
        
        print("\n=== 4. Testing Vision Fallback Rejection ===")
        # Manually force the orchestrator to think we uploaded an image
        print("Simulating image upload...")
        vision_result = run_agent("What is in this image?", project_id=project_id, image_path="dummy.jpg")
        print(f"Vision Rejection Result:\n{vision_result.get('result')}")

        print("\n=== 5. Testing Session Clearing ===")
        cleared_count = clear_session(db_path=db_path)
        print(f"Cleared {cleared_count} chat memory chunks.\n")

        print("=== 6. Testing Memory Consolidation Checker ===")
        check_and_consolidate(project_id=project_id)
        print("Memory consolidation check completed cleanly.\n")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
    finally:
        teardown_test_env(test_dir, project_id)

if __name__ == "__main__":
    run_debug_tests()
