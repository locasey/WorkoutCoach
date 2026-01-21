#!/usr/bin/env python3
"""
Workout Plan Evaluation Script

Runs standard test prompts against the LLM service and saves results
with quality scores for comparison.

Usage:
    # Run all prompts with Gemini (default)
    python scripts/evaluate_prompts.py --version v1_baseline

    # Run with specific provider and model
    python scripts/evaluate_prompts.py --version v1_baseline --provider openai --model gpt-4o

    # Run single prompt
    python scripts/evaluate_prompts.py --version v1_baseline --prompt 5k_8week

    # List available prompts
    python scripts/evaluate_prompts.py --list
"""

import os
import sys
import json
import argparse
import time
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from dotenv import load_dotenv
    # Load environment variables from .env file
    load_dotenv(Path(__file__).parent.parent / '.env')
except ImportError:
    # dotenv not available, assume env vars are set externally
    pass


def get_llm_service(provider: str = None, model: str = None):
    """
    Get an LLM service instance with optional provider/model override.

    Args:
        provider: Override provider ('gemini' or 'openai')
        model: Override model name

    Returns:
        Configured LLMService instance
    """
    # Temporarily override environment variables if specified
    original_provider = os.environ.get('LLM_PROVIDER')
    original_gemini_model = os.environ.get('GEMINI_MODEL')

    try:
        if provider:
            os.environ['LLM_PROVIDER'] = provider

        if model:
            if provider == 'gemini' or (not provider and os.environ.get('LLM_PROVIDER', 'gemini') == 'gemini'):
                os.environ['GEMINI_MODEL'] = model

        # Import after setting env vars
        from services.llm_service import LLMService
        service = LLMService()

        # Get actual model name for Gemini
        actual_model = model
        if service.provider == 'gemini' and not model:
            actual_model = os.environ.get('GEMINI_MODEL', 'gemini-2.5-flash-lite')
        elif service.provider == 'openai' and not model:
            actual_model = service.model_name

        return service, actual_model
    finally:
        # Restore original values
        if original_provider is not None:
            os.environ['LLM_PROVIDER'] = original_provider
        elif 'LLM_PROVIDER' in os.environ and provider:
            del os.environ['LLM_PROVIDER']

        if original_gemini_model is not None:
            os.environ['GEMINI_MODEL'] = original_gemini_model
        elif 'GEMINI_MODEL' in os.environ and model:
            del os.environ['GEMINI_MODEL']


def load_test_prompts(prompts_file: Path = None) -> dict:
    """Load test prompts from JSON file."""
    if prompts_file is None:
        prompts_file = Path(__file__).parent.parent / 'tests' / 'evaluation' / 'test_prompts.json'

    with open(prompts_file, 'r') as f:
        return json.load(f)


def save_result(result: dict, version: str, provider: str, model: str, prompt_id: str):
    """
    Save evaluation result to JSON file.

    Saves to: results/<version>/<provider>_<model>/<prompt_id>_<timestamp>.json
    """
    results_dir = Path(__file__).parent.parent / 'tests' / 'evaluation' / 'results'

    # Sanitize model name for directory (replace / with _)
    safe_model = model.replace('/', '_').replace('\\', '_')

    # Create directory structure
    version_dir = results_dir / version / f"{provider}_{safe_model}"
    version_dir.mkdir(parents=True, exist_ok=True)

    # Create filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{prompt_id}_{timestamp}.json"
    filepath = version_dir / filename

    with open(filepath, 'w') as f:
        json.dump(result, f, indent=2, default=str)

    return filepath


def run_evaluation(
    prompt_data: dict,
    version: str,
    provider: str = None,
    model: str = None,
    verbose: bool = True
) -> dict:
    """
    Run evaluation for a single prompt.

    Args:
        prompt_data: Prompt dictionary with id, prompt, expected
        provider: LLM provider to use
        model: Model name to use
        version: Version label for this run
        verbose: Print progress messages

    Returns:
        Evaluation result dictionary
    """
    from tests.evaluation.quality_checker import check_plan_quality

    prompt_id = prompt_data['id']
    prompt_text = prompt_data['prompt']
    expected = prompt_data.get('expected', {})

    if verbose:
        print(f"\n{'='*60}")
        print(f"Evaluating: {prompt_id}")
        print(f"Prompt: {prompt_text}")
        print(f"{'='*60}")

    # Get LLM service
    llm_service, actual_model = get_llm_service(provider, model)
    actual_provider = llm_service.provider

    if verbose:
        print(f"Provider: {actual_provider}, Model: {actual_model}")

    # Generate plan and measure time
    start_time = time.time()
    try:
        plan = llm_service.generate_workout_plan(prompt_text)
        generation_time_ms = int((time.time() - start_time) * 1000)
        success = True
        error = None
    except Exception as e:
        generation_time_ms = int((time.time() - start_time) * 1000)
        plan = None
        success = False
        error = str(e)
        if verbose:
            print(f"ERROR: {error}")

    # Run quality checks if plan was generated
    quality_score = None
    if plan:
        quality_score = check_plan_quality(plan, expected)
        if verbose:
            print(f"\nQuality Score: {quality_score['overall_score']}/100")
            print(f"Passed: {quality_score['passed']}")
            if quality_score['issues']:
                print("Issues:")
                for issue in quality_score['issues']:
                    print(f"  - {issue}")

    # Build result
    result = {
        'prompt_id': prompt_id,
        'prompt_text': prompt_text,
        'expected': expected,
        'version': version,
        'provider': actual_provider,
        'model': actual_model,
        'timestamp': datetime.now().isoformat(),
        'generation_time_ms': generation_time_ms,
        'success': success,
        'error': error,
        'plan': plan,
        'quality_score': quality_score
    }

    # Save result
    filepath = save_result(result, version, actual_provider, actual_model, prompt_id)
    if verbose:
        print(f"\nResult saved to: {filepath}")

    return result


