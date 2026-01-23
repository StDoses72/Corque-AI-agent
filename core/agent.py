from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from config.settings import settings
from tools import getWeather, sendEmail, getEmail, addTodo, getUTCNow, getTodoListinDaysFromNow, convertUTCEpochToISO, convertUTCToLocal, deleteTodo, getMostRecentTodo, changeTodoStatus
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.types import Command
import time

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

        When writing emails or messages that will be sent using tools:
        - Do not include a signature, closing, or sender name. The system will add it automatically.

        When multiple tools could be used:
        - You may use them in parallel if appropriate.
        - Ensure the final response is clean, natural, and user-facing only.
        Once you deliver the requested output, stop. Do not continue with extra suggestions unless asked.
        '''
        self.tools = [
            getWeather,
            sendEmail,
            getEmail,
            addTodo,
            getUTCNow,
            getTodoListinDaysFromNow,
            convertUTCEpochToISO,
            convertUTCToLocal,
            deleteTodo,
            getMostRecentTodo,
            changeTodoStatus
        ]
        self.model = ChatOllama(
            model=settings.modelName,
            temperature=0.2,
            stream=True
        )
        self.agent = create_agent(self.model, tools=self.tools, checkpointer=InMemorySaver(), system_prompt=self.systemPrompt,
        middleware=[HumanInTheLoopMiddleware(
            interrupt_on={'sendEmail':True},
            description_prefix="Tool execution pending approval"
        )])
        
    def ask(self,query: str,threadId = 1):
        startTime = time.time()
        config = {'configurable': {'thread_id': f'{threadId}'}}
        response = self.agent.invoke({'messages':[{'role':'user','content':query}]},config=config)
        endTime = time.time()
        print(f"Time taken: {endTime - startTime} seconds")
        if '__interrupt__' in response:
            print('Agent action is interrupted, needs human action to continue.')
            print('The reason is:')
            intr = response['__interrupt__']
            #print(intr) For debugging
            interrupt = intr[0]
            value = interrupt.value
            toolName = value['action_requests'][0]['name']
            if toolName == 'sendEmail':
                print('The agent is trying to send an email, please review the email content and decide if it is correct.'+'\n')
                print('The recipient email is:')
                print(value['action_requests'][0]['args']['recipientEmail']+'\n')
                print('The subject is:')
                print(value['action_requests'][0]['args']['subject']+'\n')
                print('The body is:')
                print(value['action_requests'][0]['args']['body']+'\n')
                decision = input('Decision: approve, edit, or reject? (a/e/r): ')
                if decision == 'a':
                    result2 = self.agent.invoke(Command(resume={'decisions':[{'type':'approve'}]}),config=config)
                    return result2["messages"][-1].content
                elif decision == 'e':
                    newRecipientEmail = value['action_requests'][0]['args']['recipientEmail']
                    newSubject = value['action_requests'][0]['args']['subject']
                    newBody = value['action_requests'][0]['args']['body']
                    while True:
                        print("\nCurrent draft:")
                        print(f"  To: {newRecipientEmail}")
                        print(f"  Subject: {newSubject}")
                        print("  Body:")
                        print(newBody)
                        print("----------------------------------")
                        editionChoice = input("Edit: recipientEmail(r), subject(s), body(b).Press view(v), done(d), cancel(c) for command: ").strip().lower()
                        if editionChoice == 'r':
                            newRecipientEmail = input('New recipient email: ')
                        elif editionChoice == 's':
                            newSubject = input('New subject: ')
                        elif editionChoice == 'b':
                            print("New body(finish with END):")
                            lines = []
                            while True:
                                line = input()
                                if line.strip().lower() == 'end':
                                    break
                                lines.append(line)
                            if lines:
                                newBody = '\n'.join(lines)
                        elif editionChoice == 'v':
                            continue
                        elif editionChoice == 'd':
                            break
                        elif editionChoice == 'c':
                            print("Email editing cancelled.")
                            return 'Email editing cancelled.'
                        else:
                            print("Invalid command. Please try again.")
                            continue

                    result2 = self.agent.invoke(
                    Command(
                        # Decisions are provided as a list, one per action under review.
                        # The order of decisions must match the order of actions
                        # listed in the `__interrupt__` request.
                        resume={
                            "decisions": [
                                {
                                    "type": "edit",
                                    # Edited action with tool name and args
                                    "edited_action": {
                                        # Tool name to call.
                                        # Will usually be the same as the original action.
                                        "name": "sendEmail",
                                        # Arguments to pass to the tool.
                                        "args": {"recipientEmail": newRecipientEmail, "subject": newSubject, "body": newBody},
                                    }
                                }
                            ]
                        }
                    ),
                    config=config  # Same thread ID to resume the paused conversation
                )
                    return result2["messages"][-1].content
                elif decision == 'r':
                    result2 = self.agent.invoke(Command(resume={'decisions':[{'type':'reject'}]}),config=config)
                    print('The attempt to send the email is rejected.'+'\n')
                    return result2["messages"][-1].content
        return response["messages"][-1].content