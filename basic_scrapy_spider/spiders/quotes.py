import json
import scrapy
import re

class LinkedCompanySpider(scrapy.Spider):
    name = "linkedin_company_profile"
    api_url = 'https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=python&location=United%2BStates&geoId=103644278&trk=public_jobs_jobs-search-bar_search-submit&start=' 

    #add your own list of company urls here
    postfixurl = '?trk=public_jobs_jserp-result_job-search-card-subtitle'
    company_pages = [
        'https://in.linkedin.com/company/microsoft'+postfixurl,
        'https://in.linkedin.com/company/twitter'+postfixurl,
        'https://in.linkedin.com/company/google'+postfixurl,
        'https://in.linkedin.com/company/apple'+postfixurl,
        'https://in.linkedin.com/company/ibm'+postfixurl,
        'https://in.linkedin.com/company/amazon-web-services'+postfixurl,
        'https://in.linkedin.com/company/intel-corporation'+postfixurl,
        'https://in.linkedin.com/company/att'+postfixurl,
        'https://in.linkedin.com/company/salesforce'+postfixurl,
        'https://in.linkedin.com/company/oracle'+postfixurl,
    ]


    def start_requests(self):
        
        company_index_tracker = 0

        #uncomment below if reading the company urls from a file instead of the self.company_pages array
        # self.readUrlsFromJobsFile()

        first_url = self.company_pages[company_index_tracker]

        yield scrapy.Request(url=first_url, callback=self.parse_response, meta={'company_index_tracker': company_index_tracker})


    def parse_response(self, response):
        company_index_tracker = response.meta['company_index_tracker']
        print('***************')
        print('****** Scraping page ' + str(company_index_tracker+1) + ' of ' + str(len(self.company_pages)))
        print('***************')

        company_item = {}

        company_item['name'] = response.css('.top-card-layout__entity-info h1::text').get(default='not-found').strip()
        company_item['summary'] = response.css('[data-test-id="about-us__description"]::text').get(default='not-found').strip()

        try:
            ## all company details 
            company_details = response.css('.core-section-container__content .mb-2')

            for ele in company_details:
                
                info = ele.css('.text-md::text').getall()
                title = info[0].strip().replace(" ", "")    
                value = info[1].strip();

                ##if title == "Companysize" :
                    ##value = re.sub("[^0-9]", "", value);
  
                company_item[title] = value;

        except IndexError:
            print("Error: Skipped Company - Some details missing")

        yield company_item
        

        company_index_tracker = company_index_tracker + 1

        if company_index_tracker <= (len(self.company_pages)-1):
            next_url = self.company_pages[company_index_tracker]

            yield scrapy.Request(url=next_url, callback=self.parse_response, meta={'company_index_tracker': company_index_tracker})

    
    def readUrlsFromJobsFile(self):
        self.company_pages = []
        with open('jobs.json') as file:
            jobsFromFile = json.load(file)

            for job in jobsFromFile:
                if job['company_link'] != 'not-found':
                    self.company_pages.append(job['company_link'])
            
        #remove any duplicate links - to prevent spider from shutting down on duplicate
        self.company_pages = list(set(self.company_pages))

    def removeSpace(string):
        return string.replace(" ", "")        