import os
import yaml
import argparse
import json
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables (OPENAI_API_KEY)
load_dotenv()

client = OpenAI()

def load_blueprint(filepath: str) -> dict:
    with open(filepath, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def run_agent(name, role, goal, instructions, context=""):
    print(f"Agent: {name} ({role}) is working...")
    
    prompt = f"""
    Role: {role}
    Goal: {goal}
    Instructions: {instructions}
    
    Context from previous steps:
    {context}
    
    Please provide your output based on the instructions above.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a specialized agent within The Beast orchestration framework."},
                {"role": "user", "content": prompt}
            ]
        )
        output = response.choices[0].message.content
        print(f"DONE: {name} completed their task.\n")
        return output
    except Exception as e:
        err_str = str(e).lower()
        print(f"ERROR: Agent execution failed: {err_str}")
        if "429" in err_str or "quota" in err_str or "too many requests" in err_str:
            return "🔴 QUOTA EXCEEDED (429). This mission requires more AI oxygen than your current account allows. Please check your billing or use a local LLM."
        return f"Error: {str(e)}"

def run_blueprint(filepath: str):
    blueprint = load_blueprint(filepath)
    print(f"Initializing Sovereign Orchestration: {blueprint.get('name', 'Unknown')}")
    print(f"Description: {blueprint.get('description', '')}\n")
    
    orch_data = blueprint.get('orchestrator', {})
    sub_agents_data = blueprint.get('sub_agents', [])
    
    results = []
    
    # 1. Run Sub-Agents
    for sa in sub_agents_data:
        res = run_agent(
            name=sa.get('name', 'Specialist'),
            role=sa.get('capability', 'Expert'),
            goal=f"Execute tasks related to {sa.get('capability', 'general')}.",
            instructions=sa.get('instructions', 'Do the work.')
        )
        results.append(f"Result from {sa.get('name')}:\n{res}")
    
    # 2. Run Integration (Orchestrator)
    context = "\n\n".join(results)
    final_result = run_agent(
        name="Orchestrator",
        role=orch_data.get('agent', 'Manager'),
        goal="Integrate all findings into a final Sovereign Report.",
        instructions=orch_data.get('instructions', 'Synthesize the work.'),
        context=context
    )
    
    print("\n==================================")
    print("SOVEREIGN EXECUTION FINAL RESULT")
    print("==================================")
    print(final_result)
    
    # Save the result to a file
    output_file = "orchestration_result.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(final_result)
    print(f"\nFinal report saved to {output_file}")
    
    return final_result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="The BEAST - Sovereign Orchestrator (Lightweight)")
    parser.add_argument("blueprint", type=str, help="Path to the .yaml.txt blueprint file")
    args = parser.parse_args()
    
    if not os.path.exists(args.blueprint):
        print(f"❌ Error: Blueprint file {args.blueprint} not found.")
        exit(1)
        
    run_blueprint(args.blueprint)
