from browser_use.llm import ChatOpenAI
from browser_use import Agent
from dotenv import load_dotenv
load_dotenv()

import asyncio

llm = ChatOpenAI(model="gpt-4o")

async def main():
    agent = Agent(
        task='''go to this url"https://iprsearch.ipindia.gov.in/PublicSearch/PublicationSearch/ApplicationStatus" and check the status of this application numbers 202421104611,202521021759 and take a screenshot of the status
    ''',
        llm=llm,
    )
    result = await agent.run()
    print(result)

asyncio.run(main())