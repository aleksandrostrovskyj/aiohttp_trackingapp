import io
import json
import asyncio
import aiohttp
from db import package
from utils import Services
from settings import config
from datetime import datetime
import xml.etree.ElementTree as ET
from sqlalchemy.sql.expression import select


class UpsTracktor:
    """
    Class for UPS tracking numbers information gathering
    """
    def __init__(self):
        self.url = 'https://www.ups.com/track/api/Track/GetStatus?loc=en_US'
        self.body = {
            'Locale': 'en_US',
            'Requester': 'wt/trackdetails'
        }
        self.headers = {
            'accept': "application/json, text/plain, */*",
            'content-type': "application/json",
        }

    @staticmethod
    def prepare_result(response: json):
        return [
            (
                package['trackingNumber'],
                package['packageStatus'],
                datetime.now()
            )
            for package in response['trackDetails']
        ]

    async def fetch_data(self, tracking_numbers: list):
        """
        Retrieve data about tracking's from UPS web-site
        :param tracking_numbers: list of strings
        :return: request.response object (response body is json-like data)
        """
        if not tracking_numbers:
            return []

        async with aiohttp.ClientSession() as session:
            self.body.update(dict(TrackingNumber=tracking_numbers))
            async with session.post(url=self.url, data=str(self.body), headers=self.headers) as response:
                assert response.status == 200
                data = await response.json()
                return self.prepare_result(data)


class UspsTracktor:
    """
    Class for USPS tracking numbers information gathering
    Use official API:
        https://www.usps.com/business/web-tools-apis/#api
    """
    def __init__(self, user_id: str):
        """
        :param user_id: user id from Web Tools API(free registration)
        """
        self.user_id = user_id
        self.url = 'http://production.shippingapis.com/ShippingAPI.dll'
        self.params = {
            'API': 'TrackV2'
        }

    def build_xml(self, tracking_numbers):
        """
        Method to build xml for the request(according API documentation)
        :return: xml string
        """
        builder = ET.TreeBuilder()
        builder.start('TrackRequest', {'USERID': self.user_id})    # start root node

        for tracking_number in tracking_numbers:              # add node with each tracking number
            builder.start('TrackID', {'ID': tracking_number})
            builder.end('TrackID')

        builder.end("TrackRequest")                                # close root node
        root = builder.close()                                     # close builder

        temp_buffer = io.BytesIO()                                 # create byte stream buffer
        ET.ElementTree.write(ET.ElementTree(root), temp_buffer, xml_declaration=True, encoding="UTF-8",
                             short_empty_elements=False)           # Write full built xml to the temp_buffer

        return temp_buffer.getvalue().decode('utf-8')

    @staticmethod
    def prepare_result(response: 'xml'):
        root = ET.fromstring(response)
        return [
            (
                package.attrib['ID'],
                package.find('./TrackSummary').text,
                datetime.now()
            )
            for package in root
        ]

    async def fetch_data(self, tracking_numbers: list):
        """
        Retrieve data about tracking's from UPS web-site
        :param tracking_numbers: list of strings
        :return: request.response object (response body is json-like data)
        """
        if not tracking_numbers:
            return []

        async with aiohttp.ClientSession() as session:
            self.params['XML'] = self.build_xml(tracking_numbers)
            async with session.post(url=self.url, params=self.params) as response:
                assert response.status == 200
                return self.prepare_result(await response.text())


async def main(app, background=True):
    ups = UpsTracktor()
    usps = UspsTracktor(config['usps']['userid'])
    while True:
        async with app['db'].acquire() as conn:
            cursor = await conn.execute(
                select(
                    [
                        package.c.tracking_number,
                        package.c.service_name
                    ]
                )
            )
            records = await cursor.fetchall()

        ups_trackings = [each[0] for each in records if each[1] == Services.UPS]
        usps_trackings = [each[0] for each in records if each[1] == Services.USPS]

        ups_task = asyncio.create_task(ups.fetch_data(ups_trackings))
        usps_task = asyncio.create_task(usps.fetch_data(usps_trackings))
        data = await asyncio.gather(ups_task, usps_task)

        clear_data = []
        for each in data:
            clear_data.extend(each)

        async with app['db'].acquire() as conn:
            for each in clear_data:
                await conn.execute(

                    package.update(
                    ).where(
                        package.c.tracking_number == each[0]
                    ).values(
                        status_text=each[1],
                        status_date=each[2]
                    )

                )
                await conn.execute('commit')

        if background:
            await asyncio.sleep(2400)
            continue
        else:
            break


async def start_background_tasks(app):
    app['parse_trackings'] = asyncio.create_task(main(app))
