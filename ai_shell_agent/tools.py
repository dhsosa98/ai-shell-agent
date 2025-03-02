import subprocess
from langchain.tools import BaseTool, tool
from langchain_core.utils.function_calling import convert_to_openai_function
from langchain_experimental.tools.python.tool import PythonREPLTool
from prompt_toolkit import prompt
from colorama import Fore, Style, Back
from . import logger

class ConsoleTool_HITL(BaseTool):
    name: str = "interactive_windows_shell_tool"
    description: str = (
        "Use this tool to run console commands and view the output."
        "Args:"
        "command (str): The initial shell command proposed by the agent."
        "Returns:"
        "str: The output from executing the edited command."
    )

    def _run(self, command: str) -> str:
        """
        Runs the command after allowing the user to edit it.
        
        Args:
            command (str): The initial shell command proposed by the agent.
        
        Returns:
            str: The output from executing the edited command.
        """
        # Format the command parts with different colors if it contains pipes or redirects
        formatted_cmd = self._format_command(command)
        
        # Display a nice box with the command
        width = 80  # Default width
        try:
            # Get terminal size
            import os
            terminal_size = os.get_terminal_size()
            width = terminal_size.columns
        except:
            pass  # Fallback to default width if can't get terminal size
            
        print(f"{Style.RESET_ALL} {Fore.RESET}❯ Got some code!{Style.RESET_ALL}{' ' * (width - 18)}{Fore.CYAN}")
        print(f"-" * width)
        print(f"{Style.RESET_ALL} {formatted_cmd}{' ' * (width - len(command) - 3)}{Fore.CYAN}")
        print(f"-" * width)
        
        # Prompt for command acceptance or edit
        print(f"{Fore.YELLOW}╰─> Run the generated command? [Accept/Edit] ▶{Style.RESET_ALL}")
        edited_command = prompt(f">", default=command)
        
        logger.debug(f"Executing command: {edited_command}")
        
        try:
            result = subprocess.run(
                edited_command,
                shell=True,
                capture_output=True,
                text=True,
                check=True
            )
            output = result.stdout
            
            if output.strip():
                print(f"{Fore.CYAN}╭{'─' * 18}╮{Style.RESET_ALL}")
                print(f"{Fore.CYAN}│{Style.RESET_ALL} {Fore.GREEN}Command Output{Style.RESET_ALL} {Fore.CYAN}│{Style.RESET_ALL}")
                print(f"{Fore.CYAN}╰{'─' * 18}╯{Style.RESET_ALL}")
                print(f"{output}")
            else:
                print(f"{Fore.YELLOW}Command executed with no output.{Style.RESET_ALL}")
                
            logger.info(f"{output}")
            return output
        except subprocess.CalledProcessError as e:
            error_msg = f"{Fore.RED}╭{'─' * 16}╮{Style.RESET_ALL}\n"
            error_msg += f"{Fore.RED}│{Style.RESET_ALL} {Fore.RED}Error Detected{Style.RESET_ALL} {Fore.RED}│{Style.RESET_ALL}\n"
            error_msg += f"{Fore.RED}╰{'─' * 16}╯{Style.RESET_ALL}\n"
            error_msg += f"{Fore.RED}{e.stderr}{Style.RESET_ALL}"
            print(error_msg)
            logger.error(f"Error: {e.stderr}")
            return f"Error: {e.stderr}"

    def _format_command(self, command: str) -> str:
        """Format a command with colors for pipes, redirects, and arguments."""
        parts = []
        current_part = ""
        in_quotes = False
        quote_char = None
        
        for char in command:
            if char in ['"', "'"]:
                if not in_quotes:
                    in_quotes = True
                    quote_char = char
                    current_part += f"{Fore.GREEN}{char}"
                elif quote_char == char:
                    in_quotes = False
                    current_part += f"{char}{Style.RESET_ALL}"
                else:
                    current_part += char
            elif char in ['|', '>', '<'] and not in_quotes:
                if current_part:
                    parts.append(current_part)
                    current_part = ""
                parts.append(f"{Fore.YELLOW}{char}{Style.RESET_ALL}")
            else:
                current_part += char
                
        if current_part:
            parts.append(current_part)
            
        # Color the first command (executable)
        if parts and ' ' in parts[0]:
            cmd, *args = parts[0].split(' ', 1)
            parts[0] = f"{Fore.MAGENTA}{cmd}{Style.RESET_ALL} {args[0]}"
            
        return " ".join(parts)

    async def _arun(self, command: str) -> str:
        """
        Asynchronous implementation of running a command.
        
        Args:
            command (str): The initial shell command proposed by the agent.
        
        Returns:
            str: The output from executing the edited command.
        """
        return self._run(command)


