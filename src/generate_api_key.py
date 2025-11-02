#!/usr/bin/env python3
"""
Generate and test VLLM API keys
"""

import secrets
import sys
import os
from pathlib import Path


def generate_key():
    """Generate a secure API key"""
    return secrets.token_urlsafe(32)


def create_env_file(api_key):
    """Create .env file with API key"""
    env_path = Path(__file__).parent / ".env"
    
    if env_path.exists():
        print(f"⚠️  .env file already exists")
        response = input("Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Cancelled")
            return False
    
    with open(env_path, 'w') as f:
        f.write(f"# VLLM API Key\n")
        f.write(f"# Generated: {__import__('datetime').datetime.now().isoformat()}\n")
        f.write(f"VLLM_API_KEY={api_key}\n")
    
    print(f"✅ Created .env file")
    return True


def test_key(port=8001):
    """Test API key with running agent"""
    import subprocess
    
    api_key = os.getenv("VLLM_API_KEY")
    if not api_key:
        print("❌ VLLM_API_KEY not set in environment")
        print("Run: source .env")
        return False
    
    print(f"\n🧪 Testing API key with agent on port {port}...")
    
    # Test without key (should fail)
    print("\n1️⃣ Testing WITHOUT key (should fail)...")
    result = subprocess.run(
        ["curl", "-s", f"http://localhost:{port}/v1/models"],
        capture_output=True,
        text=True
    )
    
    if "401" in result.stdout or "Unauthorized" in result.stdout:
        print("   ✅ Correctly rejected request without key")
    else:
        print("   ⚠️  Warning: Agent may not have authentication enabled")
    
    # Test with key (should work)
    print("\n2️⃣ Testing WITH key (should work)...")
    result = subprocess.run(
        [
            "curl", "-s",
            "-H", f"Authorization: Bearer {api_key}",
            f"http://localhost:{port}/v1/models"
        ],
        capture_output=True,
        text=True
    )
    
    if "error" in result.stdout.lower() or "401" in result.stdout:
        print("   ❌ Authentication failed")
        print(f"   Response: {result.stdout[:200]}")
        return False
    elif '"object": "list"' in result.stdout:
        print("   ✅ Authentication successful!")
        return True
    else:
        print("   ⚠️  Agent may not be running")
        print("   Start with: python3 setup.py start dev")
        return False


def show_usage_examples(api_key):
    """Show usage examples"""
    print("\n" + "="*60)
    print("📚 Usage Examples")
    print("="*60)
    
    print("\n1️⃣ Export to environment:")
    print(f"   export VLLM_API_KEY='{api_key}'")
    
    print("\n2️⃣ Use with cURL:")
    print(f"""   curl http://localhost:8001/v1/chat/completions \\
     -H "Authorization: Bearer {api_key}" \\
     -H "Content-Type: application/json" \\
     -d '{{"model":"dev","messages":[{{"role":"user","content":"Hello"}}]}}'""")
    
    print("\n3️⃣ Use with Python:")
    print(f"""   import os
   from openai import OpenAI
   
   client = OpenAI(
       base_url="http://localhost:8001/v1",
       api_key="{api_key}"
   )
   
   response = client.chat.completions.create(
       model="dev",
       messages=[{{"role": "user", "content": "Hello"}}]
   )""")
    
    print("\n4️⃣ Load from .env file:")
    print("""   # In your Python code
   import os
   from dotenv import load_dotenv
   
   load_dotenv()
   api_key = os.getenv("VLLM_API_KEY")""")
    
    print("\n" + "="*60)


def main():
    print("🔑 VLLM API Key Generator\n")
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Test mode
        if not os.getenv("VLLM_API_KEY"):
            print("❌ VLLM_API_KEY not set")
            print("Run: source .env")
            sys.exit(1)
        
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 8001
        test_key(port)
        sys.exit(0)
    
    print("1. Generate new API key")
    print("2. View existing key")
    print("3. Test API key")
    print("4. Exit")
    
    choice = input("\nChoice (1-4): ").strip()
    
    if choice == "1":
        # Generate new key
        print("\n🔐 Generating secure API key...")
        api_key = generate_key()
        
        print(f"\n✅ Generated API key:")
        print(f"   {api_key}")
        
        save = input("\n💾 Save to .env file? (Y/n): ").strip()
        if save.lower() != 'n':
            if create_env_file(api_key):
                print("\n📝 Next steps:")
                print("   1. Load environment: source .env")
                print("   2. Restart agents: docker compose restart")
                print("   3. Test: python3 generate_api_key.py test")
        else:
            print("\n⚠️  Remember to save this key!")
        
        show_usage_examples(api_key)
    
    elif choice == "2":
        # View existing
        env_path = Path(__file__).parent / ".env"
        if not env_path.exists():
            print("\n❌ No .env file found")
            print("Generate one with option 1")
        else:
            with open(env_path) as f:
                content = f.read()
            print(f"\n📄 Current .env file:")
            print(content)
            
            if "VLLM_API_KEY=" in content:
                key = content.split("VLLM_API_KEY=")[1].split("\n")[0].strip()
                show_usage_examples(key)
    
    elif choice == "3":
        # Test key
        env_path = Path(__file__).parent / ".env"
        if not env_path.exists():
            print("\n❌ No .env file found")
            sys.exit(1)
        
        print("\n💡 First load the environment:")
        print("   source .env")
        print("\nThen run:")
        print("   python3 generate_api_key.py test [port]")
        print("\nExample:")
        print("   python3 generate_api_key.py test 8001  # Test dev agent")
    
    elif choice == "4":
        print("\n👋 Goodbye!")
    
    else:
        print("\n❌ Invalid choice")


if __name__ == "__main__":
    main()
