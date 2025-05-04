import os
import sys
import psycopg
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
import logging
from typing import Dict, Any, Optional, List, Tuple
from collections import defaultdict
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.sql import SQLTools

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - [%(name)s] - %(message)s')

# --- Helper Function to Get Schema String ---
def get_schema_string(db_conn_info: str, target_tables: Optional[List[str]] = None) -> str:
    """
    Connects to the DB and retrieves CREATE TABLE statements for specified tables
    using information_schema.
    """
    schema_str = ""
    all_tables_in_db = []
    logging.info(f"Attempting to retrieve database schema using information_schema (Target tables: {target_tables or 'All'})...")

    try:
        with psycopg.connect(db_conn_info) as conn:
            with conn.cursor() as cur:
                # Get all table names in public schema
                cur.execute("""
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
                """)
                all_tables_in_db = [t[0] for t in cur.fetchall()]
                if not all_tables_in_db:
                    logging.warning("No tables found in public schema.")
                    return "-- No tables found in public schema --"

                # Determine which tables to get schema for
                tables_to_query = []
                if target_tables:
                    tables_to_query = [t for t in target_tables if t in all_tables_in_db]
                    if not tables_to_query:
                         logging.warning(f"None of the target tables {target_tables} found in the database {all_tables_in_db}.")
                         return f"-- Target tables {target_tables} not found --"
                else:
                    tables_to_query = all_tables_in_db

                logging.info(f"Fetching schema for tables: {tables_to_query}")

                # Fetch column definitions for the target tables
                placeholders = ', '.join(['%s'] * len(tables_to_query))
                cur.execute(f"""
                    SELECT
                        table_name,
                        column_name,
                        data_type,
                        is_nullable,
                        column_default,
                        character_maximum_length,
                        numeric_precision,
                        numeric_scale
                    FROM information_schema.columns
                    WHERE table_schema = 'public' AND table_name IN ({placeholders})
                    ORDER BY table_name, ordinal_position;
                """, tables_to_query)
                columns_data = cur.fetchall()

                # Group columns by table
                table_columns = defaultdict(list)
                for row in columns_data:
                    table_name, col_name, dtype, nullable, default, char_len, num_prec, num_scale = row
                    col_def = f'"{col_name}" {dtype.upper()}' # Start with name and type
                    if char_len:
                        col_def += f'({char_len})'
                    elif dtype.lower() in ('numeric', 'decimal') and num_prec is not None:
                        col_def += f'({num_prec}'
                        if num_scale is not None:
                            col_def += f',{num_scale}'
                        col_def += ')'
                    if nullable == 'NO':
                        col_def += ' NOT NULL'
                    if default is not None:
                        if 'nextval' in default: pass
                        else: col_def += f' DEFAULT {default}'
                    table_columns[table_name].append(col_def)

                # Fetch primary key constraints
                cur.execute(f"""
                    SELECT tc.table_name, kcu.column_name
                    FROM information_schema.table_constraints AS tc
                    JOIN information_schema.key_column_usage AS kcu ON tc.constraint_name = kcu.constraint_name AND tc.table_schema = kcu.table_schema
                    WHERE tc.constraint_type = 'PRIMARY KEY' AND tc.table_schema = 'public' AND tc.table_name IN ({placeholders});
                """, tables_to_query)
                pk_data = cur.fetchall()
                primary_keys = defaultdict(list)
                for table_name, col_name in pk_data: primary_keys[table_name].append(f'"{col_name}"')

                # Fetch foreign key constraints (simplified version)
                cur.execute(f"""
                    SELECT tc.table_name, kcu.column_name, ccu.table_name AS foreign_table_name, ccu.column_name AS foreign_column_name
                    FROM information_schema.table_constraints AS tc
                    JOIN information_schema.key_column_usage AS kcu ON tc.constraint_name = kcu.constraint_name AND tc.table_schema = kcu.table_schema
                    JOIN information_schema.constraint_column_usage AS ccu ON ccu.constraint_name = tc.constraint_name AND ccu.table_schema = tc.table_schema
                    WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_schema = 'public' AND tc.table_name IN ({placeholders});
                 """, tables_to_query)
                fk_data = cur.fetchall()
                foreign_keys = defaultdict(list)
                for tbl, col, ftbl, fcol in fk_data: foreign_keys[tbl].append(f'FOREIGN KEY ("{col}") REFERENCES public."{ftbl}" ("{fcol}")')

                # Construct CREATE TABLE statements
                for table_name in tables_to_query:
                    if table_name not in table_columns: continue
                    schema_str += f'CREATE TABLE public."{table_name}" (\n'
                    defs = table_columns[table_name]
                    if table_name in primary_keys: defs.append(f'PRIMARY KEY ({", ".join(primary_keys[table_name])})')
                    if table_name in foreign_keys: defs.extend(foreign_keys[table_name])
                    schema_str += ',\n'.join([f'    {d}' for d in defs])
                    schema_str += '\n);\n\n'

        if not schema_str: return f"-- Schema reconstruction failed for tables: {tables_to_query} --"
        logging.info("Successfully reconstructed database schema string using information_schema.")
        return schema_str.strip()
    except psycopg.Error as e:
         logging.error(f"Database error during schema retrieval: {e}", exc_info=True)
         return f"-- Schema retrieval failed: DB Error ({e.sqlstate}) --"
    except Exception as e:
        logging.error(f"Unexpected error retrieving database schema: {e}", exc_info=True)
        return "-- Schema retrieval failed: Unexpected Error --"


