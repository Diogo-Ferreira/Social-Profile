import re

class FilteringTools:
    """
    This class contains methods to help clean texts from smileys, links, emojis...
    """

    @staticmethod
    def full_cleaning(text):
        text = FilteringTools.remove_simple_smileys(text)
        text = FilteringTools.remove_emoji(text)
        text = FilteringTools.remove_links(text)
        return text


    @staticmethod
    def remove_simple_smileys(text):
        pattern = r'(\:\w+\:|\<[\/\\]?3|[\(\)\\\D|\*\$][\-\^]?[\:\;\=]|[\:\;\=B8][\-\^]?[3DOPp\@\$\*\\\)\(\/\|])(?=\s|[\!\.\?]|$)'
        return re.sub(pattern,'',text)


    @staticmethod
    def remove_links(text):
        return re.sub(r'http\S+', '', text, flags=re.MULTILINE)


    @staticmethod
    def remove_emoji(data):
        """
        :param data:
        :return:
        """
        if not data:
            return data
        if not isinstance(data, str):
            return data
        try:
            # UCS-4
            patt = re.compile(u'([\U00002600-\U000027BF])|([\U0001f300-\U0001f64F])|([\U0001f680-\U0001f6FF])')
        except re.error:
            # UCS-2
            patt = re.compile(u'([\u2600-\u27BF])|([\uD83C][\uDF00-\uDFFF])|([\uD83D][\uDC00-\uDE4F])|([\uD83D][\uDE80-\uDEFF])')
        return patt.sub('', data)


