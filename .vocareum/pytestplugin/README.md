# vocareum-pytest-plugin

A custom [pytest](https://docs.pytest.org/) plugin for automated grading integration with [Vocareum](https://www.vocareum.com/).  
This plugin enables instructors to attach weights, labels, and messages to test cases and automatically generate grading files for the Vocareum platform.

---
## 🔧 Installation

First, install the plugin into your Python project (containing pyproject.toml):

```bash
uv add --group dev path/to/vocareum_plugin
```

Make sure python-dotenv is available (it's included in the plugin dependencies).

---

## ⚙️ Grades and Reports File Paths

Grades and Reports file paths are defined in the `vocareumGradeFile` and `vocareumReportFile` environment variables, defined inside Vocareum.

## 📁 Pytest Integration

In pytest.ini (recommended):

```
[pytest]
addopts = -ra
markers =
    test_name(name): Custom name for the test to show in Vocareum report.
    weight(value): Score weight for this test.
    success_msg(msg): Message shown on test success.
    failure_msg(msg): Message shown on test failure.
```

⚠️ Do not include -p vocareum_plugin.plugin in addopts. The plugin is auto-discovered.


## 🧪 Usage in Tests

Annotate your tests with custom markers to control scoring and feedback:

```python
import pytest

@pytest.mark.test_name("Creation of Lambda function for events") #Name of the test (exercise)
@pytest.mark.weight(5) #Exercise grade definition
@pytest.mark.success_msg("Test 1 passed: Created Lambda function for events.")
@pytest.mark.failure_msg("Test 1 failed: Expected Lambda function for events to be created. Please try again.")
def test_lambda_created():
    assert True # Mocking a passing test. Specify the respective assertion for your test.

@pytest.mark.test_name("Creation of DynamoDB table for events") #Name of the test (exercise)
@pytest.mark.weight(5) #Exercise grade definition
@pytest.mark.success_msg("Test 2 passed: Created DynamoDB table for events.")
@pytest.mark.failure_msg("Test 2 failed: Expected DynamoDB table for events to be created. Please try again.")
def test_dynamodb_table_exists():
    assert False # Mocking a failing test. Specify the respective assertion for your test.
```

If you don't provide markers, the plugin falls back to defaults:
- weight = 10
- test_name = function name
- Standard success/failure messages

```python
def test_s3_bucket_created():
    assert True #specify the respective assertion for your test.
```

Then, run your tests:
```bash
uv run pytest
```

## 🧾 Output Files

After running pytest, the plugin will generate two files:

- Write scores to file path defined in the `vocareumGradeFile` environment variable:

  <pre><code>Creation of Lambda function for events, 5
  Creation of DynamoDB table for events, 0 
  Test s3 bucket created, 0</code></pre>
- Write scores to file path defined in the `vocareumReportFile` environment variable:
  <pre><code>Test 1 passed: Created Lambda function for events.
  =======================================================================================================================
  Test 2 failed: Expected DynamoDB table for events to be created. Please try again.
  =======================================================================================================================
  Test failed: Test s3 bucket created. Please try again.
  =======================================================================================================================</code></pre>