from lxml.html import fromstring, tostring
from lxml import etree
from bs4 import BeautifulSoup
from bs4 import NavigableString, Comment, Tag
import requests
import json


def gong_lve_parser():
    """
    攻略页面的解析
    :return:
    """
    try:
        url = 'https://www.mafengwo.cn/gonglve/'
        headers = {
            'Host': 'www.mafengwo.cn',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'pragma': 'no-cache',
            'Upgrade - Insecure - Requests': '1',
            'referer': 'https://www.mafengwo.cn/mdd/'
        }
        req = requests.get(url, headers=headers)
        req.raise_for_status()
        html = req.text.replace('\n', '')
        selector = fromstring(html)
        result = []
        # 头部解析(左侧的列表)
        nav_list = []
        nav_item = selector.xpath('//div[@class="nav-item"]')
        # 遍历每个div nav-item标签
        for item in nav_item:
            # 得到列表的标题
            li_title = item.xpath('div[@class="nav-title"]/h3/text()')[0]
            li_list = []
            nav_li = item.xpath('div[@class="nav-panel rank-panel"]/ol/li')
            # 如果是主题推荐这个div
            if len(nav_li) == 0:
                nav_dl = item.xpath('div[@class="nav-panel category-panel"]/dl')
                # 遍历主题推荐的dl
                for dl in nav_dl:
                    # 得到小标题
                    dt = dl.xpath('dt/text()')[0]
                    dd = dl.xpath('dd/a')
                    dd_a_list = []
                    # 得到小标题的每项  text 和 href
                    for a in dd:
                        a_text = a.attrib['title']
                        a_href = a.attrib['href']
                        dd_a_list.append({'place': a_text, 'place_url': 'https://www.mafengwo.cn' + a_href})
                    li_list.append({'topic': dt, 'places': dd_a_list})
            # 如果不是主题推荐这个div
            else:
                # 得到每个标题的详细内容
                for li in nav_li:
                    li_strong = li.xpath('strong/a/text()')[0]
                    li_text = li.xpath('a/text()')[0]
                    place_url = li.xpath('a/@href')[0]
                    li_list.append(
                        {'title': li_strong, 'desc': li_text, 'place_url': 'https://www.mafengwo.cn' + place_url})
            nav_list.append({'title': li_title, 'content': li_list})
        result.append({'nav': nav_list})
        # 头部解析 (右侧的图片)
        li_slide = selector.xpath('//div[@class="slide"]/ul[@id="slide_box"]/li')
        nav_img = []
        for li in li_slide:
            nav_img.append(
                {'src': li.xpath('a/img/@src')[0], 'href': 'https://www.mafengwo.cn' + li.xpath('a/@href')[0]})
        result.append({'img': nav_img})
        # 默认是显示10篇   数据来源有三种对应不同的解析
        # 正文部分解析
        gonglve_feed_list = []
        gonglve_feed = selector.xpath('//div[@class="_j_feed_data"]/div[@class="feed-item _j_feed_item"]')
        gonglve_id = 1
        # 遍历每个div
        for fee in gonglve_feed:
            # 得到fee的类型  1 2是游记和问答  3是自由行攻略
            fee_type = fee.attrib['data-type']
            if fee_type == '1' or fee_type == '2' or fee_type == '3':
                gonglve_feed_list.append(fee_parser(fee, fee_type, gonglve_id))
                gonglve_id = gonglve_id + 1
        result.append({'content': gonglve_feed_list})
        # result.append({'content': ''})
        return result
    except Exception as e:
        print(e)


def fee_parser(fee, fee_type, gonglve_id):
    """
    攻略中部内容的解析
    :param fee: element标签
    :param fee_type: div的类型
    :return:
    """
    gonglve_url = ''  # 攻略的跳转url
    from_pinyin = ''  # 攻略类型的拼音 比如 youji
    from_hanzi = ''  # 攻略类型的汉子 比如问答
    num_zan = ''  # 右上角获赞数
    title = ''  # 攻略的标题
    img_url1 = ''  # 攻略内容的图片
    img_url2 = ''  # 攻略内容的图片
    img_url3 = ''  # 攻略内容的图片
    abstract = ''  # 攻略内容的摘要
    user_img = ''  # 用户的图片地址  默认值为空
    user_name = ''  # 用户的姓名
    num_liulan = ''  # 浏览数
    num_pinglun = ''  # 评论数目
    if fee_type != '3':
        # 跳转链接
        gonglve_url = fee.xpath('a/@href')[0]
        if fee_type == '1':
            from_pinyin = 'youji'
            from_hanzi = '游记'
        else:
            from_pinyin = 'wenda'
            from_hanzi = '问答'
        # 几个蜜蜂体验过
        num_zan = fee.xpath('a/div[@class="bar clearfix"]/span[@class="stat"]/span[@class="num"]/text()')[0]
        # 标题
        title = fee.xpath('a/div[@class="title"]/text()')
        title = '' if len(title) == 0 else title[0].replace(' ', '')
        # 图片
        img_url1 = fee.xpath('a/dl[@class="art clearfix"]/dt/img/@src')
        img_url1 = '' if len(img_url1) == 0 else img_url1[0]
        img_url2 = img_url1
        img_url3 = img_url1
        # 摘要
        abstract = fee.xpath('a/dl[@class="art clearfix"]/dd/div[@class="info"]/text()')
        abstract = '' if len(abstract) == 0 else abstract[0].replace(' ', '')
        # 用户的头像
        user_img = fee.xpath('a/dl[@class="art clearfix"]/dd/div[@class="ext-r"]/span[@class="author"]/img/@src')
        user_img = '' if len(user_img) == 0 else user_img[0]
        # 用户的姓名
        user_name = fee.xpath('a/dl[@class="art clearfix"]/dd/div[@class="ext-r"]/span[@class="author"]/text()')
        user_name = '' if len(user_name) == 0 else user_name[0]
        # 浏览数和评论数
        item_see = fee.xpath('a/dl[@class="art clearfix"]/dd/div[@class="ext-r"]/span[@class="nums"]/text()')
        item_see = '' if len(item_see) == 0 else item_see[0]
        if item_see != '':
            item_see_list = item_see.split(',')
            if len(item_see_list) == 2:
                num_liulan = item_see_list[0]
                num_pinglun = item_see_list[1]
            else:
                num_liulan = item_see_list[0]
                num_pinglun = ''
        else:
            num_liulan = ''
            num_pinglun = ''
    else:
        gonglve_url = fee.xpath('a/@href')[0]
        from_pinyin = 'ziyouxinggonglve'
        from_hanzi = '自由行攻略'
        # 有几个峰峰体验过
        num_zan = fee.xpath('a/div[@class="bar clearfix"]/span[@class="stat"]/span[@class="num"]/text()')[0]
        # 标题
        title = fee.xpath('a/div[@class="title"]/text()')
        title = '' if len(title) == 0 else title[0].replace(' ', '')
        # 摘要
        abstract = fee.xpath('a/div[@class="txt"]/div[@class="info"]/text()')
        abstract = '' if len(abstract) == 0 else abstract[0].replace(' ', '')
        # 图片
        item_img = fee.xpath('a/div[@class="imgs"]/ul/li/img/@src')
        if len(item_img) == 3:
            img_url1 = item_img[0]
            img_url2 = item_img[1]
            img_url3 = item_img[2]
        elif len(item_img) == 2:
            img_url1 = item_img[0]
            img_url2 = item_img[1]
            img_url3 = img_url1
        elif len(item_img) == 1:
            img_url1 = item_img[0]
            img_url2 = img_url1
            img_url3 = img_url1
        else:
            img_url1 = ''
            img_url2 = ''
            img_url3 = ''
        # 评论和浏览
        num_liulan = fee.xpath('a/div[@class="imgs"]/ul/li[@class="ext-r"]/text()')
        num_liulan = '' if len(num_liulan) == 0 else num_liulan[0]
        num_pinglun = ''
    return {'id': str(gonglve_id), 'gonglve_url': gonglve_url, 'from_pinyin': from_pinyin, 'from_hanzi': from_hanzi,
            'num_zan': num_zan,
            'title': title,
            'img_url1': img_url1, 'img_url2': img_url2, 'img_url3': img_url3, 'abstract': abstract,
            'user_img': user_img, 'user_name': user_name, 'num_liulan': num_liulan, 'num_pinglun': num_pinglun}


