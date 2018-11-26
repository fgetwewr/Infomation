import requests
import json

headers = {
# 'referer': 'https://www.toutiao.com/search/?keyword=%E6%B5%B7%E5%BA%95%E6%8D%9E',
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36',
}
base_url = 'https://www.toutiao.com/search_content/?offset={}&format=json&keyword=海底捞&autoload=true&count=20&cur_tab=1&from=search_tab'

offset = 0
print('UUUUUUUUUUUUUUUUUU')
print(requests.get(url='https://www.toutiao.com/a6626602421458043396/', headers=headers).text)
for x in range(1):
    url = base_url.format(offset)
    offset += 20
    response = requests.get(url=url, headers=headers)
    # print(response.status_code)
    res = response.json()
    # print(response.json())
    items = res.get('data')
    # print(items)
    for item in items:
        print(item)
        print('-----------------------')
        link = item.get('article_url')
        print(item.get('title'))        # 标题
        print(item.get('media_name'))       # 媒体名
        print(link)      # 头条链接
        print(item.get('datetime'))     # 发布时间
        print(item.get('large_image_url'))      # 图片地址
        print(item.get('comment_count'))        # 评论数量
        print(item.get('has_video'))        # 是否是视频
        print(item.get('has_image'))        # 是否有图片
        if link:

            link = link.replace('group/', 'group/a')
            print('link: ', link)
            details = requests.get(url=link)
            print(details.text)
            print('IIIIIIIIIIIIIIIIIIIIIIi')
            # print(requests.get('https://www.toutiao.com/6626602421458043396/').text)
            with open('toutiao.html', 'w', encoding='utf-8') as f:
                f.write(requests.get('https://www.toutiao.com/a6626602421458043396/', headers=headers).text)
            # print('********************')
