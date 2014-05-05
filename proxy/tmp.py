import requests
from lxml import html


def rewrite_link(link):
    if link.startswith('javascript'):
        return link
    return 'http://proxy.jakubchmura.pl/?q=' + link

url = 'http://suchary.jakubchmura.pl'
r = requests.get(url)

doc = html.document_fromstring(r.text)
doc.make_links_absolute(url)
doc.rewrite_links(rewrite_link)
head = doc.head
# print(html.tostring(doc, True))
head = html.tostring(head)
head = str(head)[1:10]
print(head)