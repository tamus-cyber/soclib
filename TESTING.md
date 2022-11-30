# Unit Testing

soclib is using Pytest to handle unit testing.

## Instructions

Before any unit testing, you must setup your environment variables. This can be done in a `.env` file in the root directory of soclib or it can be done using your shell/container environment variables. Here is the environment variable template:

```env
BASE_URL="https://[azure-site-here].azurewebsites.net"
TEST_STAKEHOLDER=
TEST_DETECTION_ID=
TEST_HOST_ID=
```

Simply run the following in a terminal while in the root directory:

```bash
pytest
```

If that doesn't work, you may have an issue with your PATH. Try this instead:

```bash
python3 -m pytest
```

You should expect to see the following output:

```diff
================================= test session starts ==================================
platform ...
rootdir: ...
plugins: ...
collected 2 items                                                                      

tests/detection_test.py .                                                        [ 50%]
tests/host_test.py .                                                             [100%]

================================== X passed in X.XXs ===================================

```

## List of tests

- Azure authentication
- Vectra session creation
- Get a detection from Vectra
- Get host info from Vectra