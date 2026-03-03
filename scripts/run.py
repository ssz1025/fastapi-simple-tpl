"""
Run script with environment selection.

Usage:
    python scripts/run.py              # Development (default)
    python scripts/run.py --prod       # Production
    python scripts/run.py --port 9000  # Custom port
"""

import argparse
import os
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description="Run FastAPI application")
    parser.add_argument("--prod", action="store_true", help="Run in production mode")
    parser.add_argument("--port", type=int, default=8000, help="Port number")
    parser.add_argument("--host", default="0.0.0.0", help="Host address")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    
    args = parser.parse_args()
    
    # Build command
    cmd = ["uvicorn", "app.main:app", "--host", args.host, "--port", str(args.port)]
    
    if args.prod:
        # Production mode
        os.environ["ENVIRONMENT"] = "production"
        cmd.extend(["--workers", "4"])
        print(f"🚀 Starting production server at http://{args.host}:{args.port}")
    else:
        # Development mode
        os.environ["ENVIRONMENT"] = "development"
        cmd.append("--reload")
        print(f"🚀 Starting development server at http://{args.host}:{args.port}")
    
    # Run
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n👋 Server stopped")


if __name__ == "__main__":
    main()
