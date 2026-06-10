import scrapy
import re
import json
from scrapy import Selector
class ECourtCaseInformationSpider(scrapy.Spider):
    name = "e_court_case_information"

    async def start(self):

        case_data = {
            "type": "MACT",
            "type_code": "12^1",
            "number": "1760",
            "year": "2016",
            "state_code": "26",
            "district_code": "2",
            "court_complex_code": "1260002",
            "establishment_code": "1"
        }

        yield scrapy.Request(
            url="https://services.ecourts.gov.in/ecourtindia_v6/?p=casestatus/index&app_token=",
            callback=self.get_captcha,
            meta={
                "case_data": case_data
        },
        dont_filter=True
    )


    
    def get_captcha(self, response):

        case_data = response.meta["case_data"]

        yield scrapy.FormRequest(
            url="https://services.ecourts.gov.in/ecourtindia_v6/?p=casestatus/getCaptcha",
            formdata={
            "ajax_req": "true",
            "app_token": ""
        },
        callback=self.parse_captcha,
        meta={
            "case_data": case_data
        }
    )



    def save_captcha(self, response):

        case_data = response.meta["case_data"]

        with open("captcha.jpg", "wb") as f:
            f.write(response.body)

        print("\n" + "=" * 80)
        print("CAPTCHA SAVED -> captcha.jpg")
        print("Open captcha.jpg and enter text")
        print("=" * 80)

        captcha = input("Enter Captcha: ")

        yield scrapy.FormRequest(
        url="https://services.ecourts.gov.in/ecourtindia_v6/?p=casestatus/submitCaseNo",
        formdata={
            "state_code": case_data["state_code"],
            "dist_code": case_data["district_code"],
            "court_complex_code": case_data["court_complex_code"],
            "est_code": case_data["establishment_code"],
            "case_type": case_data["type_code"],
            "search_case_no": case_data["number"],
            "case_no": case_data["number"],
            "rgyear": case_data["year"],
            "case_captcha_code": captcha,
            "ajax_req": "true",
            "app_token": ""
        },
        callback=self.parse_case,
        meta={
            "case_data": case_data
        }
    )



    def parse_captcha(self, response):

        case_data = response.meta["case_data"]

        match = re.search(
            r'src=\\"([^"]*securimage_show\.php[^"]*)\\"',
            response.text
        )

        if not match:
            print("CAPTCHA IMAGE URL NOT FOUND")
            return

        captcha_url = match.group(1)

        captcha_url = captcha_url.replace("\\/", "/")

        captcha_url = response.urljoin(captcha_url)

        print("=" * 80)
        print("CAPTCHA URL:")
        print(captcha_url)
        print("=" * 80)

        yield scrapy.Request(
        captcha_url,
        callback=self.save_captcha,
        meta={
            "case_data": case_data
        },
        dont_filter=True
    )

    def parse_case(self, response):

        data = json.loads(response.text)

        html = data.get("case_data", "")

        match = re.search(
            r"viewHistory\((.*?)\)",
            html
        )

        if not match:
            print("VIEW HISTORY NOT FOUND")
            return

        params = match.group(1)

        print("\n" + "=" * 100)
        print("VIEW HISTORY PARAMS:")
        print(params)
        print("=" * 100)

        values = [x.strip().replace("'", "") for x in params.split(",")]

        case_no = values[0]
        cino = values[1]
        court_code = values[2]
        search_flag = values[4]
        state_code = values[5]
        dist_code = values[6]
        court_complex_code = values[7]
        search_by = values[8]

        yield scrapy.FormRequest(
            url="https://services.ecourts.gov.in/ecourtindia_v6/?p=home/viewHistory",
            formdata={
                "court_code": court_code,
                "state_code": state_code,
                "dist_code": dist_code,
                "court_complex_code": court_complex_code,
                "case_no": case_no,
                "cino": cino,
                "hideparty": "",
                "search_flag": search_flag,
                "search_by": search_by,
                "ajax_req": "true",
                "app_token": ""
            },
            callback=self.parse_history
        )


    def parse_history(self, response):

        data = json.loads(response.text)

        html = data.get("data_list", "")


        print("\n" + "=" * 100)
        print("HISTORY RESPONSE RECEIVED")
        print("=" * 100)

        #print(response.text[:10000])

        with open(
            "history_.html",
            "w",
            encoding="utf-8"
        ) as f:
            f.write(html)

        

        selector = Selector(text=html)

        case_type = selector.xpath(
            "//th[contains(text(),'Case Type')]/following-sibling::td/text()"
        ).get()

        cnr = selector.xpath(
            "//span[contains(@class,'text-danger')]/text()"
        ).get()

        print("\nCASE TYPE:", case_type)
        print("CNR:", cnr)

        
        
        status = selector.xpath(
            "//td[@headers='cs3']/strong/text()"
        ).get()

        print("STATUS:", status)

        case_info = {
            "case_type": case_type,
            "cnr": cnr,
            "status": status,
            "history": []
        }

        rows = selector.xpath(
            "//table[contains(@class,'history_table')]//tr"
        )

        previous_judge = ""
        
        for row in rows:

            judge = " ".join(row.xpath("./td[1]//text()").getall()).strip()

            if not judge:
                judge = previous_judge
            else:
                previous_judge = judge

            business_date = row.xpath("./td[2]//text()").get(default="").strip()

            hearing_date = row.xpath("./td[3]//text()").get(default="").strip()

            purpose = row.xpath("./td[4]//text()").get(default="").strip()

            # print(
            #     judge,
            #     business_date,
            #     hearing_date,
            #     purpose
            # )

            case_info["history"].append({
                "judge": judge,
                "business_date": business_date,
                "hearing_date": hearing_date,
                "purpose": purpose
            })

        with open(
            "output.json","w", encoding="utf-8") as f:
                json.dump(
                case_info,
                f,
                indent=4,
                ensure_ascii=False
                )

        print("\nOUTPUT.JSON SAVED")

        # print(
        #     json.dumps(
        #     case_info,
        #     indent=4,
        #     ensure_ascii=False
        #     )
        # )

        print("HISTORY SAVED")