def destination_parser():
    """
    目的地页面的解析
    :return:
    """
    try:
        url = 'https://www.mafengwo.cn/mdd/'
        headers = {
            'Host': 'www.mafengwo.cn',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Upgrade - Insecure - Requests': '1',
            'referer': 'https://www.mafengwo.cn/'
        }
        req = requests.get(url, headers=headers)
        req.raise_for_status()
        req.encoding = req.apparent_encoding
        html = req.text.replace('\n', '')
        selector = etree.HTML(html)
        # result 第一个元素为头图信息
        # 第二个元素为热门目的地信息
        # 第三个元素为当季推荐
        result = []
        # 头图的解析部分
        # 标题
        head_title = selector.xpath('//div[@class="show-name"]/a/h2/text()')[0]
        # 文字
        head_p = selector.xpath('//p[@class="location"]/text()')[0]
        # 图片地址
        img_src = selector.xpath('//a[@class="bigimg"]/img/@src')[0]
        # 输入框下面的五个
        place_hot = []
        input_a = selector.xpath('//div[@class="place-search-hot"]/a')
        mdd_hot_url = 'http://www.mafengwo.cn/ajax/router.php?sAct=KMdd_StructWebAjax|GetSearchHotMdds'
        mdd_hot_req = requests.get(mdd_hot_url, headers=headers)
        mdd_hot_data = dict(json.loads(mdd_hot_req.text)['data'])
        mdd_values = tuple(mdd_hot_data.values())
        mdd_keys = tuple(mdd_hot_data.keys())
        mdd_url = 'http://wwww.mafengwo.cn/travel-scenic-spot/mafengwo/'
        for i in range(0, len(mdd_keys)):
            place_hot.append({'href': mdd_url + mdd_keys[i] + '.html', 'place': mdd_values[i]})
        result.append(
            {'title': head_title, 'abstract': head_p, 'bgr_url': img_src, 'ziyouxing': '', 'place_hot': place_hot})
        # 热门目的地的解析部分
        # 热门目的地的解析结果
        hot_list_result = {}
        # 热门目的地的分类
        div_hot_name_list = selector.xpath('//div[@class="r-navbar"]/a/text()')
        # 记录热门目的地遍历到哪里
        div_hot_name_number = 0
        # 解析页面热门目的地默认选中部分
        div_hot_list_col = selector.xpath('//div[@class="hot-list clearfix"]/div[@class="col"]')
        # 第一列
        hot_list_count = 1
        hot_list_col = {}
        for i in div_hot_list_col:
            dl = i.xpath('dl')
            row = 1
            hot_list_row = {}
            for j in dl:
                # 目的地的标题
                dt = j.xpath('dt/a/text()')
                if len(dt) == 0:
                    dt = j.xpath('dt/text()')

                # 目的地的城市
                dd = j.xpath('dd/a/text()')
                hot_list_row['row' + str(row)] = {'dt': dt, 'dd': dd}
                row = row + 1
            hot_list_col['col' + str(hot_list_count)] = hot_list_row
            hot_list_count = hot_list_count + 1
        # 选中的热门目的地解析完成
        hot_list_result[div_hot_name_list[div_hot_name_number]] = hot_list_col
        div_hot_name_number = div_hot_name_number + 1
        # 解析没有选中的热门目的地
        div_hot_list_hide = selector.xpath('//div[@class="hot-list clearfix hide"]')
        for div_hide in div_hot_list_hide:
            div_hot_list_hide_col = div_hide.xpath('div[@class="col"]')
            hot_list_col_hide = {}
            hot_list_hide_count = 1
            for i in div_hot_list_hide_col:
                dl = i.xpath('dl')
                row = 1
                hot_list_hide_row = {}
                for j in dl:
                    # 热么目的地标题
                    dt = j.xpath('dt/a/text()')
                    if len(dt) == 0:
                        dt = j.xpath('dt/text()')

                    # 热门目的地城市名字
                    dd = j.xpath('dd/a/text()')
                    hot_list_hide_row['row' + str(row)] = {'dt': dt, 'dd': dd}
                    row = row + 1
                hot_list_col_hide['col' + str(hot_list_hide_count)] = hot_list_hide_row
                hot_list_hide_count = hot_list_hide_count + 1
            # 未选中的热门目的地解析完成
            hot_list_result[div_hot_name_list[div_hot_name_number]] = hot_list_col_hide
            div_hot_name_number = div_hot_name_number + 1
        # 热门目的地解析全部完成
        result.append({'hot_list_result': hot_list_result})

        # 当季推荐的解析部分
        url = 'https://pagelet.mafengwo.cn/mdd/pagelet/seasonRecommendApi?params=%7B%7D'
        headers = {
            'Host': 'pagelet.mafengwo.cn',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Upgrade - Insecure - Requests': '1'
        }
        req = requests.get(url, headers=headers)
        html = json.loads(req.text)['data']['html']
        selector = fromstring(html)
        season_recommend = []
        div_tiles_col_list = []
        div_tiles_col = selector.xpath('//div[@class="tiles"]/div[contains(@class,"item")]')
        for col in div_tiles_col:
            # 图片的来源
            src = col.xpath('a/img/@src')[0]
            # 图片的标题
            title = col.xpath('a/div/text()')
            if len(title) == 0:
                title = '更多'
            div_tiles_col_list.append({'src': src, 'title': title})
        season_recommend.append({'key':1,'detail':div_tiles_col_list})
        div_tiles_col_list = []
        tiles_hide_count = 2
        tiles_hide = selector.xpath('//div[@class="tiles hide"]')
        for tiles in tiles_hide:
            div_tiles_hide_egg = tiles.xpath('div[contains(@class,"item")]')
            for div_tiles_hide in div_tiles_hide_egg:
                src = div_tiles_hide.xpath('a/img/@src')[0]
                title = div_tiles_hide.xpath('a/div/text()')
                if len(title) == 0:
                    title = '更多'
                div_tiles_col_list.append({'src': src, 'title': title})
            season_recommend.append({'key':tiles_hide_count,'detail':div_tiles_col_list})
            div_tiles_col_list = []
            tiles_hide_count = tiles_hide_count + 1
        # 当季推荐解析完成
        result.append({'season_recommend': season_recommend})
        return result
    except Exception as e:
        print(e)


