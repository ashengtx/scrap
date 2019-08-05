import re

class DFAFilter():

    '''Filter Messages from keywords
    Use DFA to keep algorithm perform constantly
    >>> f = DFAFilter()
    >>> f.add("sexy")
    >>> f.filter("hello sexy baby")
    hello **** baby
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

    def detect(self, message):
        """
        only return the first censored word
        :param message:
        :return: word: string
        """
        message = message.lower()
        ret = []
        start = 0
        while start < len(message):
            level = self.keyword_chains
            for char in message[start:]:
                if char in level:
                    if self.delimit not in level[char]:
                        level = level[char]
                        ret.append(char)
                    else:
                        ret.append(char)
                        return ''.join(ret)
                else:
                    break
            start += 1
        return None

    def filter(self, message, repl="*", preserve_punctuation=True):
        message = message.lower()
        ret = []
        start = 0
        while start < len(message):
            level = self.keyword_chains
            step_ins = 0
            for char in message[start:]:
                if preserve_punctuation:
                    # 匹配到符号
                    if re.match(r'[^\w]|_', char):
                        # 不在敏感词内部，则保留，并停止遍历
                        if step_ins == 0:
                            ret.append(char)
                            break
                        else:  # 在敏感词内部，则忽略，继续遍历
                            step_ins += 1
                            continue
                if char in level:
                    step_ins += 1
                    if self.delimit not in level[char]:
                        level = level[char]
                    else:
                        ret.append(repl * step_ins)
                        start += step_ins - 1
                        break
                else:
                    ret.append(message[start])
                    break
            else:
                ret.append(message[start])
            start += 1

        return ''.join(ret)