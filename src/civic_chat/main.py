"""Civic Chat - Simple chat interface with persistent conversation threads."""

import asyncio
from civic_chat.workflows import create_agents_orchestration
from civic_chat.config.settings import validate_config
from civic_chat.agents.memory.thread_manager import ThreadManager


async def get_workflow_response_stream(workflow, user_input, thread=None):
    """Get workflow response with streaming from SwitchCase orchestration.
    
    Args:
        workflow: The SwitchCase workflow instance
        user_input: User's message
        thread: Optional AgentThread for conversation continuity
    """
    try:
        from agent_framework import WorkflowOutputEvent, AgentRunUpdateEvent
        
        print("\n🤖 Assistant: ", end="", flush=True)
        
        has_streamed = False
        
        # Run with thread if provided
        if thread:
            async for event in workflow.run_stream(user_input, thread=thread):
                if isinstance(event, AgentRunUpdateEvent):
                    # Skip events from the IntentClassifier
                    if hasattr(event, 'executor_id') and event.executor_id == "IntentClassifier":
                        continue
                    
                    if hasattr(event, 'data') and event.data:
                        # Extract text from AgentRunResponseUpdate
                        if hasattr(event.data, 'text') and event.data.text:
                            print(event.data.text, end="", flush=True)
                            has_streamed = True
        else:
            async for event in workflow.run_stream(user_input):
                if isinstance(event, AgentRunUpdateEvent):
                    # Skip events from the IntentClassifier
                    if hasattr(event, 'executor_id') and event.executor_id == "IntentClassifier":
                        continue
                    
                    if hasattr(event, 'data') and event.data:
                        # Extract text from AgentRunResponseUpdate
                        if hasattr(event.data, 'text') and event.data.text:
                            print(event.data.text, end="", flush=True)
                            has_streamed = True
        
        # Only add newline if we streamed something
        if has_streamed:
            print()
        
        return True
        
    except asyncio.TimeoutError:
        print("\n⏱️  Request timeout. Please try again.")
        return False
    except asyncio.CancelledError:
        # Handle user interruption gracefully
        return False
    except KeyboardInterrupt:
        # Handle Ctrl+C during streaming
        return False
    except Exception as e:
        print(f"\n⚠️  Error: {e}")
        return False

async def chat_loop():
    """Main chat interaction loop with persistent conversation threads."""
    print("🏛️  Civic Chat")
    print("Type 'exit' or 'salir' to quit\n")
    
    # Generate unique user ID (in production, from authentication)
    import uuid
    user_id = f"user_{str(uuid.uuid4())[:8]}"
    print(f"Session ID: {user_id}\n")
    
    # Initialize thread manager
    thread_manager = ThreadManager(user_id=user_id)
    thread = None
    
    try:
        # Initialize the workflow with error handling
        try:
            workflow = await create_agents_orchestration(user_id=user_id)
            print("✅ System ready!\n")
            
        except Exception as e:
            print(f"\n❌ Failed to initialize system: {e}")
            return

        while True:
            try:
                user_input = input("\n👤 You: ").strip()
                
                if user_input.lower() in ['exit', 'salir']:
                    print("\n👋 Goodbye!")
                    break
                
                if user_input.lower() == 'reset':
                    print("🔄 Memory reset not available in this version\n")
                    continue
                    
                if not user_input:
                    continue
                
                # Get response from SwitchCase workflow
                # Note: Thread persistence for workflows is complex with SwitchCase
                # For now, we rely on the memory_manager for user context
                try:
                    await get_workflow_response_stream(workflow, user_input, thread=None)
                except (KeyboardInterrupt, asyncio.CancelledError):
                    print("\n\n👋 Goodbye!")
                    break
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except EOFError:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n⚠️  Error: {e}")
                continue
                
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Please check your configuration and try again.")
    finally:
        # Cleanup
        if 'workflow' in locals() and hasattr(workflow, 'close'):
            await workflow.close()


def main():
    """Start the chat application."""
    try:
        # Validate configuration
        validate_config()
        
        # Run the chat loop
        asyncio.run(chat_loop())
        
    except ValueError as e:
        print(f"\n❌ Configuration error: {e}")
        print("Please check your .env file and ensure all required variables are set.")
        return 1
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())