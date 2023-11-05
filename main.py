
import argparse
parser = argparse.ArgumentParser(description="Service Runner")
parser.add_argument("service_name", help="Name of the service", type=str)

args = parser.parse_args()
service_name = args.service_name.lower()

print(f"Running service: {service_name}")

if service_name == "urlscraper":
    
    from Services.UrlScraper import UrlScraper
    service = UrlScraper()
    service.start()

elif service_name =="api":
    from Services.API.app import API
    service = API()
    service.start()
else:
    print(f"Service {service_name} not found")



