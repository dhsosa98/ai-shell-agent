import os
import json
import argparse
from dotenv import load_dotenv
from .llms import get_provider, get_model
from colorama import Fore, Style

# Load environment variables from .env if available.
load_dotenv()

from . import logger

# Ensure the API key is set before any other operations
# ---------------------------
# API Key Management
# ---------------------------

def _set_env_file(key: str, value: str) -> None:
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    if not os.path.exists(env_path):
        with open(env_path, "w") as f:
            f.write("")

    try:
        with open(env_path, "r") as f:
            content = f.read()
        
        # Parse existing content into a dict
        env_vars = {}
        for line in content.splitlines():
            if line.strip() and "=" in line:
                k, v = line.split("=", 1)
                env_vars[k.strip()] = v.strip()
        
        # Update/add new value
        env_vars[key] = value
        
        # Write back all variables
        with open(env_path, "w") as f:
            for k, v in env_vars.items():
                f.write(f"{k}={v}\n")
                
        logger.info(f"{key} saved successfully to .env")
    except Exception as e:
        logger.error(f"Failed to write to .env: {e}")

def get_api_key() -> str:
    """Retrieve the GOOGLE API key or OPENAI API key from the environment."""
    if get_provider() == "google":
        return os.getenv("GOOGLE_API_KEY")
    else:
        return os.getenv("OPENAI_API_KEY")

def set_api_key(api_key: str = None) -> None:
    """
    Prompt the user for an GOOGLE API key and save it to the .env file.
    Aborts if no key is entered.
    """
    if not api_key:
        if get_provider() == "google":
            api_key = input("Enter GOOGLE API key: ").strip()
        else:
            api_key = input("Enter OPENAI API key: ").strip()
    if not api_key:
        logger.warning("No API key entered. Aborting.")
        return
    if get_provider() == "google":
        os.environ["GOOGLE_API_KEY"] = api_key
    else:
        os.environ["OPENAI_API_KEY"] = api_key
        
    if get_provider() == "google":
        _set_env_file("GOOGLE_API_KEY", api_key)
    else:
        _set_env_file("OPENAI_API_KEY", api_key)


def ensure_api_key() -> None:
    """
    Ensure that the GOOGLE API or OPENAI API key is set. If not, prompt the user to enter it.
    """
    if not get_api_key():
        logger.warning(f"{get_provider()} API key not found. Please enter your API key.")
        set_api_key()
        
def set_provider(provider: str = None) -> None:
    """
    Set the provider.
    """
    if not provider:
        provider = input("Enter provider: ").strip()
    os.environ["PROVIDER"] = provider
    
    _set_env_file("PROVIDER", provider)
    
def get_provider() -> str:
    """
    Get the provider.
    """
    return os.getenv("PROVIDER")
    
def ensure_provider() -> None:
    """
    Ensure that the provider is set. If not, prompt the user to enter it.
    """
    if not get_provider():
        logger.warning("Provider not found. Please enter your provider.")
        set_provider()
        
def set_temperature(temperature: float = None) -> None:
    """
    Set the temperature.
    """
    if not temperature:
        temperature = input("Enter temperature: ").strip()
    os.environ["TEMPERATURE"] = temperature
    
    _set_env_file("TEMPERATURE", temperature)
    
def get_temperature() -> float:
    """
    Get the temperature.
    """
    return os.getenv("TEMPERATURE")

ensure_provider()
ensure_api_key()

from .chat_manager import (
    create_or_load_chat,
    get_chat_titles_list,
    rename_chat,
    delete_chat,
    load_session,
    save_session,
    send_message,
    edit_message,
    start_temp_chat,
    set_default_system_prompt,
    update_system_prompt,
    flush_temp_chats,
    execute,
    list_messages,
    current_chat_title
)

# ---------------------------
# CLI Command Handling
# ---------------------------

class ColoredHelpFormatter(argparse.HelpFormatter):
    def __init__(self, prog):
        super().__init__(prog, max_help_position=50, width=100)

    def _format_action_invocation(self, action):
        if not action.option_strings:
            default = self._get_default_metavar_for_positional(action)
            metavar = action.metavar or default
            return Fore.CYAN + metavar + Style.RESET_ALL
        else:
            parts = []
            if action.option_strings:
                parts.extend(Fore.YELLOW + option + Style.RESET_ALL for option in action.option_strings)
            if action.nargs != 0:
                default = self._get_default_metavar_for_optional(action)
                args_string = self._format_args(action, default)
                parts.append(Fore.CYAN + args_string + Style.RESET_ALL)
            return ' '.join(parts)

    def _format_usage(self, usage, actions, groups, prefix):
        if prefix is None:
            prefix = Fore.GREEN + 'Usage: ' + Style.RESET_ALL
        return super()._format_usage(usage, actions, groups, prefix)

    def _format_action(self, action):
        help_text = self._expand_help(action)
        if help_text:
            help_text = Fore.WHITE + help_text + Style.RESET_ALL
        return super()._format_action(action)

