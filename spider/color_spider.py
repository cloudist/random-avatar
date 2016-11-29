import urllib
import urllib2


def main():
    url = 'http://colorhunt.co/get.php'
    page_limit = 32
    output_filename = 'raw.data'

    res = []

    for page in range(page_limit):
        print 'page:', page
        values = {'step' : page, 'sort' : 'new'}
        data = urllib.urlencode(values)
        req = urllib2.Request(url, data)
        response = urllib2.urlopen(req)
        the_page = response.read()
        print 'size:', len(the_page)
        res.append(the_page)

    print '>>', output_filename
    with open(output_filename, 'w') as f:
        for line in res:
            f.write(line)
            f.write('\n')
    

if __name__ == '__main__':
    main()
