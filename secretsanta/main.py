from model import PCPerformance


if __name__ == '__main__':
    print(tuple(PCPerformance.select().execute()))