def main():
    try:
        load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
        ensure_provider()
        ensure_api_key()
        parser = argparse.ArgumentParser(
            description=Fore.CYAN + "AI Command-Line Chat Application" + Style.RESET_ALL,
            formatter_class=ColoredHelpFormatter
        )
        # API Key Management and model settings
        parser.add_argument("-p", "--provider", nargs="?", const=True, help="Set the provider")
        parser.add_argument("-k", "--set-api-key", nargs="?", const=True, help="Set or update the API key")
        parser.add_argument("-mtemp", "--model-temperature", nargs="?", const=True, help="Set the temperature of the model. Default is 0")
        
        # Chat management options
        parser.add_argument("-c", "--chat", help="Create or load a chat session with the specified title")
        parser.add_argument("-lc", "--load-chat", help="Load an existing chat session with the specified title")
        parser.add_argument("-lsc", "--list-chats", action="store_true", help="List all available chat sessions")
        parser.add_argument("-rnc", "--rename-chat", nargs=2, metavar=("OLD_TITLE", "NEW_TITLE"), help="Rename a chat session")
        parser.add_argument("-delc", "--delete-chat", help="Delete a chat session with the specified title")
        
        # System prompt management
        parser.add_argument("--default-system-prompt", help="Set the default system prompt for new chats")
        parser.add_argument("--system-prompt", help="Update the system prompt for the active chat session")
        
        # Messaging commands
        parser.add_argument("-m", "--send-message", help="Send a message to the active chat session")
        parser.add_argument("-tc", "--temp-chat", help="Start a temporary (in-memory) chat session with the initial message")
        parser.add_argument("-e", "--edit", nargs="+", metavar=("INDEX", "NEW_MESSAGE"), help="Edit a previous message at the given index")
        parser.add_argument("--temp-flush", action="store_true", help="Removes all temp chat sessions")
        
        # Add direct command execution
        parser.add_argument("-x", "--execute", help="Execute a shell command preserving its context for AI")
        
        # Print the chat history
        parser.add_argument("-lsm", "--list-messages", action="store_true", help="Print the chat history")
        
        parser.add_argument("-ct", "--current-chat-title", action="store_true", help="Print the current chat title")
        
        # Fallback: echo a simple message.
        parser.add_argument("message", nargs="?", help="Send a message (if no other options are provided)")

        args = parser.parse_args()
        
        # Handle provider management
        if args.provider:
            if args.provider.lower() == "google":
                set_provider("google")
            elif args.provider.lower() == "openai":
                set_provider("openai")
            else:
                logger.error("Invalid provider. Please enter 'google' or 'openai'.")
            return

        # Handle API key management
        if args.set_api_key:
            if isinstance(args.set_api_key, str):
                set_api_key(args.set_api_key)
            else:
                set_api_key()
            return
        
        if args.model_temperature:
            if isinstance(args.model_temperature, str):
                try:
                    temp = float(args.model_temperature)
                    if 0 <= temp <= 1:
                        set_temperature(args.model_temperature)
                    else:
                        logger.error("Temperature must be between 0 and 1")
                except ValueError:
                    logger.error("Temperature must be a number between 0 and 1")
            else:
                logger.error("Temperature must be a number between 0 and 1")
            return

        # Handle direct command execution
        if args.execute:
            output = execute(args.execute)
            return

        # Chat session management
        if args.chat:
            chat_file = create_or_load_chat(args.chat)
            save_session(chat_file)
            return
        
        if args.current_chat_title:
            current_chat_title()
            return

        if args.load_chat:
            chat_file = create_or_load_chat(args.load_chat)
            save_session(chat_file)
            return

        if args.list_chats:
            get_chat_titles_list()
            return

        if args.rename_chat:
            old_title, new_title = args.rename_chat
            rename_chat(old_title, new_title)
            return

        if args.delete_chat:
            delete_chat(args.delete_chat)
            return

        # System prompt management
        if args.default_system_prompt:
            set_default_system_prompt(args.default_system_prompt)
            return

        if args.system_prompt:
            update_system_prompt(args.system_prompt)
            return

        # Messaging commands
        if args.send_message:
            send_message(args.send_message)
            return

        if args.temp_chat:
            start_temp_chat(args.temp_chat)
            return

        if args.edit:
            if len(args.edit) == 1:
                new_message = args.edit[0]
                edit_message(None, new_message)
            elif len(args.edit) == 2:
                index, new_message = args.edit
                if index.lower() == "last":
                    edit_message(None, new_message)
                else:
                    edit_message(int(index), new_message)
            else:
                logger.error("Invalid number of arguments for --edit")
            return

        if args.temp_flush:
            flush_temp_chats()
            return
        
        # Print chat history
        if args.list_messages:
            list_messages()
            return
        # Fallback: if a message is provided without other commands, send it to current chat
        if args.message:
            # Use send_message which handles chat history properly
            send_message(args.message)
            return
        else:
            logger.info("No command provided. Use --help for options.")
            return
    except KeyboardInterrupt:
        logger.info("\nOperation cancelled by user. Exiting gracefully...")
        return

if __name__ == "__main__":
    main()
