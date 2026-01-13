from core.agent import Agent
from tools.todoList import initTodoList
def main():
    initTodoList()
    Corque = Agent()
    print('Corque is ready to assist you! Type quit to exit.')
    while True:
        userInput = input('User: ')
        if userInput.lower() == 'quit':
            break
        response = Corque.ask(userInput)
        print('Corque: ', response)

if __name__ == '__main__':
    main()