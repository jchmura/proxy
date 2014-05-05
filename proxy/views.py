from django.shortcuts import render, redirect
from django.template import RequestContext
from django.http import HttpResponse
from lxml import html
import requests
from proxy.forms import URLForm


def download_page(url):
    r = requests.get(url)
    contents = r.headers['content-type'].split(';')
    content = contents[0]
    if content.startswith('image'):
        page = r
    else:
        page = r.text
    return page, content


def get_title(doc):
    title = doc.find('.//title')
    if title is not None:
        return title.text


def rewrite_link(link):
    link = link.replace('&', '%26')
    if link.startswith('javascript'):
        return link
    return '/?q=' + link


def replace_links(doc, url):
    doc.make_links_absolute(url)
    doc.rewrite_links(rewrite_link)
    return doc


def get_head(doc):
    head = html.tostring(doc.head)
    head = head.decode('utf-8')
    body_list = head.split('\n')[1:-1]
    head = '\n'.join(body_list)
    return head


def get_body(doc):
    body = html.tostring(doc.body)
    body = body.decode('utf-8')
    body_list = body.split('\n')[1:-1]
    body = '\n'.join(body_list)
    return body


def check_url(url):
    if not url:
        return
    if url[:7] != 'http://' and url[:8] != 'https://':
        return 'http://' + url
    else:
        return url


def home(request):
    if request.method == 'POST':
        form = URLForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']
            return redirect('/?q=' + url)
    else:
        url = request.GET.get('q')
        url = check_url(url)
        if url:
            page, content = download_page(url)
            if content == 'text/html':
                form = URLForm()
                doc = html.document_fromstring(page)
                title = get_title(doc)
                doc = replace_links(doc, url)
                head = get_head(doc)
                body = get_body(doc)
                context = {'form': form, 'head': head, 'body': body, 'title': title}
                return render(request, 'page.html', context, context_instance=RequestContext(request))
            else:
                return HttpResponse(page, content_type=content)
        else:
            form = URLForm()
            return render(request, 'home.html', {'form': form}, context_instance=RequestContext(request))
