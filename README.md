# Prerequisites to start streaming

## System-level Dependencies:

1. **Docker**:
   - Needed to compose the services needed for the game logic.

2. **Python**
   - Needed to use the stream manager (stream.py)

## Application-level Dependencies:

These are needed to run stream.py, which is not correlated with the stream files.
stream.py only serves as a manager of the docker containers.

Hence, the requirements.txt here is ONLY for stream.py, any other dependencies should be added to the Dockerfile.

1. **Python Packages**:
   - The application requires several Python packages. You can install them using pip:
     ```
     pip install -r requirements.txt
     ```