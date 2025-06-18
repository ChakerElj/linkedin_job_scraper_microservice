import scrapy
from urllib.parse import urlencode

class LinkedInJobSpider(scrapy.Spider):
    name = "linkedin_job_spider"
    custom_settings = {
        'DUPEFILTER_DEBUG': True
    }
    def __init__(self,data_callback=None, *args, **kwargs):
        super(LinkedInJobSpider, self).__init__(*args, **kwargs)
        self.all_collected_jobs = [] # Initialize list to store all jobs
        self.data_callback = data_callback  # Callback to handle scraped data

    def start_requests(self):
        base_query_params = {
            'geoId': '102134353',
            'keywords': 'Devops engineer', 
        }
        self.current_start = 0
        initial_start = 0
        query_params = {**base_query_params,'start': str(initial_start)}
        starting_url_base = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
        starting_url=f"{starting_url_base}?{urlencode(query_params)}"
        yield scrapy.Request(url=starting_url, 
                             callback=self.parse, 
                             meta={
                                    'start': initial_start,
                                    'keywords': base_query_params['keywords'], # Pass keywords
                                    'geoId': base_query_params['geoId'], # Pass geoId
                           
                      })  

    def parse(self, response):
        current_start = response.meta['start']
        keywords = response.meta['keywords']
        geoId = response.meta['geoId']
        pageNum = 1
        self.logger.info(f"Parsing page with start={self.current_start} and URL: {response.url}")
        html_file= "jobs.html"
        jobs_cards = response.css('.base-card')
        job_ids = jobs_cards.css('::attr(data-entity-urn)').extract()
        print(f"Job IDs: {job_ids}")
        company_infos = response.css('.base-search-card__subtitle > a')
        job_titles_on_pages = [title.strip() for title in jobs_cards.css('a > .sr-only::text').extract()]
        job_company_names = [company.strip() for company in company_infos.css('::text').extract()]
        job_company_links = [company for company in company_infos.css('::attr(href)').extract() ]
        for i in range(0, len(jobs_cards)):
            data = {
                'job_id': job_ids[i].split(':')[3],
                'job_title': job_titles_on_pages[i],
                'company_name': job_company_names[i],
                'company_link': job_company_links[i],
                'pageNum': pageNum,
                'keywords': keywords,
                'geoId': geoId
            }
            self.all_collected_jobs.append(data)
        
        if (job_titles_on_pages):
            self.logger.info(f"Found {len(job_titles_on_pages)} job titles on page (start={self.current_start}): {job_titles_on_pages}")
           
           
            next_start = current_start + 25
            pageNum += 1
            paginating_query_params = {
                'keywords': keywords,
                'geoId': geoId,
                'start': str(next_start),  
            }

            next_page_url_base = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
            next_page_url = f"{next_page_url_base}?{urlencode(paginating_query_params)}"
            self.logger.info(f"Yielding request for next page: {next_page_url}")
            yield scrapy.Request(url=next_page_url,  callback=self.parse, meta={'start': next_start, 'keywords': keywords, 'geoId': geoId})

        else:
            self.logger.info(f"No job titles found on page with start={self.current_start}. Stopping pagination for this path.")

    def closed(self,reason):
        self.logger.info(f"Spider finished. Reason: {reason}")
        self.logger.info(f"Spider finished. Total unique jobs: {len(self.all_collected_jobs)}")
        self.logger.info(f"Jobs: {list(self.all_collected_jobs)}")
        if self.data_callback:
            self.data_callback(self.all_collected_jobs)
       
        return self.all_collected_jobs  
       

       
    