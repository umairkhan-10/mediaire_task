# Fr-PACS, Fr-HUB, and Fr-BRAIN

## Overview

This project consists of three independent software units: Fr-PACS, Fr-HUB, and Fr-BRAIN. These units communicate with
each other one way or the other (Fr-PACS and Fr-HUB communicate via sockets while Fr-HUB and Fr-BRAIN communicate via
persistent storage i.e. MongoDB).

## Prerequisites

- **MongoDB**: Install MongoDB service locally as we are using MongoDB for persistent storage due to its flexibility,
  documented format, and scalability. Make sure it's
  running. [MongoDB Installation Instructions](https://docs.mongodb.com/manual/installation/)

- **Docker**: Docker should be installed and running as well (for running Unit Tests via Test
  Container). [Docker Installation Instructions](https://docs.docker.com/get-docker/)
- This project uses **Python 3.12**.
  For all other dependencies, please refer to `common/requirements.txt`.

### 1. Create a Virtual Environment

```sh
python3 -m venv venv
```

### 2. Activate the Virtual Environment

```sh
source venv/bin/activate
```

### 3. Install Dependencies

```sh
pip install -r common/requirements.txt
```

### 4. Run via Makefile

To run all units:

```sh
make all
```

To run a command for an individual unit:

```sh
make <command-for-individual-unit>
```

### 5. Run Unit Tests

```sh
make tests
```

### 6. Run Test Coverage

```sh
make coverage
```

## Architecture Overview

- **Fr-PACS**:

  As per requriement, there is no need for any persistent storage in this unit, so no need for non-persistent queue
  or any persistent storage
  etc is being used
  in this unit.
    - **Client**:
        - Responsible for generating and sending brain scans to Fr-HUB via sockets. Sockets is used for low latency,
          persistent connection, better scalability, more flexibility and for real-time capturing of reports.
        - If brain scan failed to get sent (FrHUB not running or some other issue), it just logs the failed case. If it
          does get sent, it just logs the acknowledgement sent by FrHUB.
    - **Server**:
        - Responsible for receiving brain report sent by FrHUb via socket.
        - It just logs the received brain report in success case scenario, if it fails we just log them in FrHUB while
          FrPACS would keep waiting for new reports.

- **Fr-HUB**:

  As per requriement, we need persistent storage in this unit, so we have used MongoDB.
  in this unit.
    - **Client**:
        - Responsible for fetching brain report from DB ('status' set as 'False' means those which didn't get sent) and
          send it to FrPACS via network socket
        - If brain report failed to get sent (FrPACS not running or some other issue), it just logs the failed case. If
          it does get sent, it just logs and sends the acknowledgement sent by FrPACS.
    - **Server**:
        - Responsible for receiving brain scan sent by FrPACS via network socket saves it to persistent storage (
          MongoDB) with 'report_generated' as 'To Do' so that FrBRAIN knows via this key, which scan to process.
        - Sends acknowledgement in success case scenario while it keeps waiting if report is not being sent by FrPACS (
          if FrPACS is stopped or any other issue)

- **Fr-BRAIN**:

  As per requriement, we need persistent storage in this unit which was utilized by FrHUB, so we have used same MongoDB.
  in this unit.
    - **Processor**:
        - Responsible for fetching brain scan from DB that are 'report_generated' as 'To Do', sets this key as 'In
          Progress' during processing to avoid duplicate processing.
        - Analyzes them and generates a report
        - Saves the report in MongoDB collection named brain_reports with status as sent 'False' so that FrHUB knows
          from this key which reports to send, which then gets utilized by FrHUB to send it to FrPACS
        - After saving the report, it also sets the 'report_generated' key in brain scan collection as 'Done' to avoid
          duplicate processing

- **Common Utilities**:
    - DBManager - a Singleton class to handle DB Operations
    - Logger - For centralized logging
    - Models - Pydantic models for BrainScan and BrainReport.
    - Utilities: Helper functions for generating/analyzing scans, and saving reports.
    - Config - For constants and Enums

## Tech Stack/Philosophy:

#### Python:

Python is widely used by a lot of big companies and has proven to be reliable in large scale web apps. It's being used
in this project for its reliability and my experience with Python

#### Requirements/dependencies

requirements file is in a because a project can have multiple requirements file. for example, dev
requirements, etc. So it is better to have all requirements file in one folder.

#### Makefile

Having make file makes it easy to run all units at once or separately.
All the commands can be run with same format e.g. make <your command>

#### Validations

For validations, I have utilized pydantic for function parameters and return types.

#### Threading

Threading is being utilized to ensure that the system can run multiple operations concurrently.

#### Multi Processing

Multi processing FrBRAINProcessor to efficently process large data simulaneously and effectively.

#### Code Quality Tools

- **Black**: Used for code formatting.
- **isort**: Used for optimizing imports.
-

## Potential Improvements

- Store sensitive credentials like MongoDB URI in some env file or probably AWS Secrets Manager.
- Implement batch processing in Fr-HUB and Fr-BRAIN for fetching/processing to reduce the number of database calls.
- Handle the case, when FrBRAIN server stops and reports are stuck in 'In Process'.
- Implement a retry mechanism for handling network communication errors gracefully.
- Can Implement authentication/encryption for DB connections.
- Utilize monitoring and logging tools like ELK, Prometheus, Grafana or Sentry etc.
- Better and more comprehensive unit test cases for the system.
- Introduce indexing in columns like 'scan_id', 'patient_id', 'report_generated' etc.
- I could use docker file but the scope and time of this task is limited so didn't use for this excercise.

- By addressing these points, the system will become more robust, secure, and maintainable.