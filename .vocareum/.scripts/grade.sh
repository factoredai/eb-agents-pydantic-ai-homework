#!/bin/bash
set -e  # Exit on any error

UV_VERSION="0.7.12"

error_exit_for_student() {
    echo "❌ Error: Failed to set up the grading environment. Please contact the lab support team." >&2
    exit 1
}

echo "🔧 Setting up grading environment..."
echo "📁 Current directory: $(pwd)"

# Step 1: Install uv silently
if ! curl -LsSf "https://astral.sh/uv/${UV_VERSION}/install.sh" | sh >/dev/null 2>&1; then
    error_exit_for_student
fi

# Step 2: Source uv environment
set +e
source "$HOME/.local/bin/env" >/dev/null 2>&1
set -e

# Step 3: Run Makefile setup to install dependencies and plugin
if ! make setup; then
    error_exit_for_student
fi

# Step 4: Check for required environment variables
if [[ -z "$vocareumGradeFile" || -z "$vocareumReportFile" ]]; then
    echo "❌ Error: vocareumGradeFile and/or vocareumReportFile are not set." >&2
    exit 1
fi

# Step 5: Run tests via Makefile (plugin will handle grading)
if ! make test; then
    error_exit_for_student
fi

echo "✅ Grading complete."
