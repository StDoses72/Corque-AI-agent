from langchain_core.tools import tool
import os
from pathlib import Path
from config.settings import settings
import sys
import subprocess



@tool
def readFile(filePath: str) -> str:
    '''
    This function reads a file and returns the content of the file.
    You can use it to read the content of a file. 

    Args:
        filePath (str): The path to the file to read.
    Returns:
        str: The content of the file.
    '''
    try:
        with open(filePath, 'r') as file:
            return file.read()
    except Exception as e:
        return f"Error happens in reading the file: {str(e)}"

@tool
def writeFile(filePath: str, content: str) -> str:
    '''
    Write text content to a file at the specified path.
    
    CRITICAL NOTES:
    1. This operation will OVERWRITE any existing file at `filePath`.
    2. Ensure the path is correct.
    3. If the file is written successfully, DO NOT write it again unless you need to correct errors.

    Args:
        filePath (str): The path to the file to write to.
        content (str): The content to write to the file.
    Returns:
        str: A confirmation message if the file is written successfully, or an error message otherwise.
    '''
    try:
        with open(filePath, 'w') as file:
            file.write(content)
        return f"The file '{filePath}' was written successfully."
    except Exception as e:
        return f"Error happens in writing the file: {str(e)}"

@tool
def runShellCommand(command: str) -> str:
    '''
    This function runs a shell command and returns the output of the command.
    You are given with the FULL ACCESS to the shell.
    You can use it to run a shell command. 
    When using this tool, you need to use the appropriate shell command for the system you are running on to run the command.
    You can use the `systemInfo` tool to get the system information to determine the appropriate shell command for the system you are running on.
    Args:
        command (str): The command to run.
    Returns:
        str: The output of the command.
    '''
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True,timeout=30)
        output = f"The command '{command}' was executed"
        if result.returncode == 0:
            output += f"successfully with output:\n{result.stdout}"
        else:
            output += f"with error:\n{result.stderr}"
        return output
    except Exception as e:
        return f"Error happens in running the command: {str(e)}"

@tool
def systemInfo() -> str:
    '''
    This function returns the system information.
    You can use it to get the system information.
    Args:
        None
    Returns:
        str: The system information.
    '''
    try:
        return f"The system information is: {sys.platform()}"
    except Exception as e:
        return f"Error happens in getting the system information: {str(e)}"