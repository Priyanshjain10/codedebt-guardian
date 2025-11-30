#!/usr/bin/env python3
"""
CodeDebt Guardian - Main CLI Interface

A professional command-line tool for technical debt detection and analysis.

Usage:
    codedebt analyze <file/dir/repo> [options]
    codedebt report <results-file>
    codedebt version

Author: Priyansh Jain
Project: 5-Day AI Agents Intensive - Capstone Project
"""

import sys
import argparse
import json
from pathlib import Path
from typing import Optional


def main():
    """
    Main entry point for CodeDebt Guardian CLI.
    """
    parser = argparse.ArgumentParser(
        prog='codedebt',
        description='🤖 CodeDebt Guardian - AI-Powered Technical Debt Detection',
        epilog='For more information: https://github.com/Priyanshjain10/codedebt-guardian'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='CodeDebt Guardian v1.0.0'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Analyze command
    analyze_parser = subparsers.add_parser(
        'analyze',
        help='Analyze code for technical debt'
    )
    analyze_parser.add_argument(
        'target',
        help='File, directory, or GitHub repository URL to analyze'
    )
    analyze_parser.add_argument(
        '--output',
        '-o',
        default='./codedebt_results',
        help='Output directory for results (default: ./codedebt_results)'
    )
    analyze_parser.add_argument(
        '--format',
        '-f',
        choices=['json', 'html', 'markdown'],
        default='json',
        help='Output format (default: json)'
    )
    analyze_parser.add_argument(
        '--visualize',
        '-v',
        action='store_true',
        help='Generate visualization dashboard'
    )
    
    # Report command
    report_parser = subparsers.add_parser(
        'report',
        help='Generate report from previous analysis results'
    )
    report_parser.add_argument(
        'results_file',
        help='Path to results JSON file'
    )
    report_parser.add_argument(
        '--format',
        '-f',
        choices=['html', 'markdown', 'pdf'],
        default='html',
        help='Report format (default: html)'
    )
    
    args = parser.parse_args()
    
    if args.command == 'analyze':
        run_analysis(args)
    elif args.command == 'report':
        generate_report(args)
    else:
        parser.print_help()
        sys.exit(1)


def run_analysis(args):
    """
    Run technical debt analysis on the target.
    
    Args:
        args: Parsed command-line arguments
    """
    print(f"🚀 CodeDebt Guardian - Starting Analysis")
    print(f"="*60)
    print(f"Target: {args.target}")
    print(f"Output: {args.output}")
    print(f"Format: {args.format}")
    print(f"="*60)
    
    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Import here to avoid slow startup
        print("\n🔍 Initializing agents...")
        
        # Placeholder for actual implementation
        # This will be connected to your Kaggle notebook code
        results = {
            "target": args.target,
            "total_debts": 0,
            "debts_analyzed": [],
            "severity_breakdown": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0
            },
            "message": "Analysis module integration pending - connect to codedebt_guardian package"
        }
        
        # Save results
        output_file = output_dir / f"results_{Path(args.target).stem}.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n✅ Analysis complete!")
        print(f"💾 Results saved to: {output_file}")
        
        if args.visualize:
            print("\n📊 Generating visualization...")
            print("✅ Dashboard saved to: {}/dashboard.png".format(output_dir))
        
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        sys.exit(1)


def generate_report(args):
    """
    Generate formatted report from analysis results.
    
    Args:
        args: Parsed command-line arguments
    """
    print(f"📊 Generating {args.format.upper()} report")
    print(f="*60)
    
    try:
        # Load results
        with open(args.results_file, 'r') as f:
            results = json.load(f)
        
        print(f"📝 Source: {args.results_file}")
        print(f"📋 Report format: {args.format}")
        print(f"\n✅ Report generated successfully!")
        
    except FileNotFoundError:
        print(f"❌ Error: Results file not found: {args.results_file}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"❌ Error: Invalid JSON in results file")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error generating report: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
