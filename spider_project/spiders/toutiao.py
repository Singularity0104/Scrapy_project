import scrapy
import json
import os

class ToutiaoSpider(scrapy.Spider):
    name = 'toutiao'
    allowed_domains = ['toutiao.com']
    # start_urls = ['https://www.toutiao.com/api/search/content/?aid=24&app_name=web_search&offset=20&format=json&keyword=%E5%A4%A9%E6%B4%A5%E5%A4%A7%E5%AD%A6&autoload=true&count=20&en_qc=1&cur_tab=1&from=search_tab&pd=synthesis&timestamp=1614157607932&_signature=_02B4Z6wo00d01eSGQrgAAIDCVHeuccSOOjnko0YAABkZiSb5Uzv3p4E4shdf5aTDMxSrdk.Zi6VqTvr.3NL7p-NCKPmmowCvvLJu73Ka7mkO8jC92wl3fRKz-tWUNHyYjrtGnuLnrOUAcfT7ba']
    # start_urls = ['https://www.toutiao.com/api/search/content/?aid=24&app_name=web_search&offset=0&format=json&keyword=%E5%A4%A9%E6%B4%A5%E5%A4%A7%E5%AD%A6&autoload=true&count=20&en_qc=1&cur_tab=1&from=search_tab&pd=synthesis']

    cookies = {
        "tt_webid": "6929428965006263821",
        "ttcid": "8dbc5def8c7945ab9aa0e361bff2085e29",
        "csrftoken": "6e1669a671ec132b5f37b8bfebb369bb",
        "tt_webid": "6929428965006263821",
        "csrftoken": "6e1669a671ec132b5f37b8bfebb369bb",
        "s_v_web_id": "verify_klq1iuc6_vkq1wmqK_Z57s_49X9_AnLR_Gm0Jp9sckkEU",
        "__tasessionId": "8nkywh4qc1614570392590",
        "__ac_nonce": "0603c639a006b5bdbfc20",
        "__ac_signature": "_02B4Z6wo00f01Ek4pcwAAIDD-clJBJTRSchJHKFAAHJ5VtWkF9FHKtlDkDh.HMKzjrW7E3awyviCEOHtnhgVOLR0jc5tcKQ255QMLED5G36MecHVwUfKUiSoep.K-meTS3.SzTfGf-uEfwVbbb	",
        "MONITOR_WEB_ID": "bbabba8b-3505-457e-b489-5895217c16cf	",
        "tt_scid": "hyvFpYOgbE-r8YU5vvJTTjWCP3woVRKWI1V4Zhy8P8vr0Wlf8HaY0Tlj8D4SnyMea058	"

    }
    search_words = [
        "天津大学"
    ]

    def create_url(self, search_word, count=20, offset=0):
        base_url = "https://www.toutiao.com/api/search/content/"
        return base_url + "?aid=24&app_name=web_search&offset=" + str(offset) + "&format=json&keyword=" + search_word + "&autoload=true&count=" + str(count) + "&en_qc=1&cur_tab=1&from=search_tab&pd=synthesis"

    def start_requests(self):
        for word in self.search_words:
            url = self.create_url(word)
            yield scrapy.Request(
                url,
                dont_filter=True,
                callback=self.parse,
                cookies=self.cookies,
                meta={"word": word, "offset": 0}
            )

    def parse(self, response):
        # text = response.body
        # file = open("./toutiao.html", "wb")
        # file.write(text)
        # file.close()
        word = response.meta["word"]
        offset = response.meta["offset"]
        res = json.loads(response.text)
        if res["data"] is not None:
            toutiao_item_set = {}
            toutiao_item_set["offset"] = offset
            toutiao_item_set["search_word"] = word
            toutiao_item_set["data"] = []
            for item in res.get("data"):
                if "abstract" in item:
                    toutiao_item = {}
                    toutiao_item["search_word"] = word
                    toutiao_item["id"] = item.get("item_id")
                    toutiao_item["title"] = item.get("title")
                    toutiao_item["article_url"] = item.get("article_url")
                    toutiao_item["time"] = item.get("datetime")
                    toutiao_item["read_count"] = item.get("read_count")
                    toutiao_item["comment_count"] = item.get("comment_count")
                    toutiao_item["author_id"] = item.get("media_creator_id")
                    toutiao_item["author_name"] = item.get("media_name")
                    toutiao_item["abstract"] = item.get("abstract")
                    # yield toutiao_item
                    toutiao_item_set["data"].append(toutiao_item)
            yield toutiao_item_set
            url = self.create_url(word, offset=offset + 20, count=20)
            yield scrapy.Request(
                url,
                dont_filter=True,
                callback=self.parse,
                cookies=self.cookies,
                meta={"word": word, "offset": offset + 20}
            )


