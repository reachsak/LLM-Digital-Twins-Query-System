


from flask import Flask, request, jsonify
from web3 import Web3
import requests
import json
from llama_cpp_agent.llm_agent import LlamaCppAgent
from llama_cpp_agent.providers.llama_cpp_endpoint_provider import LlamaCppEndpointSettings
from llama_cpp_agent.messages_formatter import MessagesFormatterType
from llama_cpp_agent.function_calling import LlamaCppFunctionTool
from llama_cpp_agent.gbnf_grammar_generator.gbnf_grammar_from_pydantic_models import create_dynamic_model_from_function
from flask_cors import CORS
from yeelight import Bulb
from datetime import datetime
import subprocess
import requests
import uuid
import os
import uuid
import subprocess
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)



  
import random
import time
import threading

def turn_off_light(inner_thoughts: str, command: str) -> str:
    """
    Control the Yeelight bulb.

    Parameters:
        inner_thoughts (str): Inner thoughts to return alongside the action.
        command (str): The command to execute, either "turn on" or "turn off".
        
    Returns:
        str: A message indicating the action taken.
    """
    bulb_ip = "192.168.31.171"  # IP address of the Yeelight bulb
    bulb = Bulb(bulb_ip)
    if command == "turn off":
        bulb.turn_off()
        return f"{inner_thoughts} Light turned off."
    elif command == "turn on":
        bulb.turn_on()
        return f"{inner_thoughts} Light turned on."
    else:
        return "Invalid command. Please provide 'turn on' or 'turn off'."

import subprocess
import json
from typing import List, Any


import subprocess