def get_head_show_image():
    """
    解析首页头图
    :return:
    """
    url = 'http://www.mafengwo.cn/'
    headers = {
        'Host': 'www.mafengwo.cn',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Cache-Control': 'max-age=0',
        'Upgrade - Insecure - Requests': '1',
        'Pragma': 'no-cache'
    }
    r = requests.get(url, headers=headers)
    try:
        r.raise_for_status()
        # 获得html信息
        # bs4获取数据
        selector = etree.HTML(r.text)
        # 图片地址数组
        data = []
        link = selector.xpath('//ul[@class="show-image"]/li/a[1]/@href')
        src = selector.xpath('//ul[@class="show-image"]/li/a[1]/img/@src')
        h3 = selector.xpath('//ul[@class="show-image"]/li/a[2]/h3/text()')
        div_list = selector.xpath('//ul[@class="show-image"]/li/a[2]/div')
        head_img_info = []
        date = []
        for i in div_list:
            date.append(i.xpath('string(.)').replace('\n', '').replace(' ', ''))
        for i in range(0, len(link)):
            date_ = date[i].split('/')
            head_img_info.append(
                {'index': str(i + 1), 'href': 'https://www.mafengwo.cn'+link[i], 'src': src[i], 'txt3': h3[i], 'txt1': date_[0],
                 'txt2': date_[1]})
        data.append({'head_info': head_img_info})
        hot_place_a_list = selector.xpath('//div[@class="hot-place"]/a')
        hot_place_count = 1
        places = []
        for a in hot_place_a_list:
            places.append({'place': a.attrib['data-name'], 'id': str(hot_place_count)})
            hot_place_count = hot_place_count + 1
        fav_list = []
        fav_li_list = selector.xpath('//ul[@class="interest-list clearfix"]/li')
        for fav in fav_li_list:
            title = fav.xpath('a/h3/text()')[0]
            abstract = fav.xpath('a/p/text()')[0]
            img_url = fav.xpath('a/span/img/@src')[0]
            fav_list.append({'title': title, 'abstract': abstract, 'img_url': img_url, 'id': str(hot_place_count)})
            hot_place_count = hot_place_count + 1
        data.append({'fav': fav_list, 'places': places})
        return data
    except Exception as e:
        print(e)
        print(2)


def get_head_tn_list(page=None):
    """
    首页热门游记的解析入口
    :param page:
    :return:
    """
    if page is None or page == '':
        page = 0
    url = 'http://pagelet.mafengwo.cn/note/pagelet/recommendNoteApi?params={"type":0,"objid":0,"page":' + str(
        page) + '}'
    headers = {
        'Host': 'pagelet.mafengwo.cn',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Upgrade - Insecure - Requests': '1'
    }
    return get_head_parser(url, headers)


def get_head_tn_list0(page=None):
    """
    首页最新发表的解析的入口
    :param page:
    :return:
    """
    if page is None or page == '':
        page = 0
    url = 'http://pagelet.mafengwo.cn/note/pagelet/recommendNoteApi?params={"type":3,"objid":0,"page":' + str(
        page) + '}'
    headers = {
        'Host': 'pagelet.mafengwo.cn',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Upgrade - Insecure - Requests': '1'
    }
    return get_head_parser(url, headers)


def get_head_parser(url, headers):
    """
    首页热门游记和最先发表的具体实现
    :param url:
    :param headers:
    :return:
    """
    r = requests.get(url, headers=headers)
    index = 0
    try:
        r.raise_for_status()
        # 获得html信息
        html = json.loads(r.text)['data']['html']
        # print(html)
        div_selector = fromstring(html)
        # print(div_selector)
        count = div_selector.xpath('//span[@class="count"]')[0].text
        item = div_selector.xpath('//div[@class="tn-item clearfix"]')
        # 图片地址数组
        data = []
        for selector in item:
            href = selector.xpath('div[@class="tn-image"]/a/@href')[0]
            image_src = selector.xpath('div[@class="tn-image"]/a/img/@data-src')
            dt = selector.xpath('div[@class="tn-wrapper"]/dl/dt/a[@target="_blank"]/text()')[0]
            dd = selector.xpath('div[@class="tn-wrapper"]/dl/dd/a/text()')[0]
            # 有的不显示所在地
            tn_place = selector.xpath(
                'div[@class="tn-wrapper"]/div[@class="tn-extra"]/span[@class="tn-place"]/a/text()')
            tn_place = tn_place[0] if len(tn_place) != 0 else ''
            tn_user = \
                selector.xpath('div[@class="tn-wrapper"]/div[@class="tn-extra"]/span[@class="tn-user"]/a/text()[2]')[
                    0].strip()
            tn_user_img = selector.xpath(
                'div[@class="tn-wrapper"]/div[@class="tn-extra"]/span[@class="tn-user"]/a/img/@src')[0]
            tn_user_url = selector.xpath(
                'div[@class="tn-wrapper"]/div[@class="tn-extra"]/span[@class="tn-user"]/a/@href')[0]
            tn_nums = selector.xpath('div[@class="tn-wrapper"]/div[@class="tn-extra"]/span[@class="tn-nums"]/text()')[0]
            ding = selector.xpath('div[@class="tn-wrapper"]/div[@class="tn-extra"]/span[@class="tn-ding"]/em/text()')[0]
            data.append(
                {'index': str(index + 1), 'raiders_url': href, 'img_url': image_src, 'title': dt,
                 'abstract': dd,
                 'place': tn_place,
                 'place_url': '', 'user_img': tn_user_img,
                 'user_name': tn_user,
                 'user_url': tn_user_url,
                 'nums': tn_nums,
                 'ding': ding})
            index = index + 1
        return data, count
    except Exception as e:
        print(e)
        print(1)


