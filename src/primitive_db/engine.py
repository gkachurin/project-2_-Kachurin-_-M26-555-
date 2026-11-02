def welcome():
    print("Первая попытка запустить проект!")
    print()
    print("***")

    while True:
        print("<command> exit - выйти из программы")
        print("<command> help - справочная информация")

        command = input("Введите команду: ").strip().lower()

        if command == "exit":
            break

        elif command == "help":
            continue

        else:
            print("Неизвестная команда")