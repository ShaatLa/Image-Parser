import re
import requests
from requests_html import HTMLSession
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata

URL = 'https://images.nasa.gov/'


def from_url(url, img_name, func):
        response = requests.get(url)

        if response:
            with open(f'nasa/{img_name}.jpg', 'wb') as file:
                file.write(response.content)
                print(f'Url saved as {img_name}.jpg')

            with open(f'nasa/{img_name}.txt', 'w') as text_file:
                if func:
                    for line in func:
                        text_file.write(line + '\n')
                else:
                    text_file.write('No data.\n')

                parser = createParser(f'nasa/{img_name}.jpg')
                metadata = extractMetadata(parser)
                if metadata:
                    for line in metadata.exportPlaintext():
                        text_file.write('\n' + line)
        else:
            print(f'No {img_name}-medium image.')


def description(url, session):
    description = []

    page = session.get(url)
    page.html.render(sleep=3)

    shrt_desc = page.html.find('ul#detail-metadata')
    desc = page.html.find('#editDescription', first=True)

    for i in shrt_desc:
        if i:
            description.append(i.text)

    if description:
        description.append(desc.text)

    return description


if __name__ == '__main__':
    session = HTMLSession()
    page = session.get(URL)

    page.html.render(sleep=3)

    divs = page.html.find('img')

    image_hrefs = []

    for href in divs:
        img_href = re.search(r'(?<=https://images-assets\.nasa\.gov/image/)([\w_ -]+)(?=.+)', href.html)
        try:
            image_hrefs.append(img_href.group())
        except AttributeError:
            pass

    print(f'Found {len(image_hrefs)} images. Parsing...')

    for url in image_hrefs:
        from_url(f'https://images-assets.nasa.gov/image/{url}/{url}~medium.jpg',
                 url,
                 description(f'https://images.nasa.gov/details-{url}.html', session))