# --- Agent Setup Function ---
def setup_sql_agent(db_conn_info: str, openai_api_key: str) -> Optional[Any]:
    """Initializes and returns an Agno SQL Agent."""
    if not openai_api_key: logging.error("OpenAI API Key missing."); return None

    try:
        # 1. Create SQLAlchemy Engine
        from sqlalchemy import create_engine, Engine
        db_uri = f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
        engine: Engine = create_engine(db_uri)
        logging.info("SQLAlchemy engine created.")

        # 2. Initialize the Agno LLM Wrapper
        llm = OpenAIChat(
            api_key=openai_api_key,
            id="gpt-4.1",
            temperature=0.0
        )
        logging.info("Agno OpenAIChat LLM initialized.")

        # 3. Initialize the SQLTools Toolkit
        sql_tools_toolkit = SQLTools(
            db_engine=engine,
            )
        logging.info("Agno SQLTools toolkit initialized.")

        # 4. Initialize the Agno Agent
        agent = Agent(
            model=llm,
            tools=[sql_tools_toolkit],
            debug_mode=True,
        )
        logging.info("Agno Agent initialized successfully with SQLTools toolkit.")

        # 5. Return the Agent instance
        return agent

    except ImportError as e:
         logging.critical(f"Missing dependency during SQL Agent setup: {e}. Install required libraries.", exc_info=True)
         return None
    except Exception as e:
        # Catch errors during initialization (e.g., wrong args to Agno classes)
        logging.critical(f"Failed to initialize Agno SQL Agent components: {e}", exc_info=True)
        return None


# --- Result Display Function ---
def display_final_result(agent_response: Any):
    console = Console()
    logging.debug(f"Raw agent response: {agent_response}")
    if isinstance(agent_response, dict) and 'output' in agent_response:
        final_output = agent_response['output']
        if isinstance(final_output, dict) and 'status' in final_output:
             display_tool_result(final_output)
        elif isinstance(final_output, str):
             console.print(f"[bold blue]Agent Answer:[/bold blue]\n{final_output}")
        else:
             console.print(f"[bold yellow]Agent Response (Output):[/bold yellow] {final_output}")
    elif isinstance(agent_response, str):
         console.print(f"[bold blue]Agent Answer:[/bold blue]\n{agent_response}")
    else:
        console.print(f"[bold yellow]Agent Response (Raw):[/bold yellow] {agent_response}")

