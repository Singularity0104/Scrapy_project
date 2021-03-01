import scrapy
import re
import json

class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['api.zhihu.com']
    # start_urls = ['https://www.zhihu.com/search?q=天津大学&type=content&range=1d']
    cookies = {
        "KLBRSID": "37f2e85292ebb2c2ef70f1d8e39c2b34|1613643579|1613643492",
        "Hm_lvt_98beee57fd2ef70ccdd5ca52b9740c49": "1613620841,1613620852,1613641306,1613641341",
        "d_c0": "\"AIDY6Ek9rRKPTmcQpZCMb9Y85d_xRREzPOw=|1613643545\"",
        "Hm_lpvt_98beee57fd2ef70ccdd5ca52b9740c49": "1613643545",
        "_zap": "7009ff8c-7329-4f7d-ba0a-8debe42b03d0",
        "_xsrf": "0PdrAiFldsVhbvjaohnslCYfrsCD2SOt"

    }
    search_words = [
        "天津大学"
    ]
    # start_urls = ['https://api.zhihu.com/search_v3?limit=20&offset=0&q=天津大学&t=general&time_zone=a_day']

    def create_url(self, search_word, limit=20, offset=0, t="general", time_zone="a_day"):
        base_url = "https://api.zhihu.com/search_v3"
        return base_url + "?limit=" + str(limit) + "&offset=" + str(offset) + "&q=" + search_word + "&t=" + t + "&time_zone=" + time_zone

    def create_question_url(self, id, limit=5, offset=0, sort_by="default"):
        base_url = "https://www.zhihu.com/api/v4/questions/"
        url_part = "/answers?include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cattachment%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Cis_labeled%2Cpaid_info%2Cpaid_info_content%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cis_recognized%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%2A%5D.topics%3Bdata%5B%2A%5D.settings.table_of_content.enabled"
        return base_url + id + url_part + "&limit=" + str(limit) + "&offset=" + str(offset) + "&platform=desktop" + "&sort_by=" + sort_by

    def start_requests(self):
        for word in self.search_words:
            url = self.create_url(word)
            yield scrapy.Request(
                url,
                dont_filter=True,
                # headers=self.header,
                callback=self.parse,
                cookies=self.cookies,
                meta={"word": word, "page_num": 1}
            )

    def parse(self, response):
        word = response.meta["word"]
        page_num = response.meta["page_num"]
        # text = response.body
        # dir_name = "./data/" + word + "/list"
        # if os.path.exists(dir_name) is False:
        #     os.makedirs(dir_name)
        # file = open(dir_name + "/" + word + "_" + str(page_num) + ".html", "wb")
        # file.write(text)
        # file.close()
        res = json.loads(response.text)
        if res["data"] is not None:
            for item in res["data"]:
                if "object" in item:
                    if "question" in item["object"]:
                        title = item["object"]["question"]["name"]
                        id = item["object"]["question"]["id"]
                    else:
                        title = item["object"]["title"]
                        id = item["object"]["id"]
                    title = title.replace("<em>", "")
                    title = title.replace("</em>", "")
                    print(title)
                    print(id)
                    question_url = self.create_question_url(id)
                    question_item = {}
                    question_item["search_word"] = word
                    question_item["id"] = id
                    question_item["title"] = title
                    question_item["answer"] = []
                    yield scrapy.Request(
                        question_url,
                        dont_filter=True,
                        callback=self.parse_question_detail,
                        cookies=self.cookies,
                        meta={"question_item": question_item, "page_num": 1}
                    )
        if res["paging"]["is_end"] is False:
            next_url = res["paging"]["next"]
            yield scrapy.Request(
                next_url,
                dont_filter=True,
                callback=self.parse,
                cookies=self.cookies,
                meta={"word": word, "page_num": page_num + 1}
            )

        print("over")

    def parse_question_detail(self, response):
        question_item = response.meta["question_item"]
        page_num = response.meta["page_num"]
        # text = response.body
        # dir_name = "./data/" + question_item["search_word"] + "/details"
        # if os.path.exists(dir_name) is False:
        #     os.makedirs(dir_name)
        # file = open(dir_name + "/" + question_item["id"] + "_" + str(page_num) + ".html", "wb")
        # file.write(text)
        # file.close()
        res = json.loads(response.text)
        if res["data"] is not None:
            for item in res["data"]:
                answer_item = {}
                answer_item["author_name"] = item["author"]["name"]
                answer_item["author_type"] = item["author"]["type"]
                answer_item["author_id"] = item["author"]["id"]
                answer_item["author_id"] = item["author"]["id"]
                content = item["content"]
                content = content.replace("<p>", "")
                content = content.replace("</p>", "")
                answer_item["content"] = content
                answer_item["voteup_count"] = item["voteup_count"]
                answer_item["updated_time"] = item["updated_time"]
                question_item["answer"].append(answer_item)
        if res["paging"]["is_end"] is False:
            next_url = res["paging"]["next"]
            yield scrapy.Request(
                next_url,
                dont_filter=True,
                callback=self.parse_question_detail,
                cookies=self.cookies,
                meta={"question_item": question_item, "page_num": page_num + 1}
            )
        else:
            yield question_item





