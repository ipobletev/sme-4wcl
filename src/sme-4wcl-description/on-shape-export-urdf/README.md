# Onshape to Robot Test Repository

This repository provides a testing ground for converting [Onshape](https://www.onshape.com/) assemblies into robot description formats (URDF) using the `onshape-to-robot` tool.

## Prerequisites

- Python 3.x
- Onshape account and API keys (https://cad.onshape.com/user/developer/apiKeys)

## Setup Instructions

1.  **Environment Setup**:
    Run the `launch_app.sh` script to create a virtual environment and install the necessary dependencies:
    ```bash
    chmod +x launch_app.sh
    
    ./launch_app.sh

    source .venv/bin/activate (Linux) 
    .venv/Scripts/activate (Windows)
    ```
    *Note: On Windows (Git Bash), this script will handle the activation differences.*

2.  **Configuration**:
    - **API Keys**: Create a `.env` file in the root directory (based on `.env.example` if available) with your Onshape API credentials:
      ```env
      ONSHAPE_API=https://cad.onshape.com
      ONSHAPE_ACCESS_KEY=Your_Access_Key
      ONSHAPE_SECRET_KEY=Your_Secret_Key
      ```
    - **Robot Configuration**: Create folder `my-robot` and file `my-robot/config.json` to point to your Onshape assembly:
      ```json
      {
            // Onshape URL of the assembly
          "url": "https://cad.onshape.com/documents/11a7f59e37f711d732274fca/w/7807518dc67487ad405722c8/e/5233c6445c575366a6cc0d50",
          // Output format
          "output_format": "urdf"
      }
      ```

## Usage

### 1. Convert Assembly to URDF
To start the conversion process, run:
```bash
onshape-to-robot my-robot
```
Windows: replace '\\' for '/' (Check weird \ in the output urdf file)

### 2. Test
Upload the generated URDF folder to the following website:

```bash
https://viewer.robotsfan.com/
```

Also you can test the robot using bullet:

```bash
onshape-to-robot-bullet my-robot
```

## References
- [onshape-to-robot documentation](https://onshape-to-robot.readthedocs.io/en/latest/getting_started.html)