def parser_youji_head_text(id):
    try:
        url = 'http://www.mafengwo.cn/i/' + id + '.html'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh - CN, zh;q = 0.9',
            'Cache-Control': 'no-cache',
            'pragma': 'no-cache',
            'Upgrade - Insecure - Requests': '1',
            'Referer': 'http://www.mafengwo.cn/'
        }
        contentHead = {}
        contentText = {}
        req = requests.get(url, headers=headers)
        req.encoding = 'utf-8'
        selector = fromstring(req.text)
        title_img_url = selector.xpath('//div[@class="set_bg _j_load_cover"]/img/@src')[0]
        contentHead['title_img_url'] = title_img_url
        content_title = selector.xpath('//div[@class="vi_con"]/h1/text()')[0]
        contentHead['content_title'] = content_title
        time = '' if len(selector.xpath(
            '//div[@class="tarvel_dir_list clearfix"]/ul/li[@class="time"]/text()')) == 0 else selector.xpath(
            '//div[@class="tarvel_dir_list clearfix"]/ul/li[@class="time"]/text()')
        day = '' if len(selector.xpath('//div[@class="tarvel_dir_list clearfix"]/ul/li[@class="day"]/text()')) == 0 else \
            selector.xpath('//div[@class="tarvel_dir_list clearfix"]/ul/li[@class="day"]/text()')[1]
        people = '' if len(
            selector.xpath('//div[@class="tarvel_dir_list clearfix"]/ul/li[@class="people"]/text()')) == 0 else \
            selector.xpath('//div[@class="tarvel_dir_list clearfix"]/ul/li[@class="people"]/text()')[1]
        cost = '' if len(
            selector.xpath('//div[@class="tarvel_dir_list clearfix"]/ul/li[@class="cost"]/text()')) == 0 else \
            selector.xpath('//div[@class="tarvel_dir_list clearfix"]/ul/li[@class="cost"]/text()')[1]
        contentText['time'] = time
        contentText['day'] = day
        contentText['people'] = people
        contentText['cost'] = cost
        url = 'http://pagelet.mafengwo.cn/note/pagelet/headOperateApi?params={"iid":' + str(id) + '}'
        headers = {
            'Host': 'pagelet.mafengwo.cn',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Cache-Control': 'no-cache',
            'pragma': 'no-cache',
            'Upgrade - Insecure - Requests': '1'
        }
        req = requests.get(url, headers=headers)
        head_html = json.loads(req.text)['data']['html']
        selector = fromstring(head_html)
        num_ding = selector.xpath('//a[@class="up_act "]/@data-vote')[0]
        contentHead['num_ding'] = num_ding
        per_home_url = 'http://www.mafengwo.cn' + selector.xpath('//a[@class="per_pic"]/@href')[0]
        contentHead['per_home_url'] = per_home_url
        per_pic_url = selector.xpath('//a[@class="per_pic"]/img/@src')[0]
        contentHead['per_pic_url'] = per_pic_url
        per_name = selector.xpath('//a[@class="per_name"]/text()')[0].strip().replace('\n', '').replace(' ', '')
        contentHead['per_name'] = per_name
        per_grade = selector.xpath('//a[@class="per_grade"]/@title')[0]
        contentHead['per_grade'] = per_grade
        vip = 'true'
        contentHead['vip'] = vip
        vip_url = ''
        contentHead['vip_url'] = vip_url
        vip_img_url = ''
        contentHead['vip_img_url'] = vip_img_url
        time = selector.xpath('//div[@class="vc_time"]/span[@class="time"]/text()')[0]
        contentHead['time'] = time
        view = selector.xpath('//div[@class="vc_time"]/span[2]/text()')[0]
        contentHead['view'] = view
        vnum_share = selector.xpath('//a[@class="bs_btn"]/span[1]/text()')[0]
        contentHead['vnum_share'] = vnum_share
        num_collect = selector.xpath('//a[@class="bs_btn _j_do_fav"]/span[1]/text()')[0]
        contentHead['num_collect'] = num_collect
        return contentHead, contentText
    except Exception as e:
        print(e)


def parser_youji_detail(id, seq=None):
    """
    游记内容页的解析
    :param id:游记的id
    :param seq:游记div的seq，懒加载
    :return:
    """
    url = 'http://www.mafengwo.cn/note/ajax.php?act=getNoteDetailContentChunk&id=' + str(id)
    if seq is not None:
        url = url + '&seq=' + str(seq)
    headers = {
        'Host': 'www.mafengwo.cn',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Upgrade - Insecure - Requests': '1',
        'Referer': 'http://www.mafengwo.cn/'
    }
    req = requests.get(url, headers=headers)
    try:
        req.raise_for_status()
        req.encoding = req.apparent_encoding
        dict_data = json.loads(req.text)['data']
        has_more = dict_data['has_more']
        html = str(dict_data['html'])
        soup = BeautifulSoup(html, 'html.parser')
        index = -1
        tag = soup.contents[index]
        while isinstance(tag, NavigableString):
            index = index - 1
            tag = soup.contents[index]
        seq = tag.attrs['data-seq'] if has_more == True else ''
        for tag in soup.contents:
            if isinstance(tag, Tag):
                if tag.attrs['class'][0] == 'add_pic':
                    for div_tag in tag.contents:
                        if isinstance(div_tag, Tag):
                            for img_tag in div_tag.contents:
                                if isinstance(img_tag, Tag):
                                    img_tag.attrs['src'] = img_tag.attrs['data-src']
                                    break
                            break
        return str(soup), seq
    except Exception as e:
        print(e)


