# Social Media News Posting Agent Specification

## Overview

This document outlines the specifications for building and deploying a social media posting agent that fetches the latest business and trading-related news and economic calendar events from four sources: [Forex Factory](https://www.forexfactory.com), [Benzinga](https://www.benzinga.com), [Trading Economics](https://www.tradingeconomics.com), and [FastBull](https://www.fastbull.com). The agent processes this data into concise, engaging social media posts and publishes them to specified platforms (e.g., Twitter/X, LinkedIn) every 3-4 hours. The system is designed to be modular, scalable, and reliable, adhering to principles of loose coupling, standardization, and error handling.

**Key Requirements**:
- **Data Sources**: Fetch economic calendar events and news from Forex Factory, Benzinga, Trading Economics, and FastBull.
- **Posting Frequency**: Automated posts every 3-4 hours.
- **Post Content**: Summarize high-impact events/news, e.g., "India’s HSBC Services PMI hits 62.9! 📈 #TradingNews".
- **Platforms**: Twitter/X and LinkedIn (expandable to others).
- **Non-Functional Requirements**: Handle API rate limits, errors, and downtime; ensure data freshness; log activities for monitoring.
- **Assumptions**: The agent runs in a cloud environment (e.g., AWS, Heroku). APIs are preferred; web scraping is a fallback, compliant with each site’s terms of service.

**Analogy**: The agent is like a newsroom with reporters (fetchers) collecting stories from multiple outlets, editors (processors) crafting headlines, and couriers (publishers) delivering them on a regular schedule.

## Architectural Style

**Recommended Style**: Microservices with Event-Driven elements.
- **Rationale**: Enables independent scaling of modules (e.g., fetchers for each source) and asynchronous processing via events, ideal for handling multiple APIs and potential failures.
- **Alternative**: Monolithic for initial simplicity, but refactor to microservices for scalability.
- **Principles**:
  - **Modularity**: Independent modules for fetching, processing, scheduling, and publishing.
  - **Loose Coupling**: Communicate via APIs or message queues (e.g., RabbitMQ).
  - **High Cohesion**: Group related functions within modules.
  - **Scalability**: Support increased data volume or platforms.
  - **Standardization**: Use JSON for data exchange, consistent error codes.

## Modules and Responsibilities

The system comprises five core modules:

1. **Data Fetcher**:
   - **Purpose**: Retrieves economic calendar events and news from Forex Factory, Benzinga, Trading Economics, and FastBull.
   - **Handles**: API calls (preferred) or web scraping; caching for redundancy.
   - **Sources**:
     - **Forex Factory**: Calendar (e.g., USD Non-Farm Employment Change) and news (e.g., “Dollar Rises as US Productivity Strengthens”).[](https://www.forexfactory.com/news)[](https://www.forexfactory.com/calendar/)
     - **Benzinga**: Forex news (e.g., “USD/JPY Analysis: Watch Out Bulls”).[](https://www.benzinga.com/topic/forex)
     - **Trading Economics**: Calendar (e.g., “IN HSBC Services PMI: 62.9”).[](https://www.fastbull.com/calendar)
     - **FastBull**: Calendar and news (e.g., “Vietnam’s Exports Surge”).[](https://www.fastbull.com/news)[](https://www.fastbull.com/express-news)
   - **Output**: Unified JSON data, e.g., `{"source": "FastBull", "event": "IN HSBC Services PMI", "actual": "62.9", "importance": "high"}`.
   - **Interfaces**: Input - Trigger event; Output - Message queue.

2. **Data Processor**:
   - **Purpose**: Filters high-impact events/news; formats into social media posts using templates.
   - **Handles**: Character limits (e.g., 280 for Twitter/X); adding emojis, hashtags.
   - **Example Post**: “🇺🇸 US Non-Farm Employment at 75K, below forecast! 📉 #Forex #TradingEconomics”.
   - **Interfaces**: Input - JSON from queue; Output - Formatted posts to queue.

3. **Scheduler**:
   - **Purpose**: Triggers the workflow every 3-4 hours (e.g., cron `0 */3 * * *`).
   - **Handles**: Timezone adjustments; missed triggers.
   - **Interfaces**: Emits events to Data Fetcher.

4. **Social Media Publisher**:
   - **Purpose**: Posts to Twitter/X and LinkedIn via APIs.
   - **Handles**: OAuth authentication; rate limits; retries.
   - **Interfaces**: Input - Posts from queue; Output - API responses logged.

5. **Monitoring/Logging**:
   - **Purpose**: Tracks metrics (e.g., fetch success rate, post failures).
   - **Tools**: Centralized logging (e.g., ELK Stack, console logs).
   - **Interfaces**: Collects logs from all modules.

## Inter-Module Communication and Integration

- **Communication Flow**:
  - Scheduler → Data Fetcher (event trigger).
  - Data Fetcher → Data Processor (JSON via queue, e.g., RabbitMQ).
  - Data Processor → Social Media Publisher (posts via queue).
  - All modules → Monitoring/Logging (async logs).

- **Integration Details**:
  - **Data Sources**:
    - **Forex Factory**: Use calendar API (if available) or scrape `<table>` elements from the calendar page. Parse news from `/news`.[](https://www.forexfactory.com/calendar/)
    - **Benzinga**: Scrape forex news headlines or use RSS feeds.[](https://www.benzinga.com/topic/forex)
    - **Trading Economics**: Leverage their API for calendar data (XML/JSON).[](https://www.fastbull.com/calendar)
    - **FastBull**: Use API (if provided) or scrape calendar/news sections.[](https://www.fastbull.com/news)[](https://www.fastbull.com/express-news)
  - **Social Media APIs**:
    - Twitter/X: `/2/tweets` endpoint for posts.
    - LinkedIn: `/v2/ugcPosts` for shares.
    - Secure tokens in environment variables.
  - **Error Handling**: Retry with exponential backoff; cache recent data (Redis); alert on persistent failures (e.g., Slack).
  - **Data Standardization**: Unified JSON schema, e.g.:
    ```json
    {
      "source": "string",
      "type": "calendar|news",
      "event": "string",
      "actual": "string",
      "previous": "string",
      "forecast": "string",
      "importance": "high|medium|low",
      "timestamp": "ISO8601",
      "summary": "string"
    }
    ```

## Conceptual Architecture Diagram

Textual representation (visualize in Draw.io):
```
[Scheduler] --(Trigger Event)--> [Data Fetcher]
                          |
                          v
[Forex Factory, Benzinga, Trading Economics, FastBull] <-- [Data Fetcher] --(JSON via Queue)--> [Data Processor]
                                                           |
                                                           v
[Data Processor] --(Formatted Post via Queue)--> [Social Media Publisher] --> [Twitter/X, LinkedIn APIs]
                                                           |
                                                           v
[All Modules] --(Logs)--> [Monitoring/Logging]
```

- **Layers**: Data Access (Fetcher), Business Logic (Processor), Presentation (Publisher), Orchestration (Scheduler).

## Technology Stack Recommendations

- **Languages/Frameworks**: Python (Flask for lightweight services) or Node.js (Express).
- **Tools/Libraries**:
  - **Fetching**: Requests (HTTP), BeautifulSoup/Selenium (scraping), Trading Economics API client.
  - **Queues**: RabbitMQ or Redis.
  - **Scheduling**: APScheduler (Python), node-schedule (Node.js), or cron.
  - **APIs**: Tweepy (Twitter), linkedin-api (LinkedIn).
  - **Logging**: Python logging module, Winston (Node.js).
  - **Caching**: Redis for recent data.
- **Database**: Optional SQLite for caching posts/logs.
- **Environment**: Docker for containerization; Kubernetes for orchestration.

**Dependencies**: List in `requirements.txt` (Python) or `package.json` (Node.js). Avoid runtime internet installs.

## Development and Testing Guidelines

- **Development Steps**:
  1. Develop fetchers for each source (start with Trading Economics API for reliability).
  2. Implement processor with post templates.
  3. Set up scheduler with 3-hour intervals.
  4. Integrate publisher with social media APIs.
  5. Add logging across modules.

- **Testing**:
  - **Unit**: Test fetchers with mock data (e.g., sample JSON from Trading Economics).
  - **Integration**: Simulate full flow (fetch → process → post).
  - **Load**: Test with frequent triggers (e.g., every 10 minutes).
  - **Edge Cases**: Handle API downtime, invalid data, rate limits.

- **Security**: Store API keys in env vars; sanitize inputs; comply with source terms.

## Deployment Steps

**Environment**: Cloud-based (AWS, Heroku, or VPS) for 24/7 uptime.

1. **Prepare Codebase**:
   - Structure: Folders (`/fetcher`, `/processor`, `/publisher`, `/scheduler`).
   - Git repo with README.md mirroring this spec.

2. **Containerization**:
   - Dockerfile per module (e.g., Python: `FROM python:3.9`, install deps, run app).
   - docker-compose.yml for services (fetcher, processor, rabbitmq, etc.).

3. **CI/CD**:
   - GitHub Actions: Lint → Test → Build Docker → Deploy.
   - Ensure automated tests pass before deployment.

4. **Cloud Deployment**:
   - **Heroku**: Push app; set env vars; use Heroku Scheduler.
   - **AWS**:
     - ECS for containers or Lambda for serverless.
     - CloudWatch Events for scheduling.
     - Auto Scaling for load.
   - **Cost**: ~$10-50/month (AWS t3.micro, Heroku dyno).

5. **Configuration**:
   - Env Vars: SOURCE_URLS, TWITTER_API_KEY, LINKEDIN_TOKEN, QUEUE_URL, SCHEDULE_INTERVAL=3h.
   - Monitoring: Prometheus/Grafana or CloudWatch.

6. **Launch and Monitor**:
   - Deploy: `docker-compose up` or cloud commands.
   - Verify: Manual trigger; check first posts.
   - Maintenance: Rotate keys; monitor API changes; ensure uptime.

## Task Schedule

```json
{
  "name": "Social Media News Update",
  "prompt": "Fetch business/trading news and economic calendar events from Forex Factory, Benzinga, Trading Economics, and FastBull. Process into concise posts and publish to Twitter/X and LinkedIn.",
  "cadence": "daily",
  "time_of_day": ["00:00", "03:00", "06:00", "09:00", "12:00", "15:00", "18:00", "21:00"],
  "timezone": "UTC",
  "day_of_week": 1,
  "day_of_month": 1,
  "day_of_year": 1
}
```

## Potential Enhancements

- Sentiment analysis from FastBull chatrooms (e.g., “storm ain’t over yet”).[](https://www.fastbull.com/express-news)
- Support additional platforms (e.g., Facebook).
- Dashboard for manual triggers/logs.
- AI-generated post variations using an LLM.

## Risks and Mitigations

- **Risk**: Scraping blocked by sources. **Mitigation**: Prioritize APIs; cache data; use alternative sources.[](https://fxnewsgroup.com/tag/fastbull/)
- **Risk**: Social media bans for spam. **Mitigation**: Vary post timing/content; follow platform guidelines.
- **Risk**: Downtime. **Mitigation**: Redundant servers; Slack/email alerts.

## References

- Forex Factory: Calendar and news data.[](https://www.forexfactory.com/news)[](https://www.forexfactory.com/calendar/)
- Benzinga: Forex news headlines.[](https://www.benzinga.com/topic/forex)
- Trading Economics: Economic calendar API.[](https://www.fastbull.com/calendar)
- FastBull: Calendar and news.[](https://www.fastbull.com/news)[](https://www.fastbull.com/express-news)

This specification provides a complete blueprint for building and deploying the agent. For implementation, study automation bots on GitHub (e.g., *n8n*). Provide feedback for adjustments.