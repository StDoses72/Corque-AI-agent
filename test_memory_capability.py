from core.agent import Agent
import time

def test_memory():
    print("Initializing Agent...")
    try:
        bot = Agent()
        
        # Test 1: Remember something
        print("\n--- Test 1: Saving Memory ---")
        query1 = "My name is doses72 and I prefer using Python for backend tasks. Please remember this preference."
        print(f"User: {query1}")
        response1 = bot.ask(query1, threadId="test_thread_1", interactive=False)
        print(f"Corque: {response1}")

        # Test 2: Recall it (simulating a new thread/session by changing threadId or just asking)
        print("\n--- Test 2: Recalling Memory ---")
        query2 = "What is my preferred backend language?"
        print(f"User: {query2}")
        response2 = bot.ask(query2, threadId="test_thread_2", interactive=False)
        print(f"Corque: {response2}")

    except Exception as e:
        print(f"\nCRITICAL ERROR DURING EXECUTION:\n{e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_memory()