def gonglve_content_parser_3():
    """
    攻略页  点击攻略页面跳转之后页面的解析
    :return:
    """
    url = 'https://www.mafengwo.cn/gonglve/ziyouxing/133210.html?cid=1010616'
    headers = {
        'Host': 'www.mafengwo.cn',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Cache-Control': 'max-age=0',
        'Upgrade - Insecure - Requests': '1',
        'Pragma': 'no-cache'
    }
    type = '3'
    req = requests.get(url, headers=headers)
    selector = fromstring(req.text)
    gonglve_head = []
    # 文章的标题
    title = selector.xpath('//div[@class="l-topic"]/h1/text()')[0].strip()
    # 文章的浏览数目
    liulan = selector.xpath('//div[@class="sub-tit"]/span[@class="time"][1]/em/text()')[0].strip()
    # 文章的时间
    time = selector.xpath('//div[@class="sub-tit"]/span[@class="time"][2]/em/text()')[0].strip()
    # 文章归属类型
    content_name = selector.xpath('//div[@class="sub-tit"]/span[@class="time"][2]/text()')[0].strip()
    # goolve_head 添加 标题浏览等信息
    gonglve_head.append({'title': title})
    gonglve_head.append({'liulan': liulan})
    gonglve_head.append({'time': time})
    gonglve_head.append({'content_name': content_name})
    # 文章的内容解析部分
    f_block_list = selector.xpath('//div[@class="_j_content"]/div[@class="f-block"]')
    gonglve_content = []
    for f_block in f_block_list:
        if len(f_block.xpath('div[@class="p-section"]')) != 0:
            p_content = f_block.xpath('div[@class="p-section"]')[0]
            html = tostring(p_content, encoding='utf-8').decode('utf-8').strip().replace('\n', '')
            soup = BeautifulSoup(html, 'html.parser')
            p_section = soup.find('div')
            p_list = []
            for p_content in p_section.children:
                # 如果p是个文本
                if isinstance(p_content, NavigableString):
                    if len(str(p_content)) == 0 or str(p_content) == '' or str(p_content) == ' ':
                        continue
                    else:  # 这里总是不能显示&nbsp:
                        p_list.append({'p_text': str(p_content).strip()})
                elif p_content.name == 'b':
                    p_list.append({'p_b': p_content.string.strip()})
                # 如果p是个br标签
                elif p_content.name == 'br':
                    p_list.append({'p_br': '<br>'})
                # 如果是个a 标签
                elif p_content.name == 'a':
                    p_list.append({'p_a': [{'a_href': p_content.attrs['href'], 'a_text': p_content.string}]})
                else:
                    continue
            gonglve_content.append({'p': p_list})
        elif len(f_block.xpath('h3')) != 0:
            gonglve_content.append({'h3': f_block.xpath('h3/text()')[0].strip()})
        elif len(f_block.xpath('h2')) != 0:
            gonglve_content.append({'h2': f_block.xpath('h2/text()')[0].strip()})
        elif len(f_block.xpath('div[@class="tips-box"]')) != 0:
            tips_box = f_block.xpath('div[@class="tips-box"]')[0]
            html = tostring(tips_box, encoding='utf-8').decode('utf-8').replace('\n', '')
            soup = BeautifulSoup(html, 'html.parser').find('div')
            tip_list = []
            for tip in soup.children:
                if tip.name == 'b':
                    tip_list.append({'tip_b': str(tip.string).strip()})
                elif tip.name == 'br':
                    tip_list.append({'tip_br': '<br>'})
                elif isinstance(tip, NavigableString):
                    if str(tip) == '' or str(tip) == ' ' or len(str(tip)) == 0:
                        continue
                    else:
                        tip_list.append({'tip_text': str(tip).strip()})
            gonglve_content.append({'tip': tip_list})
        elif len(f_block.xpath('img')) != 0:
            gonglve_content.append({'img': f_block.xpath('img/@data-src')[0].strip()})
        else:
            continue
    return {'gonglve_content': gonglve_content, 'gonglve_head': gonglve_head}


def ziyouxing_parser(id):
    try:
        url = 'https://www.mafengwo.cn/gonglve/ziyouxing/' + str(id) + '.html'
        headers = {
            'Host': 'www.mafengwo.cn',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Cache-Control': 'no-cache',
            'pragma': 'no-cache',
            'Upgrade - Insecure - Requests': '1'
        }
        req = requests.get(url=url, headers=headers)
        req.encoding = 'utf-8'
        html = fromstring(req.text)
        location = html.xpath('//div[@class="crumb"]/a[2]/text()')[0]
        ziyouxingl = {}
        title = html.xpath('//div[@class="l-topic"]/h1/text()')[0]
        read_num = html.xpath('//div[@class="sub-tit"]/span[1]/em/text()')[0]
        time = html.xpath('//div[@class="sub-tit"]/span[2]/em/text()')[0].strip()
        author_href = ''
        if len(html.xpath('//div[@class="in-t"]/a/@href')) != 0:
            author_href = html.xpath('//div[@class="in-t"]/a/@href')[0]
        else:
            author_href = html.xpath('//div[@class="in-t"]/span[@class="name"]/a/@href')[0]
        author_name = ''
        if len(html.xpath('//div[@class="in-t"]/a/span/text()')) != 0:
            author_name = html.xpath('//div[@class="in-t"]/a/span/text()')[0]
        else:
            author_name = html.xpath('//div[@class="in-t"]/span[@class="name"]/a/text()')[0].strip()
        author_src = html.xpath('//div[@class="author"]/a/img/@src')[0]
        author_identity = html.xpath('//div[@class="in-t"]/span[@class="rz"]/text()')[0]
        gonglveDetail = etree.tostring(etree.HTML(req.text).xpath('//div[@class="_j_content"]')[0], encoding='utf-8',
                                       method='html').decode('utf-8')
        soup = BeautifulSoup(gonglveDetail, 'html.parser').contents[0]
        for tag in soup.contents:
            if isinstance(tag, Tag):
                for div_list in tag:
                    if isinstance(div_list, Tag):
                        if div_list.name == 'img':
                            div_list.attrs['src'] = div_list.attrs['data-src']
                            break
                        break
        ziyouxingl['title'] = title
        ziyouxingl['read_num'] = read_num
        ziyouxingl['time'] = time
        ziyouxingl['author_href'] = 'https://www.mafengwo.con' + author_href
        ziyouxingl['author_src'] = author_src
        ziyouxingl['author_name'] = author_name
        ziyouxingl['author_identity'] = author_identity
        ziyouxingr = {}
        selector = html.xpath('//div[@class="bar-sar clearfix"]')[0]
        comment_num = selector.xpath('a[@class="_j_goto_comment"]/em/text()')[0]
        collect_num = selector.xpath('div[@class="bs_collect"]/a/em/text()')[0]
        share_num = selector.xpath('div[@class="bs_share"]/a/em/text()')[0]
        zan_num = selector.xpath('a[@class="_j_like_btn"]/em/text()')[0]
        ding_num = selector.xpath('a[@class="_j_support_btn"]/em/text()')[0]
        catalogue = []
        selector = html.xpath('//div[@class="section"]/div[@class="top"]')
        section_index = 1
        for a in selector:
            key = section_index
            title = a.xpath('a/text()')[0]
            catalogue.append({'key': key, 'title': title})
            section_index = section_index + 1
        ziyouxingr['comment_num'] = comment_num
        ziyouxingr['collect_num'] = collect_num
        ziyouxingr['share_num'] = share_num
        ziyouxingr['zan_num'] = zan_num
        ziyouxingr['ding_num'] = ding_num
        ziyouxingr['catalogue'] = catalogue
        ziyouxing_related = {}
        gong_lve = []
        mdd_id = html.xpath('//div[@class="crumb"]/a[2]/@href')[0].split('_')[1][:-1]
        url = 'https://www.mafengwo.cn/gonglve/ziyouxing/detail/relation_guides?gid=' + id + '&mddid=+' + mdd_id
        req = requests.get(url=url, headers=headers)
        req.encoding = 'utf-8'
        html = json.loads(req.text)['html']
        selector = fromstring(html)
        ul = selector.xpath('//ul[@class="bd clearfix"]/li')
        li_index = 1
        for li in ul:
            key = li_index
            related_title = li.xpath('a/@title')[0]
            related_href = li.xpath('a/@href')[0]
            related_src = li.xpath('a/div[@class="img"]/img/@src')[0]
            related_p1 = li.xpath('a/div[@class="info"]/div/p[1]/text()')[0]
            related_p2 = li.xpath('a/div[@class="info"]/div/p[2]/text()')[0]
            gong_lve.append(
                {'key': key, 'related_title': related_title, 'related_src': related_src, 'related_href': related_href,
                 'related_p1': related_p1, 'related_p2': related_p2})
            li_index = li_index + 1
        ziyouxing_related['gong_lve'] = gong_lve

        if len(selector.xpath('//a[@class="pro_more"]/@href')) != 0:
            ziyouxing_related['more_href'] = selector.xpath('//a[@class="pro_more"]/@href')[0]
        else:
            ziyouxing_related['more_href'] = ''
        return location, ziyouxingl, ziyouxingr, ziyouxing_related
    except Exception as e:
        print(e)