def display_tool_result(execution_result: dict):
    # This function might be called less often if the agent processes tool results internally
    console = Console(); status = execution_result.get("status", "unknown"); message = execution_result.get("message", "No message.")
    if status == "error": console.print(f"[bold red]Error:[/bold red] {message}")
    elif status == "success":
        if execution_result.get("type") == "select":
            headers = execution_result.get("headers"); data = execution_result.get("data", [])
            if not data: console.print("[cyan]Query OK, 0 rows returned.[/cyan]")
            elif headers:
                table = Table(title="Query Results")
                for header in headers: table.add_column(header, style="dim", no_wrap=False)
                for row_dict in data: table.add_row(*[str(row_dict.get(h, '')) for h in headers])
                console.print(table)
            else: console.print("[yellow]Warn: Select OK but headers missing.[/yellow]"); console.print(data)
        else: console.print(f"[bold green]Status:[/bold green] {message}")
    else: console.print(f"[bold yellow]Unknown Status:[/bold yellow] {message}")


# --- Main Execution ---
if __name__ == "__main__":
    load_dotenv()
    logging.info("Starting Agno SQL Agent execution (Updated Agent Params)...")

    # --- Python Environment Check ---
    logging.info(f"Running with Python executable: {sys.executable}")
    logging.info(f"Python version: {sys.version}")

    # --- Configurations & Validation ---
    DB_USER = os.getenv("POSTGRES_USER", "agent_user"); DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    DB_HOST = os.getenv("POSTGRES_HOST", "localhost"); DB_PORT = os.getenv("POSTGRES_PORT", "5432")
    DB_NAME = os.getenv("POSTGRES_DB", "agent_db"); OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    if not DB_PASSWORD: logging.critical("CRITICAL: POSTGRES_PASSWORD missing. Exiting."); exit(1)
    if not OPENAI_API_KEY: logging.critical("CRITICAL: OPENAI_API_KEY missing. Exiting."); exit(1)
    try: import sqlalchemy
    except ImportError: logging.critical("CRITICAL: SQLAlchemy not found. Install with 'uv pip install SQLAlchemy psycopg2-binary'. Exiting."); exit(1)

    DB_CONN_INFO = f"dbname='{DB_NAME}' user='{DB_USER}' password='{DB_PASSWORD}' host='{DB_HOST}' port='{DB_PORT}'"

    current_schema_for_display = get_schema_string(DB_CONN_INFO, ['employees', 'departments'])
    if "-- Schema retrieval failed" in current_schema_for_display or "-- No tables found" in current_schema_for_display or "-- Target tables" in current_schema_for_display:
         logging.warning(f"Could not retrieve schema for display ({current_schema_for_display}). Agent setup will proceed.")

    # Setup the Agno Agent instance
    agent_instance = setup_sql_agent(
        db_conn_info=DB_CONN_INFO,
        openai_api_key=OPENAI_API_KEY
    )

    if not agent_instance:
        logging.critical("Failed to setup Agno Agent. Check previous logs for errors. Exiting.")
        exit(1)

    # --- Interaction Loop ---
    print("\n--- Agno SQL Agent Ready ---")
    print("Enter query ('schema' to view, 'quit' to exit).")
    while True:
        try:
            user_input = input("> ").strip()
            if user_input.lower() == 'quit': break
            elif user_input.lower() == 'schema':
                 print("\n--- Database Schema (employees, departments) ---")
                 print(current_schema_for_display if "failed" not in current_schema_for_display else "Schema could not be retrieved for display.")
                 print("----------------------------------------------\n")
            elif user_input:
                logging.info(f"Running Agent with input: '{user_input}'")
                result = agent_instance.run(user_input)
                display_final_result(result)
            else: pass
        except KeyboardInterrupt: break
        except AttributeError as e:
             logging.error(f"AttributeError: Agent might not accept the toolkit directly. Error: {e}", exc_info=True)
             print(f"\nError: Could not execute agent. Check if '{type(agent_instance).__name__}' needs individual tools instead of the toolkit, or uses a different method like '.chat()'.\n")
        except Exception as e:
             logging.error(f"Error in main loop: {e}", exc_info=True)
             print("\nAn unexpected error occurred. Check logs.\n")

    logging.info("SQL Agent execution finished.")
