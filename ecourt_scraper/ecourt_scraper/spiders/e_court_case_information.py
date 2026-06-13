import scrapy
import re
import json
from scrapy import Selector
import ast
import os

class ECourtCaseInformationSpider(scrapy.Spider):
    name = "e_court_case_information"

    custom_settings = {
        "CONCURRENT_REQUESTS": 1,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
        "DOWNLOAD_DELAY": 2,
    }

    def __init__(self, cases=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        print("\nRAW CASES:")
        print(cases)


        if cases:
            try:
                self.cases = json.loads(cases)
            except Exception:
                self.cases = ast.literal_eval(cases)
        else:
            self.cases = [{
                "type": "MACT",
                "type_code": "12^1",
                "number": "1760",
                "year": "2016",
                "state_code": "26",
                "district_code": "2",
                "court_complex_code": "1260002",
                "establishment_code": "1"
            }]
        self.results = []

        print(json.dumps(self.cases, indent=4))

    async def start(self):

        first_case = self.cases[0]

        yield scrapy.Request(
            url="https://services.ecourts.gov.in/ecourtindia_v6/?p=casestatus/index&app_token=",
            callback=self.get_captcha,
            meta={
                "case_data": first_case,
                "case_index": 0
            },
            dont_filter=True
        )

    
    def get_captcha(self, response):

        case_data = response.meta["case_data"]

        case_index = response.meta["case_index"]

        yield scrapy.FormRequest(
            url="https://services.ecourts.gov.in/ecourtindia_v6/?p=casestatus/getCaptcha",
            formdata={
            "ajax_req": "true",
            "app_token": ""
        },
        callback=self.parse_captcha,
        meta={
            "case_data": case_data,
            "case_index": case_index
        },
        dont_filter=True
    )



    def save_captcha(self, response):

        case_data = response.meta["case_data"]

        case_index = response.meta["case_index"]

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
            "state_code": str(case_data["state_code"]),
            "dist_code": str(case_data["district_code"]),
            "court_complex_code": str(case_data["court_complex_code"]),
            "est_code": str(case_data["establishment_code"]),
            "case_type": str(case_data["type_code"]),
            "search_case_no": str(case_data["number"]),
            "case_no": str(case_data["number"]),
            "rgyear": str(case_data["year"]),
            "case_captcha_code": str(captcha),
            "ajax_req": "true",
            "app_token": ""
        },          
        callback=self.parse_case,
        meta={
            "case_data": case_data,
            "case_index": case_index
        },
        dont_filter=True
    )



    def parse_captcha(self, response):

        case_data = response.meta["case_data"]

        case_index = response.meta["case_index"]

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
            "case_data": case_data,
            "case_index": case_index
        },
        dont_filter=True
    )

    def parse_case(self, response):


        print("="*100)
        print(response.text[:5000])
        print("="*100)

        with open("case_response.html", "w", encoding="utf-8") as f:
            f.write(response.text)


        data = json.loads(response.text)

        case_index = response.meta["case_index"]

        html = data.get("case_data", "")

        print("HTML LENGTH:", len(html))
        print(html[:3000])
    

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
            callback=self.parse_history,
            meta={
                "case_index": case_index
            },
            dont_filter=True
        )


    def parse_history(self, response):

        data = json.loads(response.text)

        html = data.get("data_list", "")

        os.makedirs("documents", exist_ok=True)


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

        filing_number = selector.xpath(
            "//th[contains(text(),'Filing Number')]/following-sibling::td[1]/text()"
        ).get(default="").strip()

        filing_date = selector.xpath(
            "//th[contains(text(),'Filing Date')]/following-sibling::td[1]/text()"
        ).get(default="").strip()

        registration_number = selector.xpath(
            "//th[contains(text(),'Registration Number')]/following-sibling::td[1]/text()"
        ).get(default="").strip()

        registration_date = selector.xpath(
            "//th[contains(text(),'Registration Date')]/following-sibling::td[1]/text()"
        ).get(default="").strip()


        first_hearing_date = selector.xpath(
            "//th[contains(text(),'First Hearing Date')]/following-sibling::td/text()"
        ).get(default="").strip()

        decision_date = selector.xpath(
            "//th[contains(text(),'Decision Date')]/following-sibling::td/text()"
        ).get(default="").strip()

        nature_of_disposal = selector.xpath(
            "//td[contains(.,'Nature of Disposal')]/following-sibling::td/strong/text()"
        ).get(default="").strip()

        court_and_judge = selector.xpath(
            "//th[contains(text(),'Court Number and Judge')]/following-sibling::td/strong/text()"
        ).get(default="").strip()

        petitioner = selector.xpath(
            "//h3[contains(text(),'Petitioner')]/following-sibling::ul/li/text()"
        ).get(default="").strip()

        respondent = selector.xpath(
            "//h3[contains(text(),'Respondent')]/following-sibling::ul/li/text()"
        ).get(default="").strip()

        act = selector.xpath(
            "//table[@id='act_table']//tr[2]/td[1]/text()"
        ).get(default="").strip()

        section = selector.xpath(
            "//table[@id='act_table']//tr[2]/td[2]/text()"
        ).get(default="").strip()

        case_info = {
            "case_type": case_type,
            "filing_number": filing_number,
            "filing_date": filing_date,
            "registration_number": registration_number,
            "registration_date": registration_date,
            "cnr": cnr,
            "first_hearing_date": first_hearing_date,
            "decision_date": decision_date,
            "status": status,
            "nature_of_disposal": nature_of_disposal,
            "court_and_judge": court_and_judge,
            "petitioner": petitioner,
            "respondent": respondent,
            "act": act,
            "section": section,
            "history": [],
            "documents": []
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

        pdf_links = selector.xpath(
            "//a[contains(@onclick,'displayPdf')]"
        )

        print("\nTOTAL PDFS =", len(pdf_links))

        for index, pdf in enumerate(pdf_links, start=1):

            document_name = pdf.xpath(
                "normalize-space(.)"
            ).get()

            onclick = pdf.xpath("@onclick").get()


            match = re.search(
                 r"displayPdf\('([^']*)','([^']*)','([^']*)','([^']*)','([^']*)'\)",
                onclick
            )

            if match:

                normal_v = match.group(1)
                case_val = match.group(2)
                court_code = match.group(3)
                filename = match.group(4)
                app_token = match.group(5)


            yield scrapy.FormRequest(
                url="https://services.ecourts.gov.in/ecourtindia_v6/?p=home/display_pdf",
                formdata={
                        "normal_v": normal_v,
                        "case_val": case_val,
                        "court_code": court_code,
                        "filename": filename,
                        "appFlag": "",
                        "ajax_req": "true",
                        "app_token": app_token
                    },
                    callback=self.save_pdf,
                    meta={
                        "document_name": document_name,
                        "pdf_index": index
                    },
                    dont_filter=True
                )

            case_info["documents"].append({
                "name": document_name
            })

        self.results.append(case_info)

        with open(
            "output.json",
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                self.results,f,
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


        case_index = response.meta.get("case_index", 0)

        next_index = case_index + 1

        if next_index < len(self.cases):

            next_case = self.cases[next_index]

            yield scrapy.Request(
                url="https://services.ecourts.gov.in/ecourtindia_v6/?p=casestatus/index&app_token=",
                callback=self.get_captcha,
                meta={
                    "case_data": next_case,
                    "case_index": next_index
                },
                dont_filter=True
            )


    def save_pdf(self, response):

        document_name = response.meta["document_name"]
        pdf_index = response.meta["pdf_index"]


        print(f"\nPDF RESPONSE RECEIVED: {document_name}")

        pdf_data = json.loads(response.text)

        pdf_path = pdf_data.get("order")



        pdf_url = (
            "https://services.ecourts.gov.in/ecourtindia_v6/"+ pdf_path)


        yield scrapy.Request(
            url=pdf_url,
            callback=self.download_actual_pdf,
            meta={
                "pdf_index": pdf_index,
                "document_name": document_name
            },
            dont_filter=True,
            priority=1000
        )

        return

    def download_actual_pdf(self, response):

        pdf_index = response.meta["pdf_index"]

        print("CONTENT TYPE =", response.headers.get("Content-Type"))

        with open(
            f"documents/document_{pdf_index}.pdf",
            "wb"
        ) as f:
            f.write(response.body)

        print(
            f"ACTUAL PDF SAVED -> documents/document_{pdf_index}.pdf"
        )