def wenda_parser():
    try:
        # 热门问题
        hot_questions = []
        # 最新问题
        new_questions = []
        # 待回答问题
        wait_questions = []
        # 热门问题
        url = 'https://www.mafengwo.cn/qa/ajax_qa/more?type=1&mddid=&tid=&sort=10&key=&page=0&time='
        headers = headers = {
            'Host': 'www.mafengwo.cn',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Cache-Control': 'no-cache',
            'pragma': 'no-cache',
            'Upgrade - Insecure - Requests': '1',
            'x-requested-with': 'XMLHttpRequest'
        }
        req = requests.get(url=url, headers=headers)
        html = json.loads(req.text)['data']['html']
        selector = fromstring(html)
        li_list = selector.xpath('//li[@class="item clearfix "]')
        # 得到每个li标签
        index = 1
        for li in li_list:
            key = int('1' + str(index))
            wenda_url = 'https://www.mafengwo.cn' + li.xpath('div[@class="title"]/a/@href')[0]
            title = li.xpath('div[@class="title"]/a/text()')[0]
            user_href = 'https://www.mafengwo.cn' + \
                        li.xpath('div[@class="container"]/div[@class="avatar"]/a/@href')[0]
            user_img = li.xpath('div[@class="container"]/div[@class="avatar"]/a/img/@src')[0]
            guide = False
            if len(li.xpath('div[@class="container"]/div[@class="identity"]/a/text()')) != 0:
                if li.xpath('div[@class="container"]/div[@class="identity"]/a/text()')[0] == '指路人':
                    guide = True
            img_url = ''
            if len(li.xpath('div[@class="container"]/div[@class="desc clearfix"]/a/img')) != 0:
                img_url = li.xpath('div[@class="container"]/div[@class="desc clearfix"]/a/img/@src')[0]
            elif len(li.xpath('div[@class="container"]/div[@class="desc clearfix"]/img')) != 0:
                img_url = li.xpath('div[@class="container"]/div[@class="desc clearfix"]/img/@src')[0]
            else:
                img_url = ''
            abstract = '' if (len(li.xpath('div[@class="container"]/div[@class="desc clearfix"]/a/p/text()'))) == 0 else \
                li.xpath('div[@class="container"]/div[@class="desc clearfix"]/a/p/text()')[0].strip()
            tags = []
            if len(li.xpath('div[@class="container"]/div[@class="tags"]')) != 0:
                tag_a_list = li.xpath('div[@class="container"]/div[@class="tags"]/a')
                for a in tag_a_list:
                    tag_href = 'https://www.mafengwo.cn' + a.xpath('@href')[0]
                    tag_title = a.xpath('text()')[0]
                    tags.append({'href': tag_href, 'title': tag_title})
            else:
                tags.append({'href': '', 'title': ''})
            zan_num = li.xpath('div[@class="container"]/div[@class="operate"]/div[@class="zan"]/text()')[0]
            mdd_href = 'https://www.mafengwo.cn' + \
                       li.xpath('div[@class="container"]/div[@class="operate"]/div[@class="mdd"]/a/@href')[0]
            mdd = li.xpath('div[@class="container"]/div[@class="operate"]/div[@class="mdd"]/a/text()')[0]
            comment_num = li.xpath('div[@class="container"]/div[@class="operate"]/a/span[@class="reply"]/text()')[0]
            date = li.xpath('div[@class="container"]/div[@class="operate"]/span[@class="date"]/text()')[0]
            index = index + 1
            hot_questions.append(
                {'key': key, 'date': date, 'comment_num': comment_num, 'mdd': mdd, 'mdd_href': mdd_href,
                 'zan_num': zan_num, 'tags': tags, 'abstract': abstract, 'img_url': img_url, 'guide': guide,
                 'user_img': user_img, 'user_href': user_href, 'title': title, 'wenda_url': wenda_url})
        # 新问题
        url = 'https://www.mafengwo.cn/qa/ajax_qa/more?type=0&mddid=&tid=&sort=1&key=&page=0&time='
        req = requests.get(url=url, headers=headers)
        html = json.loads(req.text)['data']['html']
        selector = fromstring(html)
        li_list = selector.xpath('//li[@class="item clearfix _j_question_item"]')
        index = 1
        for li in li_list:
            key = int('2' + str(index))
            wenda_url = ''
            if len(li.xpath('div[@class="container"]/div[@class="title"]/a/@href')) != 0:
                wenda_url = 'https://www.mafengwo.cn' + li.xpath('div[@class="container"]/div[@class="title"]/a/@href')[
                    0]
            else:
                wenda_url = 'https://www.mafengwo.cn' + li.xpath('div[@class="title"]/a/@href')[0]
            title = ''
            if len(li.xpath('div[@class="container"]/div[@class="title"]/a/text()')) != 0:
                title = li.xpath('div[@class="container"]/div[@class="title"]/a/text()')[0]
            else:
                title = title = li.xpath('div[@class="title"]/a/text()')[0]
            user_href = ''
            user_img = ''
            if len(li.xpath('div[@class="container"]/div[@class="avatar nm"]')) != 0:
                user_href = ''
                user_img = li.xpath('div[@class="container"]/div[@class="avatar nm"]/a/img/@src')[0]
            else:
                user_href = 'https://www.mafengwo.cn' + \
                            li.xpath('div[@class="container"]/div[@class="avatar"]/a/@href')[0]
                user_img = li.xpath('div[@class="container"]/div[@class="avatar"]/a/img/@src')[0]
            guide = False
            if len(li.xpath('div[@class="container"]/div[@class="identity"]/a/text()')) != 0:
                if li.xpath('div[@class="container"]/div[@class="identity"]/a/text()')[0] == '指路人':
                    guide = True
            img_url = ''
            if len(li.xpath('div[@class="container"]/div[@class="desc clearfix"]/a/img')) != 0:
                img_url = li.xpath('div[@class="container"]/div[@class="desc clearfix"]/a/img/@src')[0]
            elif len(li.xpath('div[@class="container"]/div[@class="desc clearfix"]/img'))!=0:
                img_url = li.xpath('div[@class="container"]/div[@class="desc clearfix"]/img/@src')[0]
            else:
                img_url = ''
            abstract = ''
            if len(li.xpath('div[@class="container"]/div[@class="desc clearfix"]/p/text()')) != 0:
                abstract = li.xpath('div[@class="container"]/div[@class="desc clearfix"]/p/text()')[0].strip()
            tags = []
            if len(li.xpath('div[@class="container"]/div[@class="tags"]')) != 0:
                tag_a_list = li.xpath('div[@class="container"]/div[@class="tags"]/a')
                for a in tag_a_list:
                    tag_href = 'https://www.mafengwo.cn' + a.xpath('@href')[0]
                    tag_title = a.xpath('text()')[0]
                    tags.append({'href': tag_href, 'title': tag_title})
            else:
                tags.append({'href': '', 'title': ''})
            zan_num = li.xpath('div[@class="container"]/div[@class="operate"]/div[@class="zan"]/text()')[0]
            mdd_href = 'https://www.mafengwo.cn' + \
                       li.xpath('div[@class="container"]/div[@class="operate"]/div[@class="mdd"]/a/@href')[0]
            mdd = li.xpath('div[@class="container"]/div[@class="operate"]/div[@class="mdd"]/a/text()')[0]
            comment_num = ''
            if len(li.xpath(
                    'div[@class="container"]/div[@class="operate"]/a[@class="reply-wait _j_filter_click"]')) != 0:
                comment_num = ''
            else:
                comment_num = li.xpath('div[@class="container"]/div[@class="operate"]/span[@class="reply"]/text()')[0]
            date = li.xpath('div[@class="container"]/div[@class="operate"]/span[@class="date"]/text()')[0]
            index = index + 1
            new_questions.append(
                {'key': key, 'date': date, 'comment_num': comment_num, 'mdd': mdd, 'mdd_href': mdd_href,
                 'zan_num': zan_num, 'tags': tags, 'abstract': abstract, 'img_url': img_url, 'guide': guide,
                 'user_img': user_img, 'user_href': user_href, 'title': title, 'wenda_url': wenda_url})
        # 待回答问题
        index = 1
        url = 'https://www.mafengwo.cn/qa/ajax_qa/more?type=2&mddid=&tid=&sort=1&key=&page=0&time='
        req = requests.get(url=url, headers=headers)
        html = json.loads(req.text)['data']['html']
        selector = fromstring(html)
        li_list = selector.xpath('//li[@class="item clearfix _j_question_item"]')
        for li in li_list:
            key = int('3' + str(index))
            wenda_url = 'https://www.mafengwo.cn' + li.xpath('div[@class="container"]/div[@class="title"]/a/@href')[0]
            title = li.xpath('div[@class="container"]/div[@class="title"]/a/text()')[0]
            user_href = ''
            user_img = ''
            if len(li.xpath('div[@class="container"]/div[@class="avatar nm"]')) != 0:
                user_href = ''
                user_img = li.xpath('div[@class="container"]/div[@class="avatar nm"]/a/img/@src')[0]
            else:
                user_href = 'https://www.mafengwo.cn' + li.xpath('div[@class="container"]/div[@class="avatar"]/a/@href')[0]
                user_img = li.xpath('div[@class="container"]/div[@class="avatar"]/a/img/@src')[0]
            guide = False
            if len(li.xpath('div[@class="container"]/div[@class="identity"]/a/text()')) != 0:
                if li.xpath('div[@class="container"]/div[@class="identity"]/a/text()')[0] == '指路人':
                    guide = True
            img_url = ''
            if len(li.xpath('div[@class="container"]/div[@class="desc clearfix"]/a/img')) != 0:
                img_url = li.xpath('div[@class="container"]/div[@class="desc clearfix"]/a/img/@src')[0]
            elif len(li.xpath('div[@class="container"]/div[@class="desc clearfix"]/img')) != 0:
                img_url = li.xpath('div[@class="container"]/div[@class="desc clearfix"]/img/@src')[0]
            else:
                img_url = ''
            abstract = ''
            if len(li.xpath('div[@class="container"]/div[@class="desc clearfix"]/p/text()')) != 0:
                abstract = li.xpath('div[@class="container"]/div[@class="desc clearfix"]/p/text()')[0].strip()
            tags = []
            if len(li.xpath('div[@class="container"]/div[@class="tags"]')) != 0:
                tag_a_list = li.xpath('div[@class="container"]/div[@class="tags"]/a')
                for a in tag_a_list:
                    tag_href = 'https://www.mafengwo.cn' + a.xpath('@href')[0]
                    tag_title = a.xpath('text()')[0]
                    tags.append({'href': tag_href, 'title': tag_title})
            else:
                tags.append({'href': '', 'title': ''})
            zan_num = li.xpath('div[@class="container"]/div[@class="operate"]/div[@class="zan"]/text()')[0]
            mdd_href = 'https://www.mafengwo.cn' + \
                       li.xpath('div[@class="container"]/div[@class="operate"]/div[@class="mdd"]/a/@href')[0]
            mdd = li.xpath('div[@class="container"]/div[@class="operate"]/div[@class="mdd"]/a/text()')[0]
            date = li.xpath('div[@class="container"]/div[@class="operate"]/span[@class="date"]/text()')[0]
            index = index + 1
            wait_questions.append(
                {'key': key, 'date': date, 'comment_num': '', 'mdd': mdd, 'mdd_href': mdd_href,
                 'zan_num': zan_num, 'tags': tags, 'abstract': abstract, 'img_url': img_url, 'guide': guide,
                 'user_img': user_img, 'user_href': user_href, 'title': title, 'wenda_url': wenda_url})
        return hot_questions, new_questions, wait_questions
    except Exception as e:
        print(e)


