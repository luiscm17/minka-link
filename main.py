#!/usr/bin/env python3
"""
Minka Link - Civic Chat Application

A free, multilingual, and neutral civic companion that empowers every citizen
with accessible democratic knowledge.

MVP Goal: Validate in NYC that civic education can be as easy as talking to
your phone in your native language.
"""

import asyncio
import sys
from pathlib import Path

# Agregar el directorio de agentes al path
sys.path.append(str(Path(__file__).parent / "agents"))

from agents.civic_orchestration import run_civic_chat, interactive_mode


def print_banner():
    """Prints welcome banner."""
    print("\n" + "=" * 80)
    print("MINKA LINK - Your Global Civic Companion")
    print("=" * 80)
    print("\nA free, multilingual, and neutral assistant for civic education.")
    print("Ask about voting, procedures, reports, or democratic concepts.")
    print("Works for any city or country.\n")


async def run_single_query(query: str):
    """
    Runs a single query and displays the result.
    
    Args:
        query: User query.
    """
    print_banner()
    response = await run_civic_chat(query, verbose=True)
    print("\n[OK] Query completed\n")


async def run_interactive():
    """Runs interactive mode."""
    print_banner()
    print("Type your queries and press Enter. Type 'exit' to quit.\n")
    await interactive_mode()


def print_help():
    """Prints usage help."""
    print("\n" + "=" * 80)
    print("MINKA LINK - Help")
    print("=" * 80)
    print("\nUsage:")
    print("  python main.py                    # Interactive mode")
    print("  python main.py -i                 # Interactive mode (explicit)")
    print('  python main.py "your query"       # Single query')
    print("  python main.py --help             # Show this help")
    print("\nExamples:")
    print('  python main.py "Where can I vote in Buenos Aires?"')
    print('  python main.py "I want to report a pothole in Madrid"')
    print('  python main.py "What is a city council member in NYC?"')
    print('  python main.py "Voting requirements in Mexico"')
    print("\nAvailable agents:")
    print("  - Civic Educator    : Civic concepts and democracy")
    print("  - Citizen Guide     : Practical info about procedures")
    print("  - Complaint Handler : Guide to report problems")
    print("  - Fact Checker      : Information verification")
    print("\nTip: Mention your city or country in the query for specific answers")
    print("\n" + "=" * 80 + "\n")


def main():
    """Main entry point."""
    
    # Parse simple arguments
    args = sys.argv[1:]
    
    # Show help
    if "--help" in args or "-h" in args:
        print_help()
        return
    
    # Interactive mode (default or with -i)
    if not args or "-i" in args or "--interactive" in args:
        try:
            asyncio.run(run_interactive())
        except KeyboardInterrupt:
            print("\n\n[EXIT] Goodbye\n")
        return
    
    # Single query
    query = " ".join(args)
    
    if not query.strip():
        print("[ERROR] You must provide a query.")
        print('        Example: python main.py "Where can I vote?"')
        print("        Or run without arguments for interactive mode.\n")
        return
    
    try:
        asyncio.run(run_single_query(query))
    except KeyboardInterrupt:
        print("\n\n[EXIT] Query cancelled\n")
    except Exception as e:
        print(f"\n[ERROR] {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
