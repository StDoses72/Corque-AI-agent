from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from config.settings import settings
from tools import getWeather, sendEmail, getEmail, addTodo, getUTCNow, getTodoListinDaysFromNow, convertUTCEpochToISO, convertUTCToLocal


class Agent:
    def __init__(self):
        self.systemPrompt = ''' 
        You are a sophisticated AI Assistant. Your name is Corque. 
        You are able to use tools to help users get information. You must use the tools when necessary.
        Do remember to do parallel function calls when needed.
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
            temperature=0
        )
        self.agent = create_agent(self.model, tools=self.tools, checkpointer=InMemorySaver(), system_prompt=self.systemPrompt)

    def ask(self,query: str,threadId = 1):
        config = {'configurable': {'thread_id': f'{threadId}'}}
        response = self.agent.invoke({'messages':[{'role':'user','content':query}]},config=config)
        return response["messages"][-1].content