def wenda_detail_parser(id):
    try:
        url = 'https://www.mafengwo.cn/wenda/detail-' + id + '.html'
        headers = {
            'Host': 'www.mafengwo.cn',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Cache-Control': 'no-cache',
            'Upgrade - Insecure - Requests': '1',
            'Pragma': 'no-cache'
        }
        req = requests.get(url=url, headers=headers)
        req.encoding = 'utf-8'
        selector = fromstring(req.text)
        mdd = ''
        mdd_href = ''
        if len(selector.xpath('//div[@class="q-content"]/div[@class="q-title"]/a[@class="location"]'))!=0:
            mdd = selector.xpath('//div[@class="q-content"]/div[@class="q-title"]/a[@class="location"]/text()')[0]
            mdd_href = selector.xpath('//div[@class="q-content"]/div[@class="q-title"]/a[@class="location"]/@href')[0]
        title = selector.xpath('//div[@class="q-content"]/div[@class="q-title"]/h1/text()')[0].strip()
        detail = ''
        if len(selector.xpath('//div[@class="q-content"]/div[@class="q-desc"]/text()'))!=0:
            detail = selector.xpath('//div[@class="q-content"]/div[@class="q-desc"]/text()')[0]
        tags = []
        if len(selector.xpath('//div[@class="q-tags fl"]/a')) != 0:
            tag = selector.xpath('//div[@class="q-tags fl"]/a')
            tag_a_index = 1
            for a in tag:
                key = tag_a_index
                href = a.xpath('@href')[0]
                name = a.xpath('text()')[0]
                tags.append({'key': key, 'name': name, 'href': href})
                tag_a_index = tag_a_index + 1
        user_img = ''
        user_href = ''
        user_name = ''
        if len(selector.xpath('//div[@class="pub-bar fr"]/a[@class="photo"]')) !=0:
            user_href = 'https://www.mafengwo.cn'+selector.xpath('//div[@class="pub-bar fr"]/a[@class="photo"]/@href')[0]
            user_img = selector.xpath('//div[@class="pub-bar fr"]/a[@class="photo"]/img/@src')[0]
            user_name = selector.xpath('//div[@class="pub-bar fr"]/a[@class="name"]/text()')[0]
        if len(selector.xpath('//div[@class="pub-bar fr"]/span[@class="photo"]')) !=0:
            user_name = '匿名用户'
            user_img = selector.xpath('//div[@class="pub-bar fr"]/span[@class="photo"]/img/@src')[0]
            user_href = ''
        user = {}
        user['user_href'] = user_href
        user['user_img'] = user_img
        user['user_name'] = user_name
        time = selector.xpath('//div[@class="pub-bar fr"]/span[@class="time"]/span/text()')[0]
        liulan_num = selector.xpath('//div[@class="q-operate clearfix"]/div[@class="fr"]/span[1]/text()')[0]
        guanzhu_num = selector.xpath('//div[@class="q-operate clearfix"]/div[@class="fr"]/span[2]/span/text()')[0]
        num = ''
        if len(selector.xpath('//div[@class="answer-wrap"]/div[@class="hd"]')) != 0:
            num = selector.xpath('//div[@class="answer-wrap"]/div[@class="hd"]/span/text()')[0]
        answer_list = []
        answer_li_index = 1
        huida_li = selector.xpath('//div[@id="normal_answer_wrap"]/li')
        if len(huida_li) != 0:
            for li in huida_li:
                key = answer_li_index

                user_img = li.xpath(
                    'div[@class="answer-content _js_answer_content"]/div[@class="answer-info clearfix"]/div[@class="user-bar fl"]/a[@class="_j_filter_click avatar"]/img/@src')[
                    0]
                user_name = li.xpath(
                    'div[@class="answer-content _js_answer_content"]/div[@class="answer-info clearfix"]/div[@class="user-bar fl"]/a[@class="name"]/text()')[
                    0]
                user_level = li.xpath(
                    'div[@class="answer-content _js_answer_content"]/div[@class="answer-info clearfix"]/div[@class="user-bar fl"]/a[@class="level"]/text()')[
                    0]
                user_href = li.xpath(
                    'div[@class="answer-content _js_answer_content"]/div[@class="answer-info clearfix"]/div[@class="user-bar fl"]/a[@class="name"]/@href')[
                    0]
                guide = False if len(li.xpath(
                    'div[@class="answer-content _js_answer_content"]/div[@class="answer-info clearfix"]/div[@class="user-bar fl"]/a[@class="identity i-guide"]')) == 0 else True
                gold = False if len(li.xpath(
                    'div[@class="answer-content _js_answer_content"]/div[@class="answer-info clearfix"]/ul[@class="answer-medal fr"]/li[@class="gold"]/div/a')) == 0 else True
                answer = etree.tostring(li.xpath(
                    'div[@class="answer-content _js_answer_content"]/div[@class="_j_short_answer_item hide"]/div[@class="_j_answer_html"]')[
                                            0], encoding='utf-8', method='html').decode('utf-8')
                answer_list.append({'key': key, 'answer': answer, 'gold': gold, 'guide': guide, 'user_href': user_href,
                                    'user_level': user_level, 'user_img': user_img, 'user_name': user_name})
                answer_li_index = answer_li_index + 1
        return mdd, mdd_href, title, detail, tags, user, time, liulan_num, guanzhu_num, num, answer_list
    except Exception as e:
        print(e)


