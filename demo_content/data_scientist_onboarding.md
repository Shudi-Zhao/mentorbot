# Data Scientist Onboarding Guide
## Welcome to DataCo Analytics Team! 🎉

Congratulations on joining DataCo as a Junior Data Scientist! This guide will help you navigate your first few months and answer common questions you might have.

---

## Your Role: Junior Data Scientist

### Position Overview
As a Junior Data Scientist on the Analytics Team, you'll work on building predictive models, analyzing experiments, and creating insights that drive product decisions. You'll collaborate closely with Product, Engineering, and Business teams to turn data into actionable recommendations.

### Your Responsibilities
- Build and maintain machine learning models for customer behavior prediction
- Analyze A/B test results and provide statistical recommendations
- Create dashboards and reports for stakeholders
- Document your work and share knowledge with the team
- Participate in code reviews and team knowledge sharing
- Support senior team members on larger projects

### Success Metrics (First 90 Days)
- Complete onboarding checklist within first 2 weeks
- Ship first dashboard/report by end of month 1
- Contribute to at least 2 A/B test analyses by month 2
- Present findings in weekly Data Review meeting by month 3

---

## Your Team

### Direct Team Members

**Sarah Chen** - Senior Data Science Manager
- Email: sarah.chen@dataco.com
- Slack: @sarah.chen
- Role: Your direct manager, handles 1:1s, performance reviews, career development
- Office Hours: Tuesdays 2-4pm, Thursdays 10am-12pm

**Michael Torres** - Senior Data Scientist
- Email: michael.torres@dataco.com
- Slack: @mtorres
- Role: Your mentor, technical lead for customer analytics projects
- Expertise: Machine learning, Python, SQL, customer segmentation

**Priya Patel** - Analytics Engineer
- Email: priya.patel@dataco.com
- Slack: @priya.p
- Role: Data pipeline development, data modeling
- Go-to for: Data warehouse questions, ETL issues, data quality

**David Kim** - Junior Data Scientist (Peer)
- Email: david.kim@dataco.com
- Slack: @dkim
- Role: Joined 3 months ago, working on recommendation systems
- Great resource for: Navigating first months, internal processes

### Cross-Functional Partners

**Product Team**
- **James Liu** - Product Manager (Customer Growth)
  - Email: james.liu@dataco.com
  - Works with you on: Growth experiments, feature analytics

- **Emma Rodriguez** - Product Manager (Engagement)
  - Email: emma.rodriguez@dataco.com
  - Works with you on: User engagement features, retention analysis

**Engineering Team**
- **Alex Johnson** - Engineering Lead
  - Email: alex.johnson@dataco.com
  - Contact for: Model deployment, API integration, production issues

**Business Intelligence Team**
- **Lisa Wang** - BI Analyst Lead
  - Email: lisa.wang@dataco.com
  - Contact for: Dashboard design best practices, Tableau support

---

## Key Contacts & Escalation Paths

### Who to Contact For What

**Data Access Requests**
- Channel: #data-requests on Slack
- Process: Submit ticket via Slack workflow
- Approval Time: 1-2 business days
- Contact: Priya Patel for urgent requests

**IT Support**
- Email: it-help@dataco.com
- Slack: #it-support
- For: Laptop issues, software installation, VPN access

**HR Questions**
- Email: hr@dataco.com
- Contact: Jennifer Martinez (HR Business Partner)
- For: Benefits, PTO, policies, workplace concerns

**Finance & Expenses**
- Email: finance@dataco.com
- Tool: Expensify
- For: Travel reimbursement, software purchases, conference expenses

**Learning & Development**
- Contact: Sarah Chen (your manager)
- Budget: $2,000/year for courses, conferences, books
- Process: Discuss with manager, get approval, submit receipt

**Security Incidents**
- Email: security@dataco.com (urgent)
- Slack: #security-alerts
- For: Data breaches, suspicious activity, lost devices

---

## Tools & Systems

### Core Data Stack