class ConsoleTool_Direct(BaseTool):
    name: str = "direct_windows_shell_tool"
    description: str = "Executes a console command directly without user confirmation."

    def _run(self, command: str) -> str:
        """
        Runs the shell command directly without user confirmation.
        
        Args:
            command (str): The shell command to execute.
        
        Returns:
            str: The output from executing the command.
        """
        formatted_cmd = self._format_command(command)
        print(f"{Fore.CYAN}▶ {formatted_cmd}{Style.RESET_ALL}")
        logger.debug(f"> {formatted_cmd}")
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                check=True
            )
            output = result.stdout
            
            if output.strip():
                print(f"{Fore.CYAN}╭{'─' * 18}╮{Style.RESET_ALL}")
                print(f"{Fore.CYAN}│{Style.RESET_ALL} {Fore.GREEN}Command Output{Style.RESET_ALL} {Fore.CYAN}│{Style.RESET_ALL}")
                print(f"{Fore.CYAN}╰{'─' * 18}╯{Style.RESET_ALL}")
                print(f"{output}")
            
            logger.info(f"{output}")
            return output
        except subprocess.CalledProcessError as e:
            error_msg = f"{Fore.RED}╭{'─' * 16}╮{Style.RESET_ALL}\n"
            error_msg += f"{Fore.RED}│{Style.RESET_ALL} {Fore.RED}Error Detected{Style.RESET_ALL} {Fore.RED}│{Style.RESET_ALL}\n"
            error_msg += f"{Fore.RED}╰{'─' * 16}╯{Style.RESET_ALL}\n"
            error_msg += f"{Fore.RED}{e.stderr}{Style.RESET_ALL}"
            print(error_msg)
            logger.error(f"Error: {e.stderr}")
            return f"Error: {e.stderr}"
            
    def _format_command(self, command: str) -> str:
        """Format a command with colors for pipes, redirects, and arguments."""
        parts = []
        current_part = ""
        in_quotes = False
        quote_char = None
        
        for char in command:
            if char in ['"', "'"]:
                if not in_quotes:
                    in_quotes = True
                    quote_char = char
                    current_part += f"{Fore.GREEN}{char}"
                elif quote_char == char:
                    in_quotes = False
                    current_part += f"{char}{Style.RESET_ALL}"
                else:
                    current_part += char
            elif char in ['|', '>', '<'] and not in_quotes:
                if current_part:
                    parts.append(current_part)
                    current_part = ""
                parts.append(f"{Fore.YELLOW}{char}{Style.RESET_ALL}")
            else:
                current_part += char
                
        if current_part:
            parts.append(current_part)
            
        # Color the first command (executable)
        if parts and ' ' in parts[0]:
            cmd, *args = parts[0].split(' ', 1)
            parts[0] = f"{Fore.MAGENTA}{cmd}{Style.RESET_ALL} {args[0]}"
            
        return " ".join(parts)

    async def _arun(self, command: str) -> str:
        """
        Asynchronous implementation of running a command.
        
        Args:
            command (str): The shell command to execute.
        
        Returns:
            str: The output from executing the command.
        """
        return self._run(command)

# Initialize the built-in Python REPL tool
python_repl_tool = PythonREPLTool(
    name="run_python_code",
)
interactive_windows_shell_tool = ConsoleTool_HITL()
direct_windows_shell_tool = ConsoleTool_Direct()

tools = [
    interactive_windows_shell_tool,
    python_repl_tool,
    
]

tools_functions = [convert_to_openai_function(t) for t in tools]