def wenda_related_parser(id):
    try:
        url = 'https://www.mafengwo.cn/wenda/detail-' + id + '.html'
        headers = {
            'Host': 'www.mafengwo.cn',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Cache-Control': 'no-cache',
            'Upgrade - Insecure - Requests': '1',
            'Pragma': 'no-cache'
        }
        req = requests.get(url=url, headers=headers)
        req.encoding = 'utf-8'
        selector = fromstring(req.text)
        mdd_id = \
            selector.xpath('//div[@class="q-content"]/div[@class="q-title"]/a[@class="location"]/@href')[0].split('-')[
                1].split('.')[0]
        url = 'https://pagelet.mafengwo.cn/qa/pagelet/TopRecommendApi?params={"mddid":' + mdd_id + '}'
        headers = {
            'Host': 'pagelet.mafengwo.cn',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Cache-Control': 'no-cache',
            'pragma': 'no-cache',
            'Upgrade - Insecure - Requests': '1'
        }
        req = requests.get(url=url, headers=headers)
        data = json.loads(req.text)['data']['html']
        html = fromstring(data)
        activity = []
        ul = html.xpath('//ul[@class="slide-img"]/li')
        activity_index = 1
        for li in ul:
            href = li.xpath('a/@href')[0]
            src = li.xpath('a/img/@src')[0]
            key = int('1' + str(activity_index))
            activity_index = activity_index + 1
            activity.append({'key': key, 'href': href, 'src': src})
        url = 'https://pagelet.mafengwo.cn/qa/pagelet/RelationQuestionApi?params={"qid":' + id + '}'
        req = requests.get(url=url, headers=headers)
        data = json.loads(req.text)['data']['html']
        html = fromstring(data)
        related_questions = []
        ul = html.xpath('//ul[@class="bd"]/li')
        related_index = 1
        for li in ul:
            title = li.xpath('a/text()')[0].strip()
            href = li.xpath('a/@href')[0]
            answer = li.xpath('span/text()')[0]
            key = int('2' + str(related_index))
            related_index = related_index + 1
            related_questions.append({'key': key, 'href': href, 'answer': answer, 'title': title})
        return activity, related_questions
    except Exception as  e:
        print(e)
