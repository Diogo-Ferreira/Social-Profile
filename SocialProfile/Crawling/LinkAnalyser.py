from tld import get_tld

from SocialProfile.TagMiners.MappingValues import LINK_TO_MCARS


class LinkAnalyser:

    @staticmethod
    def analyse_link(link):
        """
        Check if given link means something to mCars values
        :param link:
        :return:
        """
        domain = LinkAnalyser.extract_domain(link)

        out = {
            "domain": domain
        }

        if domain in LINK_TO_MCARS:
            out["likeli_tag"] = LINK_TO_MCARS[domain]
        else:
            out["not_in_mcars"] = True

        return out
    
    @staticmethod
    def extract_domain(link):
        return get_tld(link, as_object=True).domain
