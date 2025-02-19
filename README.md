Pre reqs:
You should also install Mongo DB service locally as for persistent storage we're using MongoDB, and make sure its
running

(e.g. You could query on any LLM on how to install MongoDB service in <System OS>)

You should also install Docker and it should be running as well (for running Unit Tests via Test Container)

This project uses Python 3.12
For all the other dependencies, please have a look at common/requirements.txt

### Steps to run Single Unit:

#### 1: Create virtual env:

* python3 -m venv venv

#### 2: Activate virtual env

* source venv/bin/activate

#### 3: Install dependencies:

* pip install -r common/requirements.txt

#### 4: Run via Makefile:

* make all
  OR
* make "command for individual unit"

#### 4: Run Unitests:

* make tests

#### 4: Run Test Coverage:

* make coverage

# Fr-PACS, Fr-HUB, and Fr-BRAIN

## Overview

This project consists of three independent software units: Fr-PACS, Fr-HUB, and Fr-BRAIN. These units communicate with
each other one way or the other (FrPACS and FrHUB communicates via sockets while FrHUB and FrBRAIN communciates via
persistent storage i.e. MongoDB)

## Architecture Overview

- **Fr-PACS**:

  As per requriement, there is no need for any persistent storage in this unit, so no queue, DB etc is being used
  in this unit.
    - **Client**:
        - Responsible for generating and sending brain scans to Fr-HUB via sockets. Sockets is used for low latency,
          persistent connection, better scalability, more flexibility and for real-time capturing of reports.
        - If brain scan failed to get sent (FrHUB not running or some other issue), it just logs the failed case. If it
          does get sent, it just logs the acknowledgement sent by FrHUB (We could also integrate queue instead of
          sending brain scan directly but as per requirement, there is no use for it)
    - **Server**:
        - Responsible for receiving brain report sent by FrHUb via socket.
        - It just logs the receviing brain report in success case scenario, if it fails we just log them in FrHUB while
          FrPACS
          would keep waiting for new reports (no need to keep the incoming report persistent)

- **Fr-HUB**:

  As per requriement, we need persistent storage in this unit, so we have used MongoDB.
  in this unit.
    - **Client**:
        - Responsible for fetching brain report from DB ('status' set as 'False' means those which didn't get sent) and
          send it to FrPACS via network socket
        - If brain report failed to get sent (FrPACS not running or some other issue), it just logs the failed case. If
          it does get sent, it just logs the acknowledgement sent by FrPACS (We could also integrate queue instead of
          sending brain scan directly but as per requirement, there is no use for it)
    - **Server**:
        - Responsible for receiving brain scan sent by FrPACS via network socket saves it to persistent storage (
          MongoDB) with 'report_generated' as 'To Do' so that FrBRAIN knows via this key, which scan to process.
        - Sends acknolwedgement in success case scenario while it keeps waiting if report is not being sent by FrPACS (
          if FrPACS is stopped)

- **Fr-BRAIN**:

  As per requriement, we need persistent storage in this unit which was utilized by FrHUB, so we have used same MongoDB.
  in this unit.
    - **Processor**:
        - Responsible for fetching brain scan from DB that are 'report_generated' as 'To Do', sets this key as 'In
          Progress' so that no other process can take this exact scan while processing
        - Analyzes them and generates a report
        - Saves the report in MongoDB collection named brain_reports with status as sent 'False' so that FrHUB knows
          from this key which reports to send, it then
          gets utilized by FrHUB to send it to FrPACS
        - After saving the report, it also sets the 'report_generated' key in brain scan collection as 'Done' to avoid
          duplicate processing

- **Common Utilities**:
    - DBManager - a Singleton class to handle DB Operations
    - Logger - For centralized logging
    - Models - Pydantic models for BrainScan and BrainReport.
    - Utilities: Helper functions for generating/analyzing scans, and saving reports.
    - Const - For constants and Enums

## Tech Stack/Philosophy:

#### Python:

Python is being used by a lot of big companies and has proven to be reliable in big scale web apps. So I prefer to
choose something that is proven to work on scale and also having experience in Python makes it better choice for me.

#### Requirements/dependencies

requirements file is in a separate folder because a project can have multiple requirements file. for example, dev
requirements, etc. So it is better to have all requirements file in one folder.

#### Makefile

Having make file makes it easy to run all units at once or separately.
All the commands can be run with same format e.g. make <your command>

#### Validations

For validations, I have utilized pydantic for function parameters and return types.

#### Threading

Threading is being utilized to ensure that the system can run multiple operations concurrently.

#### Black Formatter and isort

Utilized black code formatter to better format the code as well and also optimized import via isort.

## Potential Improvements

- We should use critical credentials like MongoDB in some env file or probably AWS Secrets Manager to improve security.
- We can introduce batch processing in both FrHUB and FrBRAIN to fetch and process data of scans and reports in batches
  instead of fetching single which increases our DB calls.
- Implement a retry mechanism for handling errors gracefully in network communication.
- We can implement locking mechanism to avoid handling of same data or objects by multiple threads
- We should better implement Multi-Processing for FRBRAIN to create the reports in an optimized way.
- Can implement authentication/encryption for DB connections.
- Utilize better monitoring and logging tools like ELK, Prometheus, Grafana or Sentry etc.
- Better and more unit tests for the system
- We could introduce indexing in columns like scan_id, patient_id, report_generated etc.
- I could use docker file but the scope and time of this task is limited so didn't use for this excercise.
- Can also write more Unit Tests and can separate out each unit test cases as well.