"""
Command-line interface for the todo application with modern UI/UX.
"""

import sys
from typing import List
from .task_manager import TaskManager
from .task import Task
from .utils import is_valid_task_id, parse_task_id

try:
    # Try to import colorama for colored output
    from colorama import init, Fore, Style
    init()  # Initialize colorama
    COLORS_AVAILABLE = True
except ImportError:
    # If colorama is not available, use basic strings
    class MockColor:
        RED = ""
        GREEN = ""
        YELLOW = ""
        BLUE = ""
        MAGENTA = ""
        CYAN = ""
        WHITE = ""
        RESET = ""

    class MockStyle:
        BRIGHT = ""
        DIM = ""
        RESET_ALL = ""

    Fore = MockColor()
    Style = MockStyle()
    COLORS_AVAILABLE = False


class TodoCLI:
    """
    Command-line interface for the todo application with modern UI/UX.
    """

    def __init__(self) -> None:
        """
        Initialize the CLI with a task manager.
        """
        self.task_manager = TaskManager()
        self._print_header()

    def _print_header(self) -> None:
        """
        Print the application header with styling.
        """
        header = f"""
{Fore.CYAN}+{'='*70}+
|{Style.BRIGHT}                           TODO APP                                   {Style.RESET_ALL}|{Fore.CYAN}
|                          Your Personal Task Manager                            |
+{'='*70}+{Style.RESET_ALL}
        """
        print(header)

    def _print_menu(self) -> None:
        """
        Print the available commands menu with styling.
        """
        menu = f"""
{Fore.YELLOW}+{'='*70}+{Style.RESET_ALL}
{Fore.YELLOW}|{Style.BRIGHT}                                MENU                                      {Style.RESET_ALL}{Fore.YELLOW}|{Style.RESET_ALL}
{Fore.YELLOW}+{'='*70}+{Style.RESET_ALL}
{Fore.YELLOW}|{Fore.GREEN} • add \"title\" \"description\"     {Fore.WHITE}- Add a new task                         {Fore.YELLOW}|{Style.RESET_ALL}
{Fore.YELLOW}|{Fore.GREEN} • list                          {Fore.WHITE}- Show all tasks                        {Fore.YELLOW}|{Style.RESET_ALL}
{Fore.YELLOW}|{Fore.GREEN} • update <id> \"title\" \"desc\"    {Fore.WHITE}- Update a task                         {Fore.YELLOW}|{Style.RESET_ALL}
{Fore.YELLOW}|{Fore.GREEN} • delete <id>                   {Fore.WHITE}- Remove a task                         {Fore.YELLOW}|{Style.RESET_ALL}
{Fore.YELLOW}|{Fore.GREEN} • complete <id>                 {Fore.WHITE}- Toggle task completion                {Fore.YELLOW}|{Style.RESET_ALL}
{Fore.YELLOW}|{Fore.GREEN} • quit                          {Fore.WHITE}- Exit the application                  {Fore.YELLOW}|{Style.RESET_ALL}
{Fore.YELLOW}+{'='*70}+{Style.RESET_ALL}
        """
        print(menu)

    def run(self) -> None:
        """
        Run the interactive command-line interface.
        """
        self._print_menu()
        print(f"{Fore.CYAN}Tip: Type 'menu' to see available commands again{Style.RESET_ALL}\n")

        while True:
            try:
                user_input = input(f"{Fore.BLUE}[{Fore.GREEN}TodoApp{Fore.BLUE}]> {Style.RESET_ALL}").strip()
                if not user_input:
                    continue

                if user_input.lower() == 'quit':
                    print(f"\n{Fore.CYAN}Goodbye! Have a productive day!{Style.RESET_ALL}")
                    break
                elif user_input.lower() == 'menu':
                    self._print_menu()
                    continue

                self._process_command(user_input)
            except KeyboardInterrupt:
                print(f"\n\n{Fore.CYAN}Goodbye! Have a productive day!{Style.RESET_ALL}")
                break
            except EOFError:
                print(f"\n{Fore.CYAN}Goodbye! Have a productive day!{Style.RESET_ALL}")
                break

    def _process_command(self, user_input: str) -> None:
        """
        Process a command from the user input.

        Args:
            user_input: The raw command input from the user
        """
        parts = user_input.split()
        if not parts:
            return

        command = parts[0].lower()

        if command == 'add':
            self._handle_add(parts)
        elif command == 'list':
            self._handle_list()
        elif command == 'update':
            self._handle_update(parts)
        elif command == 'delete':
            self._handle_delete(parts)
        elif command == 'complete':
            self._handle_complete(parts)
        else:
            print(f"{Fore.RED}ERROR: Unknown command: {command}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Tip: Type 'menu' to see available commands{Style.RESET_ALL}")

    def _handle_add(self, parts: List[str]) -> None:
        """
        Handle the 'add' command to add a new task.

        Args:
            parts: List of command parts from user input
        """
        if len(parts) < 2:
            print(f'{Fore.RED}ERROR: Usage: add "title" "description" (description is optional){Style.RESET_ALL}')
            return

        # For the add command, we need to parse the quoted arguments properly
        args_str = ' '.join(parts[1:])
        title, description = self._parse_add_arguments(args_str)

        if not title:
            print(f"{Fore.RED}ERROR: Title is required. Usage: add \"title\" \"description\"{Style.RESET_ALL}")
            return

        task = self.task_manager.add_task(title, description)
        print(f"{Fore.GREEN}SUCCESS: Added task #{task.id}: {task.title}{Style.RESET_ALL}")

    def _parse_add_arguments(self, args_str: str) -> tuple[str, str]:
        """
        Parse the arguments for the add command, handling quoted strings.

        Args:
            args_str: The arguments part of the add command

        Returns:
            A tuple of (title, description) where description may be empty
        """
        import re
        # Find quoted strings using regex
        quoted_strings = re.findall(r'"([^"]*)"', args_str)

        if len(quoted_strings) >= 1:
            title = quoted_strings[0]
        else:
            title = ""

        if len(quoted_strings) >= 2:
            description = quoted_strings[1]
        else:
            description = ""

        return title, description

    def _handle_list(self) -> None:
        """
        Handle the 'list' command to display all tasks.
        """
        tasks = self.task_manager.list_tasks()

        if not tasks:
            print(f"{Fore.YELLOW}INFO: No tasks found. Add a task to get started!{Style.RESET_ALL}")
            return

        print(f"\n{Fore.CYAN}YOUR TASKS ({len(tasks)} total){Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'=' * 50}{Style.RESET_ALL}")

        for i, task in enumerate(tasks):
            status_symbol = "DONE" if task.completed else "TODO"
            status_color = Fore.GREEN if task.completed else Fore.YELLOW
            id_color = Fore.MAGENTA

            print(f"[{status_color}{status_symbol}{Style.RESET_ALL}] {id_color}#{task.id}{Style.RESET_ALL}. {task.title}")

            if task.description:
                print(f"     {Fore.WHITE}Desc: {task.description}{Style.RESET_ALL}")

            if i < len(tasks) - 1:  # Add separator between tasks except the last one
                print(f"{Fore.CYAN}{'-' * 30}{Style.RESET_ALL}")

    def _handle_update(self, parts: List[str]) -> None:
        """
        Handle the 'update' command to update a task.

        Args:
            parts: List of command parts from user input
        """
        if len(parts) < 2:
            print(f"{Fore.RED}ERROR: Usage: update <id> \"new_title\" \"new_description\"{Style.RESET_ALL}")
            return

        task_id_str = parts[1]
        if not is_valid_task_id(task_id_str):
            print(f"{Fore.RED}ERROR: Invalid task ID. Please provide a positive integer.{Style.RESET_ALL}")
            return

        task_id = parse_task_id(task_id_str)
        if not self.task_manager.get_task(task_id):
            print(f"{Fore.RED}ERROR: Task with ID {task_id} does not exist. Please try again with a different ID.{Style.RESET_ALL}")
            return

        # Parse the new title and description
        args_str = ' '.join(parts[2:])
        new_title, new_description = self._parse_add_arguments(args_str)

        # Update the task
        success = self.task_manager.update_task(
            task_id,
            title=new_title if new_title else None,
            description=new_description if new_description else None
        )

        if success:
            print(f"{Fore.GREEN}SUCCESS: Task #{task_id} updated successfully.{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}ERROR: Failed to update task #{task_id}.{Style.RESET_ALL}")

    def _handle_delete(self, parts: List[str]) -> None:
        """
        Handle the 'delete' command to delete a task.

        Args:
            parts: List of command parts from user input
        """
        if len(parts) < 2:
            print(f"{Fore.RED}ERROR: Usage: delete <id>{Style.RESET_ALL}")
            return

        task_id_str = parts[1]
        if not is_valid_task_id(task_id_str):
            print(f"{Fore.RED}ERROR: Invalid task ID. Please provide a positive integer.{Style.RESET_ALL}")
            return

        task_id = parse_task_id(task_id_str)
        if not self.task_manager.get_task(task_id):
            print(f"{Fore.RED}ERROR: Task with ID {task_id} does not exist. Please try again with a different ID.{Style.RESET_ALL}")
            return

        success = self.task_manager.delete_task(task_id)
        if success:
            print(f"{Fore.GREEN}SUCCESS: Task #{task_id} deleted successfully.{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}ERROR: Failed to delete task #{task_id}.{Style.RESET_ALL}")

    def _handle_complete(self, parts: List[str]) -> None:
        """
        Handle the 'complete' command to toggle task completion status.

        Args:
            parts: List of command parts from user input
        """
        if len(parts) < 2:
            print(f"{Fore.RED}ERROR: Usage: complete <id>{Style.RESET_ALL}")
            return

        task_id_str = parts[1]
        if not is_valid_task_id(task_id_str):
            print(f"{Fore.RED}ERROR: Invalid task ID. Please provide a positive integer.{Style.RESET_ALL}")
            return

        task_id = parse_task_id(task_id_str)
        if not self.task_manager.get_task(task_id):
            print(f"{Fore.RED}ERROR: Task with ID {task_id} does not exist. Please try again with a different ID.{Style.RESET_ALL}")
            return

        success = self.task_manager.toggle_task_status(task_id)
        if success:
            task = self.task_manager.get_task(task_id)
            if task and task.completed:
                print(f"{Fore.GREEN}SUCCESS: Task #{task_id} marked as complete.{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}INFO: Task #{task_id} marked as pending.{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}ERROR: Failed to toggle status for task #{task_id}.{Style.RESET_ALL}")