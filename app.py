import os

def main():
    print("Hello World! runs on Actions")
    
    for i in [1,2,3,4,5]:
        print("♞ " * i)
    name = os.getenv("USERNAME")
    print(f"Hola { name }")

if __name__ == "__main__":
    main()