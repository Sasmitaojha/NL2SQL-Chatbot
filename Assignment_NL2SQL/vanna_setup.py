import os
import re
from vanna import Agent, AgentConfig
from vanna.core.registry import ToolRegistry
from vanna.core.user import UserResolver, User, RequestContext
from vanna.tools import RunSqlTool, VisualizeDataTool
from vanna.tools.agent_memory import SaveQuestionToolArgsTool, SearchSavedCorrectToolUsesTool
from vanna.integrations.sqlite import SqliteRunner
from vanna.integrations.local.agent_memory import DemoAgentMemory
from vanna.integrations.google import GeminiLlmService
from dotenv import load_dotenv

load_dotenv()

class SimpleUserResolver(UserResolver):
    def resolve_user(self, request_context: RequestContext) -> User | None:
        return User(id="default_user")

class ValidatedRunSqlTool(RunSqlTool):
    async def run(self, sql: str, **kwargs):
        sql_upper = sql.upper().strip()
        
        if not sql_upper.startswith("SELECT"):
            raise ValueError("Validation failed: Only SELECT queries are allowed.")
            
        dangerous_keywords = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "EXEC", 
                              "XP_", "SP_", "GRANT", "REVOKE", "SHUTDOWN"]
        
        for word in dangerous_keywords:
            if re.search(rf'\b{word}\b', sql_upper):
                raise ValueError(f"Validation failed: Dangerous keyword detected: {word}")
                
        if "SQLITE_MASTER" in sql_upper or "SQLITE_" in sql_upper:
            raise ValueError("Validation failed: Queries accessing system tables are not allowed.")
            
        return await super().run(sql=sql, **kwargs)

def get_vanna_agent():
    api_key = os.environ.get("GOOGLE_API_KEY", "dummy_if_not_present")
    
    # We use gemini-2.5-flash per requirement Option A
    # Some older installations might complain about model names but gemini-2.5-flash is required text.
    llm_service = GeminiLlmService(api_key=api_key, model="gemini-2.5-flash")

    agent_memory = DemoAgentMemory()

    db_runner = SqliteRunner(database_path='clinic.db')

    tool_registry = ToolRegistry()
    
    # We register our Validated tool but fallback to normal RunSql if we aren't bypassing
    tool_registry.register_local_tool(ValidatedRunSqlTool(sql_runner=db_runner), access_groups=["*"])
    tool_registry.register_local_tool(VisualizeDataTool(), access_groups=["*"])
    tool_registry.register_local_tool(SaveQuestionToolArgsTool(), access_groups=["*"])
    tool_registry.register_local_tool(SearchSavedCorrectToolUsesTool(), access_groups=["*"])

    config = AgentConfig(
        agent_name="ClinicNL2SQL",
        description="NL2SQL agent for clinic database",
        debug=True,
    )

    agent = Agent(
        config=config,
        llm_service=llm_service,
        tool_registry=tool_registry,
        agent_memory=agent_memory,
        user_resolver=SimpleUserResolver()
    )
    agent.sqldb_runner = db_runner
    
    return agent

agent = get_vanna_agent()
