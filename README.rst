Streaming Analtyics Demo 
========================

This project demonstrates how to query streaming data using several Azure technologies:

- Azure Streaming Analtyics
- Azure Eventhubs

Workflow:

- Generator App sents message to Eventhubs
- Streaming analytics queries device message for failing devices

|architecture-overview|

Setup
=====
This setup will deploy the core infrastructure needed to run the the solution:

- Core infrastructure
- Generator App

Core Infrastructure
-------------------

Configure the global variables

.. code-block:: bash

    # Global
    RG_NAME=sa_demo
    RG_REGION=westus
    STORAGE_ACCOUNT_NAME=sa_demo
    
    #Event Hubs
    EH_NAMESPACE=sa_demo_ehn
    EH_NAME=sa_demo_eh

    #Streaming Analytics
    SA_NAME=sa_demo_sa
    SA_JOB_NAME=sa_demo_sa
    SA_INPUT_NAME=SaInputName
    SA_OUTPUT_NAME=StreamingDeviceCount

    # Existing Resources
    ACR_REGISTRY_NAME = <existing-registry-name>
    SERVICE_PRINCIPAL_ID = <existing-service-principal-id>
    SERVICE_PRINCIPAL_PASSWORD = <existing-service-principal-password>

**Resource Group**

Create a resource group for this project

.. code-block:: bash

    az group create --name $RG_NAME --location $RG_REGION

**Evenhubs**

.. code-block:: bash

    # Create an Event Hubs namespace. Specify a name for the Event Hubs namespace.
    az eventhubs namespace create --name $EH_NAMESPACE --resource-group $RG_NAME -l $RG_REGION   

    # Create an event hub. Specify a name for the event hub. 
    az eventhubs eventhub create --name $EH_NAME --resource-group $RG_NAME --namespace-name $EH_NAMESPACE

    # Create Read Policy and Connection string
    #TBD 

**Streaming Analytics**

Copy the following files and replace the values:

- `/streaming_analytics/input_datasource_example.json` to `/streaming_analytics/input_datasource.json` 
- `/streaming_analytics/pbi_output_datasource_example.json` to `/streaming_analytics/pbi_output_datasource.json` 
- 
.. code-block:: bash

    # Create a Job
    az stream-analytics job create --resource-group $RG_NAME --name $SA_NAME --location $RG_REGION  --output-error-policy "Drop" --events-outoforder-policy "Drop" --events-outoforder-max-delay 5 --events-late-arrival-max-delay 16 --data-locale "en-US"

    # Create input to eventhub
    az stream-analytics input create --resource-group $RG_NAME --job-name $SA_JOB_NAME --name $SA_INPUT_NAME --type Stream --datasource @datasource.json --serialization @serialization.json

    # Create output to Powerbi
    az stream-analytics output create --resource-group $RG_NAME --job-name $SA_JOB_NAME --name $SA_OUTPUT_NAME --datasource @datasource.json --serialization @serialization.json
    
    # Create Transformation query
    az stream-analytics transformation create --resource-group $RG_NAME --job-name $SA_JOB_NAME --name Transformation --streaming-units "6" --transformation-query "${cat query.sql}"

Generator
---------

The generator is a python application that runs in a docker container. The container expects the following environment variables stored in a ``local.env`` file.

Run generator in docker

.. code-block:: bash

    # Build and run image
    > docker build --pull --rm -f "dockerfile" -t streaminganaltyicsdemo:latest "."
    > docker run --rm -it --env-file local.env streaminganaltyicsdemo:latest

    #Run app
    > python main.py --template_path /path/to/templates/

Development
===========

Setup your dev environment by creating a virtual environment

.. code-block:: bash

    # virtualenv \path\to\.venv -p path\to\specific_version_python.exe
    python -m venv .venv.
    .venv\scripts\activate

    deactivate


Style Guidelines
----------------

This project enforces quite strict `PEP8 <https://www.python.org/dev/peps/pep-0008/>`_ and `PEP257 (Docstring Conventions) <https://www.python.org/dev/peps/pep-0257/>`_ compliance on all code submitted.

We use `Black <https://github.com/psf/black>`_ for uncompromised code formatting.

Summary of the most relevant points:

- Comments should be full sentences and end with a period.
- `Imports <https://www.python.org/dev/peps/pep-0008/#imports>`_  should be ordered.
- Constants and the content of lists and dictionaries should be in alphabetical order.
- It is advisable to adjust IDE or editor settings to match those requirements.

Ordering of imports
-------------------

Instead of ordering the imports manually, use `isort <https://github.com/timothycrosley/isort>`_.

Use new style string formatting
-------------------------------

Prefer `f-strings <https://docs.python.org/3/reference/lexical_analysis.html#f-strings>`_ over ``%`` or ``str.format``.

.. code-block:: python

    #New
    f"{some_value} {some_other_value}"
    # Old, wrong
    "{} {}".format("New", "style")
    "%s %s" % ("Old", "style")

One exception is for logging which uses the percentage formatting. This is to avoid formatting the log message when it is suppressed.

.. code-block:: python

    _LOGGER.info("Can't connect to the webservice %s at %s", string1, string2)


Testing
--------
You'll need to install the test dependencies into your Python environment:

.. code-block:: bash

    pip3 install -r requirements_dev.txt

Now that you have all test dependencies installed, you can run linting and tests on the project:

.. code-block:: bash

    isort generator
    codespell generator
    black generator
    flake8 generator
    pylint generator
    pydocstyle generator

Resources
=========

- Streaming Analytics Quick Start https://docs.microsoft.com/en-us/azure/stream-analytics/quick-create-azure-cli
- Streaming Analytics References https://docs.microsoft.com/en-us/cli/azure/stream-analytics/input?view=azure-cli-latest#az_stream_analytics_input_create
- 

.. |architecture-overview| image:: docs/StreamingAnalyticsDemoArchitecture.png