def list_rooms(inner_thoughts: str, command: str) -> str:
    """
    Executes the list-rooms.py script and returns its output.

    Parameters:
        inner_thoughts (str): Inner thoughts to log alongside the action.
        command (str): The command to execute (ignored in this case).

    Returns:
        str: The output of the list-rooms.py script.
    """
    try:
        script_path = "./list-rooms.py"  # Ensure the script is in the same directory
        command_args = ["python3", script_path]

        # Run the script and capture its output
        result = subprocess.run(command_args, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Return the output of the script
        return result.stdout

    except subprocess.CalledProcessError as e:
        print(f"{inner_thoughts} Error occurred while executing list-rooms.py: {e}")
        return ""
    except Exception as e:
        print(f"{inner_thoughts} Unexpected error: {e}")
        return ""

def list_levels(inner_thoughts: str, command: str) -> str:
    """
    Executes the list-levels.py script and returns its output.

    This function runs the `list-levels.py` script to fetch and return a list of levels
    from the system or server, depending on how the script is designed. It captures 
    and returns the script's standard output.

    Parameters:
        inner_thoughts (str): A log message to track the internal processing state.
        command (str): A command string (currently unused, but kept for potential future use).

    Returns:
        str: The output of the `list-levels.py` script, typically a list of building levels or floors.
    """
    try:
        script_path = "./list-levels.py"  # Ensure the script is in the same directory
        command_args = ["python3", script_path]

        # Run the script and capture its output
        result = subprocess.run(command_args, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Return the output of the script
        return result.stdout

    except subprocess.CalledProcessError as e:
        print(f"{inner_thoughts} Error occurred while executing list-levels.py: {e}")
        return ""
    except Exception as e:
        print(f"{inner_thoughts} Unexpected error: {e}")
        return ""
    
    
import subprocess

def list_element_rooms(inner_thoughts: str, command: str) -> str:
    """
    Executes the list-element-rooms.py script and returns its output.

    This function runs the `list-element-rooms.py` script to fetch and return a list 
    of elements and their associated rooms. The script's output is captured and returned.

    Parameters:
        inner_thoughts (str): A log message to track the internal processing state.
        command (str): A command string (currently unused, but kept for potential future use).

    Returns:
        str: The output of the `list-element-rooms.py` script, typically a mapping of elements to rooms.
    """
    try:
        script_path = "./list-element-rooms.py"
        command_args = ["python3", script_path]

        result = subprocess.run(command_args, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        return result.stdout

    except subprocess.CalledProcessError as e:
        print(f"{inner_thoughts} Error occurred while executing list-element-rooms.py: {e}")
        return ""
    except Exception as e:
        print(f"{inner_thoughts} Unexpected error: {e}")
        return ""


def list_facility_structure(inner_thoughts: str, command: str) -> str:
    """
    Executes the list-facility-structure.py script and returns its output.

    This function runs the `list-facility-structure.py` script to fetch and return 
    the structure or hierarchy of a facility. The script's output is captured and returned.

    Parameters:
        inner_thoughts (str): A log message to track the internal processing state.
        command (str): A command string (currently unused, but kept for potential future use).

    Returns:
        str: The output of the `list-facility-structure.py` script, typically a facility hierarchy.
    """
    try:
        script_path = "./list-facility-structure.py"
        command_args = ["python3", script_path]

        result = subprocess.run(command_args, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        return result.stdout

    except subprocess.CalledProcessError as e:
        print(f"{inner_thoughts} Error occurred while executing list-facility-structure.py: {e}")
        return ""
    except Exception as e:
        print(f"{inner_thoughts} Unexpected error: {e}")
        return ""


def list_level_assets(inner_thoughts: str, command: str) -> str:
    """
    Executes the list-level-assets.py script and returns its output.

    This function runs the `list-level-assets.py` script to fetch and return a list 
    of assets for a specific level or levels. The script's output is captured and returned.

    Parameters:
        inner_thoughts (str): A log message to track the internal processing state.
        command (str): A command string (currently unused, but kept for potential future use).

    Returns:
        str: The output of the `list-level-assets.py` script, typically a list of assets on a level.
    """
    try:
        script_path = "./list-level-assets.py"
        command_args = ["python3", script_path]

        result = subprocess.run(command_args, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        return result.stdout

    except subprocess.CalledProcessError as e:
        print(f"{inner_thoughts} Error occurred while executing list-level-assets.py: {e}")
        return ""
    except Exception as e:
        print(f"{inner_thoughts} Unexpected error: {e}")
        return ""


def list_level_rooms(inner_thoughts: str, command: str) -> str:
    """
    Executes the list-level-rooms.py script and returns its output.

    This function runs the `list-level-rooms.py` script to fetch and return a list 
    of rooms for a specific level or levels. The script's output is captured and returned.

    Parameters:
        inner_thoughts (str): A log message to track the internal processing state.
        command (str): A command string (currently unused, but kept for potential future use).

    Returns:
        str: The output of the `list-level-rooms.py` script, typically a list of rooms on a level.
    """
    try:
        script_path = "./list-level-rooms.py"
        command_args = ["python3", script_path]

        result = subprocess.run(command_args, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        return result.stdout

    except subprocess.CalledProcessError as e:
        print(f"{inner_thoughts} Error occurred while executing list-level-rooms.py: {e}")
        return ""
    except Exception as e:
        print(f"{inner_thoughts} Unexpected error: {e}")
        return ""

    

DynamicSampleModel2 = create_dynamic_model_from_function(list_rooms, "list rooms")
DynamicSampleModel4 = create_dynamic_model_from_function(list_levels, "list levels")
DynamicSampleModel5 = create_dynamic_model_from_function(list_element_rooms, "list_element_rooms")
DynamicSampleModel6 = create_dynamic_model_from_function(list_facility_structure, "list_facility_structure")
DynamicSampleModel7 = create_dynamic_model_from_function(list_level_assets, "list_level_assets")
DynamicSampleModel8 = create_dynamic_model_from_function(list_level_rooms, "list_level_rooms")

function_tools = [LlamaCppFunctionTool(DynamicSampleModel2),LlamaCppFunctionTool(DynamicSampleModel4),LlamaCppFunctionTool(DynamicSampleModel5),LlamaCppFunctionTool(DynamicSampleModel6),LlamaCppFunctionTool(DynamicSampleModel8),LlamaCppFunctionTool(DynamicSampleModel7)]
function_tool_registry = LlamaCppAgent.get_function_tool_registry(function_tools)
system_prompt = "You are an intelligent AI assistant for managing a smart home environment. Your primary role is to facilitate control over various smart devices, enhancing user comfort and convenience. You can also query data from building data as well"
main_model = LlamaCppEndpointSettings(
    completions_endpoint_url="http://127.0.0.1:8080/completion"
)
llama_cpp_agent = LlamaCppAgent(main_model, debug_output=True,
                                system_prompt=system_prompt + function_tool_registry.get_documentation(),
                                predefined_messages_formatter_type=MessagesFormatterType.CHATML)

app = Flask(__name__)
CORS(app)

@app.route('/process_input', methods=['POST'])
def process_input():
    user_input = request.json.get('input')  # Assuming input is sent as JSON {"input": "user input here"}
    # Process user input using AI model
    ai_response = llama_cpp_agent.get_chat_response(user_input, temperature=0.3, function_tool_registry=function_tool_registry)
   
    return str(ai_response[0]['return_value'])

if __name__ == '__main__':
    app.run(host='localhost', port=1234, debug=True) 

#64538121593627479219236717456296040253649251070565921025083761489207682213087