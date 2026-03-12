# BEACON
## AI-Powered Customer Health Scoring for B2B SaaS

**Product Spec v0.1 — Driftwood Labs**

---

## 01 POSITIONING

### The Pitch
Beacon is a customer health scoring platform for B2B SaaS companies. It connects to your existing tools, analyzes customer behavior, and tells you which accounts are about to churn before they do. Customer success teams use it to prioritize outreach and reduce churn.

### The Headline
"Know which customers are about to leave before they do."

### The Market Gap
Most CS teams are flying blind. They check in with customers on a schedule, not based on actual signals. By the time a customer says they're leaving, it's usually too late. Beacon gives CS teams a real-time health score for every account, based on actual product usage, support activity, and engagement data.

---

## 02 TARGET CUSTOMER

### Primary
Customer success managers at B2B SaaS companies with 50-500 customers. Company ARR between $1M and $20M. They have a CS team of 2-8 people. They're using Salesforce or HubSpot but find it inadequate for tracking actual customer health.

### Not the Target
- Consumer apps
- Companies with fewer than 50 customers (they know every customer personally)
- Enterprise CS teams with existing dedicated tooling (Gainsight, Totango)

---

## 03 CORE FEATURES

### Health Score Engine
Each customer account gets a health score from 0-100. The score is calculated from weighted signals across four categories:

- **Product Usage** (40%) — DAU/MAU ratio, feature adoption, session frequency
- **Support Activity** (20%) — open tickets, CSAT scores, ticket volume trend
- **Engagement** (25%) — QBR attendance, email open rates, champion responsiveness
- **Commercial** (15%) — days until renewal, expansion history, contract value trend

Weights are configurable per company.

### Alert System
When a score drops below a configurable threshold, the assigned CSM gets an alert. Alerts go to Slack or email.

### Integrations
- Salesforce (CRM data)
- HubSpot (CRM data)
- Intercom (support tickets)
- Mixpanel (product usage)
- Segment (product usage)
- Gmail (engagement signals)

### Dashboard
A list view of all accounts sorted by health score. CSMs see their assigned accounts. Managers see all accounts. Clicking an account shows the score breakdown and recent signal history.

---

## 04 PRICING

| Plan | Price | Accounts | Users |
|------|-------|----------|-------|
| Starter | $299/mo | Up to 100 | 3 |
| Growth | $599/mo | Up to 300 | 10 |
| Scale | $999/mo | Unlimited | Unlimited |

Annual discount: 20% off.

---

## 05 TECHNICAL ARCHITECTURE

### Stack
- Backend: Node.js + Express
- Database: PostgreSQL
- Queue: Bull (Redis)
- Frontend: React + Tailwind
- Hosting: AWS

### Data Pipeline
Integrations sync on a schedule. Usage data comes in via webhooks where available, polling otherwise. Scores are recalculated nightly.

### Score Calculation
A weighted average of normalized signals. Each signal is normalized to 0-100 before weighting. The final score is the weighted sum.

---

## 06 GO TO MARKET

### Launch Plan
1. Beta with 10 design partners
2. Product Hunt launch
3. Content marketing — blog posts about churn prevention
4. Cold outreach to CS leaders on LinkedIn

### Pricing Strategy
Start low to get customers, raise prices later.

---

## 07 RISKS

- Integrations are hard to build and maintain
- Health scores might not actually predict churn
- Competition from Gainsight is significant
- Hard to get customers to trust an automated score

---

## 08 OPEN QUESTIONS

- Which integration should we build first?
- Should we offer a free trial?
- How do we validate the scoring model?
