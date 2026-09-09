import os
import shutil
import base64
from core.rag import build_index, search, clear_session, ingest_text, get_db, _store_chunk
from core.config import load_config, get_ollama_options, set_mem_percent, get_background_job_percent
from core.orchestrator import run_agent, get_model_map, classify_task
from core.memory_manager import check_and_consolidate
from core.model_registry import discover_models
from core.doc_gen import docgen_tool

def setup_test_env():
    test_dir = "test_workspace_temp"
    os.makedirs(test_dir, exist_ok=True)
    
    # 1. Dummy config file for indexer
    with open(f"{test_dir}/dummy_config.py", "w") as f:
        f.write("MAX_RAM = 40\nDEBUG = True\n# Dummy config file.\n")
    
    # 2. Dummy markdown file for indexer
    with open(f"{test_dir}/dummy_manual.md", "w") as f:
        f.write("# User Manual\n\nTo configure memory throttling, adjust the MAX_RAM variable.")
    
    # 3. Create a REAL 1x1 pixel PNG image for vision testing
    tiny_png = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=")
    img_path = f"{test_dir}/tiny.png"
    with open(img_path, "wb") as f:
        f.write(tiny_png)
        
    print(f"Setup: Created test directory '{test_dir}' with dummy files and a valid tiny.png.")
    return test_dir, img_path

def teardown_test_env(test_dir, project_id):
    print("\n=== Cleaning Up Test Environment ===")
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
        print(f"Teardown: Deleted directory '{test_dir}'")
    db_path = f"memory/{project_id}.db"
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Teardown: Deleted database '{db_path}'")
    
    # Cleanup any stray docx files generated in the root
    for file in os.listdir("."):
        if file.endswith(".docx") and file.startswith("tmp"):
            os.remove(file)

def run_all_tests():
    project_id = "debug_full_123"
    test_dir, img_path = setup_test_env()
    db_path = f"memory/{project_id}.db"
    
    try:
        print("\n=== 1. Testing Config & Model Registry ===")
        set_mem_percent(40)
        print(f"Ollama Options: {get_ollama_options()}")
        print(f"Background Job Throttle: {get_background_job_percent()}%")
        
        discovered = discover_models()
        print(f"\nDiscovered {len(discovered)} models:")
        for m in discovered:
            print(f"  - {m['name']} -> {m['guessed_capability']}")
        print(f"Routing Map: {get_model_map()}")

        print("\n=== 2. Testing Task Classification ===")
        print(f"Code Prompt -> {classify_task('Write a python script')[0]}")
        print(f"Image Prompt -> {classify_task('What is this?', has_image=True)[0]}")
        print(f"General Prompt -> {classify_task('Explain history')[0]}")

        print("\n=== 3. Testing RAG (Bulk Index & Dynamic Ingest) ===")
        indexed = build_index(directory=test_dir, db_path=db_path)
        print(f"Bulk indexed {indexed} chunks.")
        
        ingested = ingest_text("This is dynamically uploaded text from the UI.", "dynamic_upload.txt", db_path=db_path)
        print(f"Dynamically ingested {ingested} chunks.")
        
        hits = search("memory throttling", top_k=1, db_path=db_path)
        print(f"Search Hit: {hits[0][1]['file']} (Distance: {hits[0][0]:.3f})" if hits else "Search Hit: None")

        print("\n=== 4. Testing DocGen Tool (Pandoc Dependency Check) ===")
        # Testing the tool directly to ensure OS-level Pandoc doesn't crash
        doc_res = docgen_tool.fn("# Hello\nThis is a test doc.")
        print(f"DocGen OK? {doc_res.ok}")
        if doc_res.ok:
            print(f"Output saved to: {doc_res.output}")
        else:
            print(f"DocGen FAILED (Is Pandoc installed?): {doc_res.output}")

        print("\n=== 5. Testing Agent Loop (Reasoning + Tool Use) ===")
        prompt = "Search the knowledge base for memory throttling and summarize it."
        result = run_agent(prompt, project_id=project_id)
        print(f"Agent Status: {result.get('status')}")
        print(f"Steps taken: {len(result.get('trace', []))}")

        print("\n=== 6. Testing Agent Loop (Vision Path) ===")
        vis_result = run_agent("Describe this image.", project_id=project_id, image_path=img_path)
        print(f"Vision Response (or Rejection): {vis_result.get('result')[:150]}...")

        print("\n=== 7. Testing Memory Consolidation (Forcing >50 messages) ===")
        # Artificially inject 51 fake chat messages to trigger the actual LLM summarization
        db = get_db(db_path)
        try:
            for i in range(51):
                # Fake embeddings [0.0]*768 to bypass Ollama embedding calls for speed
                _store_chunk(db, "chat:default", f"User: t{i}\nAssistant: t{i}", "chat", [0.0]*768)
            db.commit()
        finally:
            db.close()
        
        print("Injected 51 messages. Running check_and_consolidate()...")
        check_and_consolidate(project_id=project_id)
        
        # Verify chats were wiped and summarized
        db = get_db(db_path)
        chat_count = db.execute("SELECT COUNT(*) as cnt FROM chunks WHERE source_type = 'chat'").fetchone()["cnt"]
        summary_count = db.execute("SELECT COUNT(*) as cnt FROM chunks WHERE source_type = 'doc' AND file_path LIKE 'summary:%'").fetchone()["cnt"]
        db.close()
        
        print(f"Chats remaining after consolidation: {chat_count} (Should be 0)")
        print(f"Summary documents created: {summary_count} (Should be 1)")
        
    except Exception as e:
        import traceback
        print(f"\n❌ TEST FAILED: {e}")
        traceback.print_exc()
    finally:
        teardown_test_env(test_dir, project_id)

if __name__ == "__main__":
    run_all_tests()