def list_prompts():
    """Print available test prompts."""
    prompts_data = load_test_prompts()
    print("\nAvailable test prompts:")
    print("-" * 50)
    for prompt in prompts_data['prompts']:
        print(f"\n  ID: {prompt['id']}")
        print(f"  Prompt: {prompt['prompt']}")
        if 'expected' in prompt:
            print(f"  Expected duration: {prompt['expected'].get('duration_weeks', 'N/A')} weeks")


def main():
    parser = argparse.ArgumentParser(
        description='Evaluate workout plan generation with standard prompts',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/evaluate_prompts.py --version v1_baseline
  python scripts/evaluate_prompts.py --version v1_baseline --provider gemini
  python scripts/evaluate_prompts.py --version v1_baseline --provider openai --model gpt-4o
  python scripts/evaluate_prompts.py --version v1_baseline --prompt 5k_8week
  python scripts/evaluate_prompts.py --list
        """
    )

    parser.add_argument('--version', '-v', type=str,
                        help='Version label for this evaluation run (e.g., v1_baseline)')
    parser.add_argument('--provider', '-p', type=str, choices=['gemini', 'openai'],
                        help='LLM provider to use (default: from env or gemini)')
    parser.add_argument('--model', '-m', type=str,
                        help='Model name (e.g., gemini-2.5-flash-lite, gpt-4o)')
    parser.add_argument('--prompt', type=str,
                        help='Run single prompt by ID (default: all prompts)')
    parser.add_argument('--all', action='store_true', default=True,
                        help='Run all prompts (default)')
    parser.add_argument('--list', '-l', action='store_true',
                        help='List available test prompts')
    parser.add_argument('--quiet', '-q', action='store_true',
                        help='Minimal output')

    args = parser.parse_args()

    if args.list:
        list_prompts()
        return 0

    if not args.version:
        print("Error: --version is required for evaluation runs")
        print("Use --list to see available prompts, or --help for usage")
        return 1

    # Load prompts
    prompts_data = load_test_prompts()
    prompts = prompts_data['prompts']

    # Filter to single prompt if specified
    if args.prompt:
        prompts = [p for p in prompts if p['id'] == args.prompt]
        if not prompts:
            print(f"Error: Prompt '{args.prompt}' not found")
            list_prompts()
            return 1

    verbose = not args.quiet

    if verbose:
        print(f"\nWorkout Plan Evaluation")
        print(f"Version: {args.version}")
        print(f"Provider: {args.provider or 'default'}")
        print(f"Model: {args.model or 'default'}")
        print(f"Prompts to run: {len(prompts)}")

    # Run evaluations
    results = []
    for prompt_data in prompts:
        result = run_evaluation(
            prompt_data=prompt_data,
            version=args.version,
            provider=args.provider,
            model=args.model,
            verbose=verbose
        )
        results.append(result)

    # Summary
    if verbose and len(results) > 1:
        print(f"\n{'='*60}")
        print("SUMMARY")
        print(f"{'='*60}")

        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]

        print(f"Total: {len(results)}")
        print(f"Successful: {len(successful)}")
        print(f"Failed: {len(failed)}")

        if successful:
            scores = [r['quality_score']['overall_score'] for r in successful]
            avg_score = sum(scores) / len(scores)
            print(f"\nAverage Quality Score: {avg_score:.1f}/100")

            passed = [r for r in successful if r['quality_score']['passed']]
            print(f"Passed Quality Checks: {len(passed)}/{len(successful)}")

        if failed:
            print(f"\nFailed prompts:")
            for r in failed:
                print(f"  - {r['prompt_id']}: {r['error']}")

    return 0 if all(r['success'] for r in results) else 1


if __name__ == '__main__':
    sys.exit(main())
