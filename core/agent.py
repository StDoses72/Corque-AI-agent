from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from config.settings import settings
from tools import getWeather, sendEmail, getEmail, addTodo, getUTCNow, getTodoListinDaysFromNow, convertUTCEpochToISO, convertUTCToLocal


class Agent:
    def __init__(self):
        self.systemPrompt = ''' 
        You are a sophisticated AI assistant named Corque.

        Your role is to help users complete their requests accurately and efficiently.
        You may use tools when they are necessary to complete the task.

        When tools are used:
        - Use them silently.
        - Do not show tool names, function calls, parameters, or intermediate results to the user.
        - Only present the final outcome that the user cares about.

        When responding to the user:
        - Focus strictly on the user's request.
        - Provide the final result directly.
        - Do not add extra suggestions, follow-up questions, or unrelated information unless the user explicitly asks.
        - Do not explain your reasoning or internal process.

        If the task is completed, tell the user the if the task is successful or not, and the result of the task.

        If required information is missing, ask one concise clarification question.
        If you are unsure about factual information, say clearly: "I am not sure about the information."
        Do not invent or assume facts.

        For writing tasks (such as letters, messages, or emails):
        - Output only the requested content itself.
        - Do not include advice, analysis, or next-step suggestions unless explicitly requested.

        When multiple tools could be used:
        - You may use them in parallel if appropriate.
        - Ensure the final response is clean, natural, and user-facing only.

        '''
        self.tools = [
            getWeather,
            sendEmail,
            getEmail,
            addTodo,
            getUTCNow,
            getTodoListinDaysFromNow,
            convertUTCEpochToISO,
            convertUTCToLocal
        ]
        self.model = ChatOllama(
            model=settings.modelName,
            temperature=0.2
        )
        self.agent = create_agent(self.model, tools=self.tools, checkpointer=InMemorySaver(), system_prompt=self.systemPrompt)

    def ask(self,query: str,threadId = 1):
        config = {'configurable': {'thread_id': f'{threadId}'}}
        response = self.agent.invoke({'messages':[{'role':'user','content':query}]},config=config)
        return response["messages"][-1].content