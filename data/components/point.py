

class Point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __iadd__(self, other):
        return self.x + other[0], self.y + other[1]
        
if __name__ == "__main__":      
    point = Point(50, 50)
    print point
    print point
    point += (10, -5)

    print point

    point += (10, 5)
    print point