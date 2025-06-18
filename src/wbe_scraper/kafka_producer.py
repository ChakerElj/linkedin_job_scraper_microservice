from kafka import KafkaProducer 
import logging
import os

# Configure logging 
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class KafkaProducerClient:
    def __init__(self, bootstrap_servers=None):
        if bootstrap_servers is None:
            bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
        logging.info(f"Initializing Kafka producer with bootstrap servers: {bootstrap_servers}")
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            key_serializer= lambda k: k.encode('utf-8') if isinstance(k, str) else k,
            value_serializer=lambda v: v.encode('utf-8') if isinstance(v, str) else v
        )
        self.collect_jobs_data = []
        
    
    def produce_message(self):
        """Produce a message to kafka topic."""
        if (len(self.collect_jobs_scraped_data) > 0):
            i = 0
            for job in self.collect_jobs_scraped_data:
                # this is the jobs_data structure [{'job_title': 'Product Manager', 'company_nam': 'Yassir', 'company_link': 'https://www.linkedin.com/company/yassir?trk=public_jobs_jserp-result_job-search-card-subtitle', 'pageNum': 1, 'keywords': 'Product Manager', 'geoId': '102134353'}
                logging.info(f"Producing message to topic jobs_topic with key {job['job_id']} and value {job}")
                try:
                    future=self.producer.send(
                        topic="jobs_topic",
                        key=job['job_id'],
                        value=str(job)
                    )
                    record_metadata = future.get(timeout=10)
                    logging.info(f"Message sent to topic {record_metadata.topic} partition {record_metadata.partition} ")
                except Exception as e:
                    logging.error(f"Failed to send message: {e}")
    def finalize(self):
        """Finalize the producer by flushing and closing it."""
        if self.producer:
            self.producer.flush()
            self.producer.close()
            logging.info("Kafka producer finalized ")
    
    def collect_jobs_scraped_data(self,jobs_data):
        """Collect jobs scraped data."""
        if jobs_data:
            self.collect_jobs_scraped_data = jobs_data
            return self.collect_jobs_scraped_data
        return self.collect_jobs_scraped_data