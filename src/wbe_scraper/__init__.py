
import kafka
from scrapy.crawler import CrawlerProcess
from linkedin_job_scraper import LinkedInJobSpider

from langchain_openai import AzureChatOpenAI
from dotenv import load_dotenv

from kafka_producer import KafkaProducerClient


# load environment variables from .env file
# load_dotenv()
# Initialize the AzureChatOpenAI model

# agentScraper= AgentScraper(llm=llm)
kafkaJobProducer = KafkaProducerClient()

#  pass the scrapped jobs data to the agent company website scraper 
def handle_scraped_jobs(jobs_data):
    """Callback function to handle scraped data jobs"""
    if jobs_data:

        kafkaJobProducer.collect_jobs_scraped_data(jobs_data)
        print("Kafka producer initialized with scraped jobs data. :", jobs_data)
        kafkaJobProducer.produce_message()
        kafkaJobProducer.finalize()
      


def run_scrapping_pipeline():
    """Run the complete linkedin job scraping pipeline"""
    # crawl process for LinkedIn job scraping
    process=CrawlerProcess()
    process.crawl(LinkedInJobSpider,data_callback=handle_scraped_jobs)
    process.start()


run_scrapping_pipeline()