**Snowflake** - Data Warehouse
- Access: Via Okta SSO (request through #data-requests)
- Login: https://dataco.snowflakecomputing.com
- Your Role: `JUNIOR_DS_ROLE` (read access to prod, write to dev)
- Documentation: Confluence > Data Team > Snowflake Guide

**Tableau** - Business Intelligence
- Access: Via Okta SSO
- Login: https://tableau.dataco.com
- Your Workspace: Personal folder created automatically
- Training: Tableau Fundamentals course (required in week 1)

**Jupyter Hub** - Data Science Notebooks
- Access: https://jupyter.dataco.com
- Environment: Python 3.10, R 4.2
- Compute: 16GB RAM, 4 CPUs (request more for large jobs)
- Storage: 50GB home directory

**GitHub Enterprise** - Version Control
- Access: https://github.dataco.com
- Your Team: @dataco/data-science
- Main Repos:
  - `ds-models` - Production ML models
  - `ds-notebooks` - Shared analysis notebooks
  - `ds-utils` - Common utilities and functions

**Slack** - Communication
- Required Channels:
  - #data-science - Team channel
  - #data-requests - Data access requests
  - #data-incidents - Production issues
  - #company-all - Company announcements
- Optional but Recommended:
  - #python - Python tips and troubleshooting
  - #sql-help - SQL questions
  - #random - Water cooler chat

**Jira** - Project Management
- Access: https://dataco.atlassian.net
- Board: Data Science Sprint Board
- Your Tickets: Assigned during sprint planning
- Workflow: To Do → In Progress → Code Review → Done

**Confluence** - Documentation
- Space: Data Team Knowledge Base
- Your Page: Create your personal page under "Team Members"
- Important Pages:
  - Data Dictionary
  - SQL Style Guide
  - Model Deployment Checklist
  - Incident Response Playbook

### Additional Tools

- **DBT (Data Build Tool)**: Data transformation (Priya's domain primarily)
- **Looker**: Ad-hoc SQL queries and quick charts
- **DataDog**: System monitoring and alerts
- **PagerDuty**: On-call rotation (you'll join after 3 months)
- **Zoom**: Video meetings (install desktop app)
- **1Password**: Password manager (company license)

---

## Common Workflows

### 1. Getting Data Access

**Step-by-Step Process:**

1. Identify what data you need
   - Check data dictionary first (Confluence)
   - Verify if data exists in Snowflake

2. Submit access request
   - Go to #data-requests Slack channel
   - Use the workflow: `/request-data-access`
   - Fill out form:
     - Database/Schema needed
     - Business justification
     - Duration of access (default: indefinite)

3. Wait for approval
   - Typical turnaround: 24-48 hours
   - Approver: Priya Patel or Sarah Chen
   - You'll get Slack notification when approved

4. Verify access
   - Login to Snowflake
   - Run: `SHOW GRANTS TO ROLE JUNIOR_DS_ROLE;`
   - Test query on the new table

**Pro Tips:**
- Request access to schemas, not individual tables
- Include specific use case in justification (helps approvers)
- For urgent requests, DM Priya directly (but use sparingly)

---

### 2. Running an A/B Test Analysis

**Standard Process:**

1. **Pre-Analysis Setup**
   - Get experiment ID from Product team (usually in JIRA ticket)
   - Confirm experiment design and success metrics
   - Check experiment ran long enough (minimum 7 days typically)

2. **Data Pull**
   - Use SQL template: `ds-notebooks/templates/ab_test_analysis.sql`
   - Replace placeholders:
     - `{experiment_id}`
     - `{start_date}`
     - `{end_date}`
   - Run in Snowflake or Jupyter notebook

3. **Statistical Analysis**
   - Use notebook template: `ds-notebooks/templates/ab_test_analysis.ipynb`
   - Calculate:
     - Sample sizes per variant
     - Conversion rates
     - Statistical significance (t-test or chi-square)
     - Confidence intervals
     - Effect size

4. **Document Findings**
   - Create Confluence page (use template: "A/B Test Results")
   - Include:
     - Experiment summary
     - Methodology
     - Results (tables + charts)
     - Recommendation (ship, iterate, or kill)
     - Next steps

5. **Present Results**
   - Share in #product-analytics Slack channel
   - Present in weekly Data Review meeting (Wednesdays 2pm)
   - Be ready to answer questions about statistical choices

**Common Pitfalls to Avoid:**
- Don't peek at results early (wait for full duration)
- Check for sample ratio mismatch
- Look for novelty effects
- Consider multiple testing correction if running many metrics

---

### 3. Deploying a Machine Learning Model

**Production Deployment Steps:**

1. **Development Phase**
   - Build model in Jupyter notebook
   - Track experiments in MLflow
   - Document model card (performance, limitations, training data)

2. **Code Review**
   - Move code to `ds-models` repo
   - Create pull request
   - Request review from Michael Torres
   - Address feedback and get approval

3. **Staging Deployment**
   - Engineering team creates API endpoint
   - You provide model artifacts and dependencies
   - Test in staging environment
   - Validate predictions match notebook results

4. **Production Deployment**
   - Submit deployment ticket in JIRA
   - Include: Model version, rollout plan, rollback procedure
   - Coordinate with Alex Johnson (Engineering Lead)
   - Monitor in DataDog for first 24 hours

5. **Post-Deployment**
   - Set up monitoring alerts
   - Schedule model refresh (retraining frequency)
   - Add to on-call runbook
   - Present in team demo (show & tell meeting)

**Required Approvals:**
- Code review: Michael Torres
- Production deployment: Sarah Chen + Alex Johnson

---

### 4. Creating a Dashboard

**Dashboard Development Process:**

1. **Scope Definition**
   - Meet with stakeholders (Product/Business team)
   - Define: Audience, key metrics, refresh frequency
   - Create mockup in Figma or PowerPoint first

2. **Data Preparation**
   - Write SQL queries in Snowflake
   - Create DBT models if complex transformations needed (work with Priya)
   - Test data quality and freshness

3. **Build in Tableau**
   - Create workbook in your personal folder first
   - Follow Tableau Style Guide (Confluence)
   - Use company color palette and fonts
   - Add filters and interactivity

4. **Review & Iterate**
   - Share draft with stakeholders
   - Incorporate feedback
   - Have Lisa Wang review for BI best practices

5. **Publish & Handoff**
   - Publish to appropriate Tableau folder
   - Set up refresh schedule
   - Document in Confluence (how to use, data sources, refresh timing)
   - Train stakeholders if needed

**Dashboard Checklist:**
- [ ] Clear title and description
- [ ] Last updated timestamp
- [ ] Filters are intuitive
- [ ] Mobile-friendly layout
- [ ] Performance optimized (<10 second load)
- [ ] Documentation exists

---

## Current Projects

### Active Team Projects

**Project Phoenix: Customer Churn Prediction Model**
- Lead: Michael Torres
- Your Role: Feature engineering support
- Status: In production, monthly retraining
- Goal: Predict 90-day churn risk for subscription customers
- Impact: $2M in prevented churn last quarter

**Project Nebula: Personalized Recommendation Engine**
- Lead: David Kim
- Your Role: You'll join this after onboarding
- Status: Prototype stage
- Goal: Recommend relevant products based on browsing history
- Target Launch: Q3 2025

**Project Atlas: Dashboard Migration**
- Lead: Lisa Wang (BI team)
- Your Role: Migrate 5 legacy reports to Tableau
- Status: 60% complete
- Deadline: End of Q2 2025
- Your Dashboards:
  - Weekly Active Users dashboard
  - Conversion funnel dashboard
  - Marketing campaign performance dashboard

### Upcoming Initiatives (Q3 2025)

- **Real-time Scoring API**: Low-latency prediction service
- **Automated Experiment Analysis**: Reduce manual analysis time
- **Customer 360 View**: Unified customer data dashboard

---

## Meeting Schedules

### Recurring Team Meetings

**Monday 10:00am - 10:30am: Team Standup**
- Format: Each person shares: What I did, What I'm doing, Blockers
- Location: Zoom (link in calendar invite)
- Optional to attend if OOO or in deep work

**Wednesday 2:00pm - 3:00pm: Data Review**
- Format: Present recent analyses, A/B test results, insights
- Attendees: Data team + Product team
- Prepare slides if presenting (use team template)

**Friday 3:00pm - 4:00pm: Show & Tell**
- Format: Demos of new models, tools, cool analyses
- Informal and fun
- Volunteer to present when you have something interesting

**Bi-weekly: Sprint Planning**
- Schedule: Every other Tuesday, 1:00pm - 2:00pm
- Format: Review backlog, assign tickets, estimate effort
- Bring questions about tickets

### 1:1 Meetings

**With Sarah Chen (Manager)**
- Frequency: Weekly, 30 minutes
- Format: Your agenda (career, feedback, priorities)
- Prep: Bring topics/questions in shared doc

**With Michael Torres (Mentor)**
- Frequency: Weekly, 45 minutes
- Format: Technical topics, code review, career advice
- Rotating agenda: pairing sessions, whiteboarding, learning new topics

---

## Learning Resources

### Required Training (Complete in First 2 Weeks)

1. **Security & Compliance Training**
   - Platform: Workday Learning
   - Duration: 2 hours
   - Topics: Data privacy, GDPR, security best practices

2. **Tableau Fundamentals**
   - Platform: Tableau Online Learning
   - Duration: 4 hours
   - Covers: Connecting data, building charts, dashboards

3. **SQL for Data Science**
   - Platform: Internal course (Confluence)
   - Duration: Self-paced (recommend 1 week)
   - Covers: Company SQL patterns, Snowflake specifics

### Recommended Resources

**Books (Company Library)**
- "Designing Data-Intensive Applications" - Martin Kleppmann
- "The Signal and the Noise" - Nate Silver
- "Python for Data Analysis" - Wes McKinney

**Online Courses (Udemy for Business)**
- Machine Learning A-Z
- Advanced SQL for Data Scientists
- Docker for Data Science

**Internal Resources**
- Slack: #data-science-learning (share articles, papers)
- Confluence: Data Team Book Club (monthly reads)
- Wiki: Best Practices Library

### Mentorship Program

- **Assigned Mentor**: Michael Torres
- **Format**: Weekly 1:1, pair programming, code reviews
- **Duration**: First 6 months, then optional
- **Goals**: Technical growth, navigation, knowledge transfer

---

## Frequently Asked Questions

### Getting Started

**Q: How do I set up my development environment?**
A: Follow the setup guide in Confluence > Data Team > Dev Environment Setup. It covers Python, R, Git, and necessary CLIs. If you get stuck, ask in #data-science.

**Q: Where can I find the data dictionary?**
A: Confluence > Data Team > Data Dictionary. It lists all tables, columns, definitions, and ownership. Keep it bookmarked!

**Q: What's the coding style guide?**
A: We follow PEP 8 for Python and the company SQL Style Guide (in Confluence). Use `black` for Python formatting and `sqlfluff` for SQL.

### Day-to-Day Work

**Q: How do I request PTO?**
A: Submit in BambooHR, notify Sarah Chen via Slack. For planned time off, give 2 weeks notice. For sick days, just let Sarah know ASAP.

**Q: Can I work remotely?**
A: Yes, we're hybrid. Required in-office: Tuesdays and Wednesdays. Other days are flexible. Update your Slack status to indicate location.

**Q: How do I expense something?**
A: Use Expensify app. Take photo of receipt, categorize, submit. Approval goes to Sarah. Reimbursement in next paycheck cycle.

**Q: What if I make a mistake that affects production?**
A: Don't panic! Immediately notify #data-incidents on Slack. Follow the incident runbook. We have a blameless culture - focus on fixing and learning.

### Technical Questions

**Q: How do I access production data?**
A: Request via #data-requests. You'll get read-only access. Never write to prod tables. Use your dev schema for testing.

**Q: Can I use external Python packages?**
A: Yes, but check with team first. If it's new, submit PR to add to `requirements.txt` and explain use case. Security team must approve.

**Q: How often should I commit code?**
A: Commit often (multiple times a day for active work). Push to GitHub daily. Create PR when feature/analysis is complete.

**Q: What compute resources are available for training large models?**
A: Jupyter default: 16GB RAM. For larger jobs, request GPU instance via #data-requests. We have shared cluster with A100 GPUs.

### Career & Growth

**Q: When will I get promoted?**
A: Promotions typically happen during mid-year and end-of-year reviews. Timeline: 18-24 months for DS I → DS II. Discuss career goals with Sarah in 1:1s.

**Q: Can I attend conferences?**
A: Yes! $2K/year budget. Popular ones: Strata, NeurIPS, PyData. Discuss with Sarah, submit CFP if speaking (company sponsors speakers).

**Q: How does on-call work?**
A: You'll join rotation after 3 months. 1 week shifts, with backup. Compensated with extra PTO. Runbooks exist for common issues.

**Q: Can I work on side projects?**
A: Yes, but must not conflict with company work or use company data. Fill out IP agreement form with legal if publishing externally.

---

## First Week Checklist

### Day 1: Monday
- [ ] Complete IT setup (laptop, accounts, badges)
- [ ] Attend team welcome meeting
- [ ] Set up Slack profile (photo, title, pronouns)
- [ ] Read this onboarding doc thoroughly
- [ ] Schedule coffee chats with team members

### Day 2: Tuesday
- [ ] Request access to Snowflake and Tableau
- [ ] Clone GitHub repos (`ds-models`, `ds-notebooks`, `ds-utils`)
- [ ] Complete security training
- [ ] Set up dev environment (Python, R, Docker)

### Day 3: Wednesday
- [ ] Attend Data Review meeting (just observe)
- [ ] Start Tableau Fundamentals course
- [ ] Explore data dictionary in Confluence
- [ ] Run sample SQL queries in Snowflake

### Day 4: Thursday
- [ ] Pair with Michael on current analysis
- [ ] Review team coding standards
- [ ] Practice PR process (make small docs contribution)
- [ ] Complete SQL training module 1

### Day 5: Friday
- [ ] Attend Show & Tell meeting
- [ ] Submit first question in team Q&A Slack channel
- [ ] Update your personal Confluence page
- [ ] Reflect on week in 1:1 with Sarah

---

## Contact Information Quick Reference

| Name | Role | Email | Slack |
|------|------|-------|-------|
| Sarah Chen | Manager | sarah.chen@dataco.com | @sarah.chen |
| Michael Torres | Mentor | michael.torres@dataco.com | @mtorres |
| Priya Patel | Analytics Engineer | priya.patel@dataco.com | @priya.p |
| David Kim | Peer DS | david.kim@dataco.com | @dkim |
| James Liu | Product Manager | james.liu@dataco.com | @jliu |
| Emma Rodriguez | Product Manager | emma.rodriguez@dataco.com | @erodriguez |
| Alex Johnson | Engineering Lead | alex.johnson@dataco.com | @alexj |
| Lisa Wang | BI Lead | lisa.wang@dataco.com | @lisawang |

---

## Important Links

- **Confluence**: https://dataco.atlassian.net/wiki
- **GitHub**: https://github.dataco.com
- **Snowflake**: https://dataco.snowflakecomputing.com
- **Tableau**: https://tableau.dataco.com
- **Jupyter**: https://jupyter.dataco.com
- **Jira**: https://dataco.atlassian.net
- **HR Portal**: https://hr.dataco.com
- **Expensify**: https://www.expensify.com

---

## Notes

- This guide is maintained by the Data Science team. Last updated: January 2025
- Found an error? Submit a PR to `ds-docs` repo or ping #data-science
- Feedback and suggestions welcome!

**Welcome aboard! We're excited to have you on the team!** 🚀
