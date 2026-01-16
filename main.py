from core.agent import Agent
from tools.todoListTools import initTodoList
import time
def main():
    initTodoList()
    Corque = Agent()
    print('Corque is ready to assist you! Type quit to exit.')
    while True:
        userInput = input('User: ')
        if userInput.lower() == 'quit':
            break
        startTime = time.time()
        response = Corque.ask(userInput)
        endTime = time.time()
        print(f"Time taken: {endTime - startTime} seconds")
        print('Corque: ', response)

if __name__ == '__main__':
    main()