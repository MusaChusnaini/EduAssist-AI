from ai_logic import call_me, generate_answer, initialize_client

prompt:str = ""

if __name__ == "__main__":
    initialize_client()
    while True:
        print("Masukkan Prompt ", end=": ")
        prompt = input()
        if prompt == "/end":
            print("Talk ended. Thank You!")
            break
        print(generate_answer(prompt),"\n")