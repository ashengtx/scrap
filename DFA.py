import re
from pprint import pprint

class DFAFilter():

    '''Filter Messages from keywords
    Use DFA to keep algorithm perform constantly
    >>> f = DFAFilter()
    >>> f.add("sexy")
    >>> f.match("hello sexy baby")
    sexy
    '''

    def __init__(self, words):
        self.keyword_chains = {}
        self.delimit = '\x00'
        self._build(words)

    def _build(self, words):
        for w in words:
            self.add(w.strip())

    def add(self, keyword):
        keyword = keyword.lower()
        chars = keyword.strip()
        if not chars:
            return
        level = self.keyword_chains
        for i in range(len(chars)):
            if chars[i] in level:
                level = level[chars[i]]
            else:
                if not isinstance(level, dict):
                    break
                for j in range(i, len(chars)):
                    level[chars[j]] = {}
                    last_level, last_char = level, chars[j]
                    level = level[chars[j]]
                last_level[last_char] = {self.delimit: 0}
                break
        if i == len(chars) - 1:
            level[self.delimit] = 0

    def match(self, text):
        """
        return match word list
        :param text: string
        :return: words: list
        """
        text = text.lower()
        words = []
        start = 0
        while start < len(text):
            print('start', start)
            level = self.keyword_chains
            match_word = []
            for char in text[start:]:
                print(char)
                pprint(level)
                if char in level:
                    if self.delimit not in level[char]:
                        level = level[char]
                        match_word.append(char)
                    else:
                        match_word.append(char)
                        print('word: ', ''.join(match_word))
                        words.append(''.join(match_word))
                        if len(level[char]) == 1: # 只有终止符就说明没有更长的词了，前进一位
                            break
                        else:
                            level = level[char]
                else: # 没匹配到字，前进一位
                    break
            start += 1
        return list(set(words))

def test_DFA():
    category = ['口红','化妆品','香水','曲奇','曲奇饼干','饼干','香水瓶子']
    dfa = DFAFilter(category)
    pprint(dfa.keyword_chains)
    text = "好吃的超曲奇饼干啊啊啊啊啊香水有毒香水瓶子真好看"
    print(dfa.match(text))


if __name__ == "__main__":
    test_DFA()