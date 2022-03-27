

class GitRepo:

    def __init__(self, url, stars):
        self.url = url
        self.stars = stars

    def __eq__(self, other):
        if isinstance(other, GitRepo):
            return self.url == other.url
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.url)

    def __str__(self):
        return self.url + "," + str(self.stars)

