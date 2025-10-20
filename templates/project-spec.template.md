# [Project Name]

> **Instructions**: Fill in all sections below. The more detail you provide, the better the feature breakdown will be. Delete this instruction block when done.

## Project Overview

### What We're Building
[Describe what you're building in 2-3 sentences]

### Why We're Building It
[Business problem or opportunity this solves]

### Who It's For
[Primary target audience]

---

## Business Objectives

What are the key business goals this project aims to achieve?

1. **Objective 1**: [e.g., Increase user engagement by 40%]
2. **Objective 2**: [e.g., Reduce manual processing time by 60%]
3. **Objective 3**: [e.g., Generate $X in revenue by Q4]

---

## Target Users

### User Persona 1: [Role Name]
- **Description**: [Who they are]
- **Needs**: [What they need from the system]
- **Goals**: [What they're trying to accomplish]
- **Pain Points**: [Current problems they face]

### User Persona 2: [Role Name]
- **Description**: [Who they are]
- **Needs**: [What they need from the system]
- **Goals**: [What they're trying to accomplish]
- **Pain Points**: [Current problems they face]

[Add more personas as needed]

---

## Features & Requirements

### Core Features (Must Have for MVP)

#### Feature Area 1: [e.g., User Management]
- **Registration**: Email/password signup with verification
- **Login**: Secure authentication with session management
- **Profile**: User can view and edit their profile
- **Password Reset**: Forgot password flow via email

#### Feature Area 2: [e.g., Content Management]
- **Browse**: View list of items with pagination
- **Search**: Full-text search across items
- **Filters**: Filter by category, date, status
- **Detail View**: See complete information for one item

#### Feature Area 3: [e.g., Transactions]
- **Create**: Add new items
- **Update**: Edit existing items
- **Delete**: Remove items with confirmation
- **Export**: Download data as CSV/Excel

[Add more feature areas as needed]

### Enhanced Features (Nice to Have)

- **Feature X**: [Description and why it's valuable]
- **Feature Y**: [Description and why it's valuable]
- **Feature Z**: [Description and why it's valuable]

### Future Considerations (Phase 2+)

- **Future Feature 1**: [Description]
- **Future Feature 2**: [Description]

---

## Technical Requirements

### Technology Stack

**Frontend**:
- Framework: [Next.js 14, React 18, Vue 3, Angular, etc.]
- UI Library: [Tailwind CSS, Material UI, shadcn/ui, etc.]
- State Management: [Redux, Zustand, React Query, etc.]

**Backend**:
- Runtime: [Node.js, Python, Ruby, etc.]
- Framework: [Express, FastAPI, Rails, etc.]
- Database: [PostgreSQL, MongoDB, MySQL, etc.]
- ORM: [Prisma, TypeORM, SQLAlchemy, etc.]

**Infrastructure**:
- Hosting: [Vercel, AWS, Google Cloud, etc.]
- Storage: [S3, Cloudinary, etc.]
- CDN: [Cloudflare, Fastly, etc.]

### Integration Requirements

- **Payment**: [Stripe, PayPal, Square, etc.]
- **Email**: [SendGrid, Mailgun, AWS SES, etc.]
- **Auth**: [NextAuth, Auth0, Firebase Auth, etc.]
- **Analytics**: [Google Analytics, Mixpanel, etc.]
- **Other APIs**: [List any third-party APIs needed]

### Performance Requirements

- **Page Load Time**: [e.g., < 2 seconds]
- **API Response Time**: [e.g., < 500ms]
- **Concurrent Users**: [e.g., 10,000+]
- **Uptime**: [e.g., 99.9%]
- **Mobile Support**: [Yes/No, specific requirements]

### Security Requirements

- **Authentication**: [Requirements]
- **Data Encryption**: [In transit and at rest]
- **Compliance**: [GDPR, HIPAA, SOC2, etc.]
- **Audit Logging**: [What needs to be logged]

---

## Success Criteria

### Quantitative Metrics
- [ ] Metric 1: [e.g., 5,000 registered users in first month]
- [ ] Metric 2: [e.g., 95% customer satisfaction score]
- [ ] Metric 3: [e.g., < 1% error rate]

### Qualitative Metrics
- [ ] User feedback: [Target rating or feedback]
- [ ] Stakeholder approval: [Criteria for success]
- [ ] Market validation: [How success is measured]

---

## Constraints & Assumptions

### Timeline Constraints
- **Total Duration**: [e.g., 3 months]
- **Launch Date**: [Target date]
- **Key Milestones**: 
  - Milestone 1: [Date and deliverable]
  - Milestone 2: [Date and deliverable]

### Budget Constraints
- **Development Budget**: [$X]
- **Infrastructure Budget**: [$X/month]
- **Third-party Services**: [$X/month]

### Team Constraints
- **Team Size**: [e.g., 2 developers, 1 designer]
- **Skills Available**: [List key skills on team]
- **Skills Needed**: [Any gaps that need filling]

### Technical Constraints
- **Must integrate with**: [Existing systems]
- **Must support**: [Browsers, devices, etc.]
- **Cannot use**: [Restricted technologies]

### Business Constraints
- **Regulatory**: [Compliance requirements]
- **Legal**: [Terms, privacy, etc.]
- **Operational**: [Support hours, SLAs, etc.]

---

## Assumptions

1. [Assumption 1 - e.g., "Users have modern browsers (Chrome, Firefox, Safari)"]
2. [Assumption 2 - e.g., "Payment processing handled by third-party (Stripe)"]
3. [Assumption 3 - e.g., "User data stored in US/EU regions only"]

---

## Out of Scope

Explicitly list what is NOT included in this project:

- [Feature X that won't be included]
- [Integration Y that's deferred to Phase 2]
- [Requirement Z that's explicitly excluded]

---

## Questions & Risks

### Open Questions
1. [Question 1 that needs answering]
2. [Question 2 that needs answering]

### Known Risks
1. **Risk**: [Description]  
   **Mitigation**: [How to address]

2. **Risk**: [Description]  
   **Mitigation**: [How to address]

---

## Approval & Sign-off

- **Project Owner**: [Name]
- **Technical Lead**: [Name]
- **Approved Date**: [Date]

---

## Ready for Breakdown?

Once this spec is complete, run:

```bash
/speckit.breakdown docs/PROJECT_SPEC.md
```

This will generate:
- Master breakdown document
- Individual feature files
- Implementation roadmap
- Quick-start commands
