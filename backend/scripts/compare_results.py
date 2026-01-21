#!/usr/bin/env python3
"""
Compare workout plan evaluation results.

Compares results between different versions, providers, or models
to identify improvements and regressions.

Usage:
    # Compare two versions (same provider/model)
    python scripts/compare_results.py v1_baseline v2_improved --provider gemini

    # Compare two providers (same version)
    python scripts/compare_results.py v1_baseline v1_baseline --providers gemini,openai

    # List available results
    python scripts/compare_results.py --list
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Results directory
RESULTS_DIR = Path(__file__).parent.parent / 'tests' / 'evaluation' / 'results'


def find_latest_results(version: str, provider: str = None, model: str = None) -> dict:
    """
    Find the latest result files for a version/provider combination.

    Returns dict mapping prompt_id to result data.
    """
    version_dir = RESULTS_DIR / version

    if not version_dir.exists():
        return {}

    results = {}

    # Find matching provider directories
    for provider_dir in version_dir.iterdir():
        if not provider_dir.is_dir():
            continue

        # Parse provider_model from directory name
        dir_name = provider_dir.name
        parts = dir_name.split('_', 1)
        dir_provider = parts[0]
        dir_model = parts[1] if len(parts) > 1 else 'default'

        # Filter by provider/model if specified
        if provider and dir_provider != provider:
            continue
        if model and dir_model != model:
            continue

        # Find latest result for each prompt
        result_files = defaultdict(list)
        for result_file in provider_dir.glob('*.json'):
            # Parse prompt_id from filename (format: prompt_id_YYYYMMDD_HHMMSS.json)
            parts = result_file.stem.rsplit('_', 2)
            if len(parts) >= 3:
                prompt_id = '_'.join(parts[:-2])
                timestamp = f"{parts[-2]}_{parts[-1]}"
                result_files[prompt_id].append((timestamp, result_file))

        # Get latest for each prompt
        for prompt_id, files in result_files.items():
            files.sort(reverse=True)  # Latest first
            latest_file = files[0][1]
            with open(latest_file) as f:
                result = json.load(f)
                key = f"{prompt_id}:{dir_provider}:{dir_model}"
                results[key] = result

    return results


def list_available_results():
    """List all available evaluation results."""
    if not RESULTS_DIR.exists():
        print("No results directory found.")
        return

    print("\nAvailable evaluation results:")
    print("=" * 60)

    for version_dir in sorted(RESULTS_DIR.iterdir()):
        if not version_dir.is_dir():
            continue

        print(f"\nVersion: {version_dir.name}")

        for provider_dir in sorted(version_dir.iterdir()):
            if not provider_dir.is_dir():
                continue

            # Count result files
            result_files = list(provider_dir.glob('*.json'))
            if result_files:
                # Get unique prompt IDs
                prompt_ids = set()
                for f in result_files:
                    parts = f.stem.rsplit('_', 2)
                    if len(parts) >= 3:
                        prompt_ids.add('_'.join(parts[:-2]))

                print(f"  {provider_dir.name}: {len(prompt_ids)} prompts, {len(result_files)} total results")


def compare_results(
    version1: str,
    version2: str,
    provider1: str = None,
    provider2: str = None,
    model1: str = None,
    model2: str = None,
    verbose: bool = True
) -> dict:
    """
    Compare results between two evaluation runs.

    Args:
        version1: First version to compare (baseline)
        version2: Second version to compare
        provider1: Provider for version1 (optional)
        provider2: Provider for version2 (optional, defaults to provider1)
        model1: Model for version1 (optional)
        model2: Model for version2 (optional)
        verbose: Print detailed comparison

    Returns:
        Comparison report dictionary
    """
    # Default provider2 to provider1 if not specified
    if provider2 is None:
        provider2 = provider1
    if model2 is None:
        model2 = model1

    # Load results
    results1 = find_latest_results(version1, provider1, model1)
    results2 = find_latest_results(version2, provider2, model2)

    if not results1:
        print(f"No results found for {version1}" +
              (f" (provider: {provider1})" if provider1 else ""))
        return None

    if not results2:
        print(f"No results found for {version2}" +
              (f" (provider: {provider2})" if provider2 else ""))
        return None

    # Build comparison
    comparison = {
        'baseline': {
            'version': version1,
            'provider': provider1,
            'model': model1
        },
        'comparison': {
            'version': version2,
            'provider': provider2,
            'model': model2
        },
        'prompts': [],
        'summary': {}
    }

    # Get all prompt IDs from both sets
    prompt_ids = set()
    for key in results1:
        prompt_id = key.split(':')[0]
        prompt_ids.add(prompt_id)
    for key in results2:
        prompt_id = key.split(':')[0]
        prompt_ids.add(prompt_id)

    # Compare each prompt
    improvements = []
    regressions = []
    unchanged = []

    for prompt_id in sorted(prompt_ids):
        # Find matching results
        result1 = None
        result2 = None

        for key, result in results1.items():
            if key.startswith(f"{prompt_id}:"):
                result1 = result
                break

        for key, result in results2.items():
            if key.startswith(f"{prompt_id}:"):
                result2 = result
                break

        if not result1 or not result2:
            comparison['prompts'].append({
                'prompt_id': prompt_id,
                'status': 'missing',
                'baseline': result1 is not None,
                'comparison': result2 is not None
            })
            continue

        # Get scores
        score1 = result1.get('quality_score', {}).get('overall_score', 0) if result1.get('success') else 0
        score2 = result2.get('quality_score', {}).get('overall_score', 0) if result2.get('success') else 0
        diff = score2 - score1

        prompt_comparison = {
            'prompt_id': prompt_id,
            'prompt_text': result1.get('prompt_text', ''),
            'baseline_score': score1,
            'comparison_score': score2,
            'difference': diff,
            'baseline_passed': result1.get('quality_score', {}).get('passed', False) if result1.get('success') else False,
            'comparison_passed': result2.get('quality_score', {}).get('passed', False) if result2.get('success') else False,
            'baseline_time_ms': result1.get('generation_time_ms', 0),
            'comparison_time_ms': result2.get('generation_time_ms', 0),
        }

        # Add check-level comparison
        if result1.get('quality_score') and result2.get('quality_score'):
            checks1 = result1['quality_score'].get('checks', {})
            checks2 = result2['quality_score'].get('checks', {})

            check_changes = []
            for check_name in set(checks1.keys()) | set(checks2.keys()):
                s1 = checks1.get(check_name, {}).get('score', 0)
                s2 = checks2.get(check_name, {}).get('score', 0)
                if s1 != s2:
                    check_changes.append({
                        'check': check_name,
                        'baseline': s1,
                        'comparison': s2,
                        'diff': s2 - s1
                    })

            prompt_comparison['check_changes'] = check_changes

        # Categorize
        if diff > 5:
            improvements.append(prompt_comparison)
        elif diff < -5:
            regressions.append(prompt_comparison)
        else:
            unchanged.append(prompt_comparison)

        comparison['prompts'].append(prompt_comparison)

    # Calculate summary
    all_scores1 = [p['baseline_score'] for p in comparison['prompts'] if p.get('baseline_score') is not None]
    all_scores2 = [p['comparison_score'] for p in comparison['prompts'] if p.get('comparison_score') is not None]

    comparison['summary'] = {
        'total_prompts': len(prompt_ids),
        'improvements': len(improvements),
        'regressions': len(regressions),
        'unchanged': len(unchanged),
        'baseline_avg_score': sum(all_scores1) / len(all_scores1) if all_scores1 else 0,
        'comparison_avg_score': sum(all_scores2) / len(all_scores2) if all_scores2 else 0,
        'avg_score_diff': (sum(all_scores2) / len(all_scores2) - sum(all_scores1) / len(all_scores1)) if all_scores1 and all_scores2 else 0
    }

    # Print comparison if verbose
    if verbose:
        print_comparison(comparison, improvements, regressions, unchanged)

    return comparison


def print_comparison(comparison: dict, improvements: list, regressions: list, unchanged: list):
    """Print formatted comparison report."""
    print("\n" + "=" * 70)
    print("EVALUATION COMPARISON REPORT")
    print("=" * 70)

    baseline = comparison['baseline']
    comp = comparison['comparison']

    print(f"\nBaseline:   {baseline['version']}", end="")
    if baseline['provider']:
        print(f" ({baseline['provider']}", end="")
        if baseline['model']:
            print(f" / {baseline['model']}", end="")
        print(")", end="")
    print()

    print(f"Comparison: {comp['version']}", end="")
    if comp['provider']:
        print(f" ({comp['provider']}", end="")
        if comp['model']:
            print(f" / {comp['model']}", end="")
        print(")", end="")
    print()

    # Summary
    summary = comparison['summary']
    print("\n" + "-" * 70)
    print("SUMMARY")
    print("-" * 70)
    print(f"Total prompts compared: {summary['total_prompts']}")
    print(f"Average score: {summary['baseline_avg_score']:.1f} -> {summary['comparison_avg_score']:.1f} ({summary['avg_score_diff']:+.1f})")
    print(f"Improvements: {summary['improvements']} | Regressions: {summary['regressions']} | Unchanged: {summary['unchanged']}")

    # Improvements
    if improvements:
        print("\n" + "-" * 70)
        print("IMPROVEMENTS")
        print("-" * 70)
        for p in sorted(improvements, key=lambda x: x['difference'], reverse=True):
            print(f"\n  {p['prompt_id']}")
            print(f"    Score: {p['baseline_score']:.1f} -> {p['comparison_score']:.1f} ({p['difference']:+.1f})")
            if p.get('check_changes'):
                print("    Check changes:")
                for c in p['check_changes']:
                    if c['diff'] > 0:
                        print(f"      + {c['check']}: {c['baseline']:.0f} -> {c['comparison']:.0f}")

    # Regressions
    if regressions:
        print("\n" + "-" * 70)
        print("REGRESSIONS")
        print("-" * 70)
        for p in sorted(regressions, key=lambda x: x['difference']):
            print(f"\n  {p['prompt_id']}")
            print(f"    Score: {p['baseline_score']:.1f} -> {p['comparison_score']:.1f} ({p['difference']:+.1f})")
            if p.get('check_changes'):
                print("    Check changes:")
                for c in p['check_changes']:
                    if c['diff'] < 0:
                        print(f"      - {c['check']}: {c['baseline']:.0f} -> {c['comparison']:.0f}")

    # Detailed per-prompt
    print("\n" + "-" * 70)
    print("ALL PROMPTS")
    print("-" * 70)
    print(f"{'Prompt ID':<30} {'Baseline':>10} {'Comparison':>12} {'Diff':>8} {'Status':>10}")
    print("-" * 70)

    for p in comparison['prompts']:
        status = "missing" if p.get('status') == 'missing' else (
            "improved" if p['difference'] > 5 else (
                "regressed" if p['difference'] < -5 else "same"
            )
        )
        if p.get('status') == 'missing':
            print(f"{p['prompt_id']:<30} {'N/A':>10} {'N/A':>12} {'':>8} {status:>10}")
        else:
            print(f"{p['prompt_id']:<30} {p['baseline_score']:>10.1f} {p['comparison_score']:>12.1f} {p['difference']:>+8.1f} {status:>10}")

    print()


def main():
    parser = argparse.ArgumentParser(
        description='Compare workout plan evaluation results',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Compare two versions with the same provider
  python scripts/compare_results.py v1_baseline v2_improved --provider gemini

  # Compare two providers on the same version
  python scripts/compare_results.py v1_baseline v1_baseline --providers gemini,openai

  # List available results
  python scripts/compare_results.py --list
        """
    )

    parser.add_argument('version1', nargs='?', type=str,
                        help='Baseline version to compare')
    parser.add_argument('version2', nargs='?', type=str,
                        help='Version to compare against baseline')
    parser.add_argument('--provider', '-p', type=str,
                        help='Provider for both versions (when comparing versions)')
    parser.add_argument('--providers', type=str,
                        help='Comma-separated providers to compare (e.g., gemini,openai)')
    parser.add_argument('--model', '-m', type=str,
                        help='Model for both versions')
    parser.add_argument('--models', type=str,
                        help='Comma-separated models to compare')
    parser.add_argument('--list', '-l', action='store_true',
                        help='List available results')
    parser.add_argument('--quiet', '-q', action='store_true',
                        help='Minimal output')
    parser.add_argument('--json', action='store_true',
                        help='Output comparison as JSON')

    args = parser.parse_args()

    if args.list:
        list_available_results()
        return 0

    if not args.version1 or not args.version2:
        print("Error: Both version1 and version2 are required")
        print("Use --list to see available results, or --help for usage")
        return 1

    # Determine provider/model settings
    provider1, provider2 = None, None
    model1, model2 = None, None

    if args.providers:
        providers = args.providers.split(',')
        if len(providers) != 2:
            print("Error: --providers requires exactly 2 comma-separated values")
            return 1
        provider1, provider2 = providers[0].strip(), providers[1].strip()
    elif args.provider:
        provider1 = provider2 = args.provider

    if args.models:
        models = args.models.split(',')
        if len(models) != 2:
            print("Error: --models requires exactly 2 comma-separated values")
            return 1
        model1, model2 = models[0].strip(), models[1].strip()
    elif args.model:
        model1 = model2 = args.model

    # Run comparison
    comparison = compare_results(
        version1=args.version1,
        version2=args.version2,
        provider1=provider1,
        provider2=provider2,
        model1=model1,
        model2=model2,
        verbose=not args.quiet and not args.json
    )

    if args.json and comparison:
        print(json.dumps(comparison, indent=2))

    return 0 if comparison else 1


if __name__ == '__main__':
    sys.exit(main())
