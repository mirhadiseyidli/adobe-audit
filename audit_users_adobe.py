import asyncio
import aiohttp
import json
import logging
import csv

from okta.client import Client as OktaClient
from okta import models

class GetAdobeUserStatus:
    def __init__(self, config_file):
        # Load configuration from a JSON file
        config = json.load(open(config_file))
        # Connect to Okta
        self.okta_client = OktaClient({
            'orgUrl': config['okta_org_url'],
            'token': config['okta_token']
        })

    async def fetch(self, config_file, url):
        try:
            with open(config_file, 'r') as file:
                config = json.load(file)
            headers = {
                "Content-Type": "application/json",
                'X-Api-Key': config['CLIENT_ID'],
                'Authorization': 'Bearer ' + config['ACCESS_TOKEN']
            }
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(url) as response:
                    response_text = await response.text()
                    if response.status != 200:
                        # Log error response
                        logging.error(f"Error response {response.status}: {response_text}")
                        return {"error": response.status, "message": response_text}
                    return response_text
        except Exception as e:
            logging.error(f"An exception occurred: {e}")
            return {"error": "exception", "message": str(e)}

    def extract_emails(self, response_text):
        if "error" in response_text:
            return []
        users = json.loads(response_text)
        emails = [user['email'] for user in users]
        return emails

    async def check_users_status(self, config_file, urls):
        all_data = []
        for product_name, single_url in urls.items():
            print(f"\nProduct: ADOBE {product_name.replace('_URL', '').replace('_', ' ')}")
            response_text = await self.fetch(config_file, single_url)
            if "error" in response_text:
                print(f"Failed to fetch data for {product_name}. Error: {response_text['message']}")
                continue
            emails = self.extract_emails(response_text)
            if len(emails) == 0:
                print("No Users Are Currently Assigned to This Application")
            else:
                i = 1
                print(f"{'No.':<5} {'USERNAME':<35} {'Status'}")
                for user_email in emails:
                    try:
                        self.user, _, _ = await self.okta_client.get_user(user_email)
                        print(f"{i:<5} {user_email:<35} {self.user.status}")
                        all_data.append(['ADOBE ' + product_name.replace('_URL', '').replace('_', ' '), i, user_email, self.user.status])
                        i += 1
                    except Exception as e:
                        print(f"{i:<5} {user_email:<35} Error 404: User Not Found")

        with open('user_statuses.csv', 'w', newline='') as csvfile:
            fieldnames = ['Product', 'No.', 'Username', 'Status']
            writer = csv.writer(csvfile)
            writer.writerow(fieldnames)
            writer.writerows(all_data)

async def main():
    config_file = 'usermanagement.json'
    config = json.load(open(config_file))
    status_check = GetAdobeUserStatus(config_file)
    await status_check.check_users_status(config_file, config['URLS'])

# Run the main function
if __name__ == "__main__":
    asyncio.run(main())
