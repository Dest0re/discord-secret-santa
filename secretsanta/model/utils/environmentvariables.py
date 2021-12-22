import os


class EnvironmentVariables:
    def __init__(self, *args: str):
        
        for name in args:
            var = os.getenv(name)

            if var == None:
                raise KeyError(f'Missing important variable named {name}')

            setattr(self, name, var)
            

if __name__ == '__main__':
    print(EnvironmentVariables('DATABASE_PORT').DATABASE_PORT)
