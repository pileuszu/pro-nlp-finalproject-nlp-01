try:
    from gitingest import ingest
    print("gitingest imported successfully")
except ImportError:
    print("gitingest not installed")
    exit(1)

url = "https://github.com/pileuszu/chzzk-stream-deck"
try:
    print(f"Testing ingest on {url} with max_size=10240")
    # Using the signature from _fetch_repo_deep
    summary, tree, content = ingest(
        url,
        max_size=10240,
        exclude_patterns=["*.json", "*.lock", "node_modules"]
    )
    print(f"Summary Type: {type(summary)}")
    print(f"Tree Type: {type(tree)}")
    print(f"Content Type: {type(content)}")
    print(f"Tree Length: {len(tree)}")
    print(f"Content Length: {len(content)}")
    print("-" * 20)
    print("Tree Sample:")
    print(tree[:200])
    print("-" * 20)
    print("Content Sample:")
    print(content[:200])

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
