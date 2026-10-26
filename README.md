# Carbon Calculator Backend

## Brief
A FastAPI-driven REST API that handles multi-variable carbon footprint calculations, custom user authentication, and curated environmental data aggregation.

## Deployment Links
* **Backend GitHub:** [https://github.com/sdg877/carbon_calculator_be](https://github.com/sdg877/carbon_calculator_be)

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
* **Consistency:** Used FastAPI's request and response validation to keep endpoints consistent and easy to test.
* **Security:** Implemented custom JWT authentication with bcrypt password hashing, without relying on third-party providers.

## Key Learnings
* **API Design:** Deepened expertise in RESTful principles, specifically regarding secure endpoint protection and status codes.
* **Cloud Infrastructure:** Gained hands-on experience deploying a backend on Render with a hosted PostgreSQL database on Supabase.

## Bugs
* **Rate Limiting:** Managing NewsAPI constraints during concurrent user testing.
* **CORS Headers:** Initial configuration issues between Render (Backend) and Vercel (Frontend) during cross-domain requests (now resolved).

## Future Improvements
* **Microservices:** Decoupling the calculation engine into a standalone service for higher scalability.
* **Testing Suite:** Extending Pytest coverage from the calculation logic to the API endpoints.