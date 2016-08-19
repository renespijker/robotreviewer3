"""
formatting.py
functions for displaying RobotReviewer internal data in useful ways
"""

from robotreviewer.app import app
import logging
from collections import defaultdict

log = logging.getLogger(__name__)


def format_authors(author_list, max_authors=1):
    et_al = False
    if len(author_list) > max_authors:
        et_al = True
        author_list = author_list[:max_authors]
    authors = u", ".join([u"{lastname} {initials}".format(**a) for a in author_list])
    if et_al:
        authors += " et al"
    return authors

@app.context_processor
def short_citation_fn():
    def short_citation(article):
        try:
            return u"{} {}, {}".format(article['authors'][0]['lastname'], article['authors'][0]['initials'], article.get('year', '[unknown year]'))
        except Exception as e:
            log.debug("Fallback: {} raised".format(e))
            return article['filename']
    return dict(short_citation=short_citation)

@app.context_processor
def long_citation_fn():
    def long_citation(article):
        try:
            bracket_issue = u"({})".format(article['issue']) if article.get('issue') else u""
            return u"{}. {} {} {}. {}{}; {}".format(format_authors(article['authors']), article['title'], article.get('journal_abbr', article['journal']), article.get('year', '[unknown year]'), article.get('volume', '?'), bracket_issue, article.get('pages', '?'))
        except Exception as e:
            log.debug("Fallback: {} raised".format(e))
            return u"Unable to extract citation information for file {}".format(article['filename'])
    return dict(long_citation=long_citation)

@app.context_processor
def registry_ids_fn():
    def registry_ids(article):
        return article.get("registry", [])
    return dict(registry_ids=registry_ids)

@app.context_processor
def group_by_reg_ids_fn():
    def group_by_reg_ids(articles):
        regid_to_i = {}
        fn_to_i = {}

        i = 0

        for article_i, article in enumerate(articles):
            reg_ids = article.get('registry')
            if not reg_ids:
                # give the article it's own id and move on
                i += 1
                fn_to_i[article_i] = i
                i += 1
                continue
            
            for regid in article['registry']:
                i += 1        
                fn_encountered = fn_to_i.get(article_i)
                regid_encountered = regid_to_i.get(regid)
                        
                regid_to_i[regid] = i
                fn_to_i[article_i] = i
                
                # map all previously encountered to the new index
                fn_to_i = {k: i if (v==fn_encountered or v==regid_encountered) else v for k, v in fn_to_i.items()}
                regid_to_i = {k: i if (v==fn_encountered or v==regid_encountered)  else v for k, v in regid_to_i.items()}


        # now parse out the results
        i_s = set(fn_to_i.values()) # could equally do the regids

        i_to_fn = defaultdict(list)
        for pmid, i in fn_to_i.items():
            i_to_fn[i].append(pmid)

        i_to_regid = defaultdict(list)
        for regid, i in regid_to_i.items():
            i_to_regid[i].append(regid)

        out = []
        for trial_num, i in enumerate(i_s):
            out.append((i_to_regid[i], i_to_fn[i]))
        return out
    return dict(group_by_reg_ids=group_by_reg_ids)

            

    




