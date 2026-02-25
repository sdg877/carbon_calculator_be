# Carbon Calculator Backend

## Brief
A robust FastAPI-driven REST API that handles multi-variable carbon footprint calculations, proprietary user authentication, and curated environmental data aggregation.

## Deployment Links
* **Backend GitHub:** [https://github.com/sdg877/carbon_calculator_be](https://github.com/sdg877/carbon_calculator_be)
* **API Deployment:** [Link to Render/Supabase here]

## Timeframe
Developed over six months. Transitioned from a local prototype into a scalable production logic layer for environmental analytics.

## Technologies Used
* **Framework:** FastAPI (Python)
* **Database:** SQLite (Development), Supabase/PostgreSQL (Production)
* **Authentication:** Custom JWT-based session management & Bcrypt hashing
* **Integrations:** NewsAPI
* **Deployment:** Render

## Code Process
* **Analytical Engine:** Engineered core Python logic to process 20+ activity variables (transport, diet, utilities) into standardised carbon metrics.
* **News Proxy:** Developed a dedicated backend route to fetch and filter environmental news, securing the API key and offloading filtering logic from the client.
* **Database Schema:** Designed relational PostgreSQL tables to maintain historical user data, allowing for longitudinal trend tracking.
* **Security Layer:** Built a self-managed authentication system from scratch to ensure full control over user data privacy and session integrity.

## Challenges
* **Database Parity:** Navigating strict relational constraints when migrating from local SQLite files to a cloud-hosted PostgreSQL instance on Supabase.
* **Architecture Pivot:** Re-engineering the data flow to support a proxy news engine after identifying a lack of production-ready volunteering APIs.

## Wins
* **Performance:** Leveraged FastAPI’s asynchronous capabilities to ensure low-latency responses for complex calculation queries.
* **Security:** Successfully implemented a custom, production-ready authentication flow without relying on third-party providers.

## Key Learnings
* **API Design:** Deepened expertise in RESTful principles, specifically regarding secure endpoint protection and status codes.
* **Cloud Infrastructure:** Mastered the deployment and management of serverless databases and automated backend hosting.

## Bugs
* **Rate Limiting:** Managing NewsAPI constraints during concurrent user testing.
* **CORS Headers:** Initial configuration issues between Render (Backend) and Vercel (Frontend) during cross-domain requests (now resolved).

## Future Improvements
* **Microservices:** Decoupling the calculation engine into a standalone service for higher scalability.
* **Testing Suite:** Implementing comprehensive Pytest coverage for all calculation logic and API endpoints.
